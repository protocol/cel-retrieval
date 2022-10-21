import os
import sys
import numpy as np
from typing import List


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))
sys.path.append(MODULE_DIR)

from treasury_sim.operator_v2 import OperatorV2
from treasury_sim.sim import *


def run_single_sim(
    sim_len: int,
    k1: float,
    k2: float,
    penalty_multiplier: float,
    day_pool_list: List[float],
    initial_ops_num: int,
    new_ops_num: int,
    is_growth_pool: bool = False,
    total_pool: float = None,
) -> List[OperatorV2]:
    ops_list = generate_ops_v2(initial_ops_num)
    for sim_step in range(sim_len):
        # Update perf. metrics and log detection flags
        update_ops_bandwidth(ops_list)
        update_ops_flags(ops_list)
        # Get daily reward from initial pool
        if is_growth_pool:
            day_pool: float = compute_growth_day_pool_v2(
                sim_step, sim_len, total_pool, ops_list
            )
        elif sim_step < len(day_pool_list):
            day_pool: float = day_pool_list[sim_step]
        else:
            day_pool: float = 0.0
        # Compute rewards (before penalties)
        update_ops_rewards(ops_list, day_pool, k1, k2, penalty_multiplier)
        # Compute final payout (after penalties)
        update_ops_payouts(ops_list)
        # Add new ops to list (if we are not in the last iteration)
        if sim_step < sim_len - 1:
            new_ops = generate_ops_v2(new_ops_num)
            ops_list += new_ops
    return ops_list


def compute_growth_day_pool_v2(
    sim_step: int, sim_len: int, total_pool: float, ops_list: List[OperatorV2]
):
    # Get current cummulive rewards
    curr_bw_arr = np.array([op.get_total_bandwidth() for op in ops_list])
    curr_cum_rewards_achieved = compute_cum_rewards_v2(
        sim_step, sim_len, total_pool, curr_bw_arr
    )
    # Get previous cummulive rewards
    day_bw_arr = np.array([op.bandwidth_list[-1] for op in ops_list])
    prev_bw_list = curr_bw_arr - day_bw_arr
    prev_cum_rewards_achieved = compute_cum_rewards_v2(
        sim_step - 1, sim_len, total_pool, prev_bw_list
    )
    # Set day pool
    day_pool = curr_cum_rewards_achieved - prev_cum_rewards_achieved

    return day_pool


def compute_cum_rewards_v2(
    sim_step: int, sim_len: int, total_pool: float, bw_arr: np.array
):
    # Get goal bandwidth variables
    goal_committed_bw = get_goal_bandwidth_v2(sim_step)
    total_bandwidth_goal = get_goal_bandwidth_v2(sim_len)
    # Get commited bandwidth variables
    total_committed_bw = sum(bw_arr)
    # Get reward varibles
    committed_bw_ratio = (
        min(goal_committed_bw, total_committed_bw) / total_bandwidth_goal
    )
    cum_rewards = total_pool * committed_bw_ratio
    return cum_rewards


def get_goal_bandwidth_v2(sim_step: int):
    """
    The bandwidth goal is computed with the following assumptions:
        1. At the end of 12 months (360 days), we aim to serve 300TB/day
        2. We start with 0 TB/day at launch
        3. We assume a linear growth in the daily bandwidth served
    """
    if sim_step < 0:
        total_goal_bw = 0.0
    else:
        daily_goal_list = [(i + 1) * 300.0 / 360.0 for i in range(sim_step)]
        total_goal_bw = sum(daily_goal_list)
    return total_goal_bw


def generate_ops_v2(num_ops: int) -> List[OperatorV2]:
    op_types = ["honest_high_l1", "honest_normal_l1", "honest_low_l1", "cheating_l1"]
    op_types_probs = [0.1, 0.75, 0.1, 0.05]
    ops_list = []
    for i in range(num_ops):
        op_type = np.random.choice(op_types, p=op_types_probs)
        new_op = OperatorV2(op_type)
        ops_list.append(new_op)
    return ops_list
