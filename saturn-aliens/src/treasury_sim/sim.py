import os
import sys
import numpy as np
from typing import List


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))
sys.path.append(MODULE_DIR)

from treasury_sim.operator import Operator


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
) -> List[Operator]:
    ops_list = generate_ops(initial_ops_num)
    for sim_step in range(sim_len):
        # Update perf. metrics and log detection flags
        update_ops_bandwidth(ops_list)
        update_ops_flags(ops_list)
        # Get daily reward from initial pool
        if is_growth_pool:
            day_pool: float = compute_growth_day_pool(
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
            new_ops = generate_ops(new_ops_num)
            ops_list += new_ops
    return ops_list


def compute_growth_day_pool(
    sim_step: int, sim_len: int, total_pool: float, ops_list: List[Operator]
):
    # Get current cummulive rewards
    curr_bw_arr = np.array([op.get_total_bandwidth() for op in ops_list])
    curr_cum_rewards_achieved = compute_cum_rewards(
        sim_step, sim_len, total_pool, curr_bw_arr
    )
    # Get previous cummulive rewards
    day_bw_arr = np.array([op.bandwidth_list[-1] for op in ops_list])
    prev_bw_list = curr_bw_arr - day_bw_arr
    prev_cum_rewards_achieved = compute_cum_rewards(
        sim_step - 1, sim_len, total_pool, prev_bw_list
    )
    # Set day pool
    day_pool = curr_cum_rewards_achieved - prev_cum_rewards_achieved

    return day_pool


def compute_cum_rewards(
    sim_step: int, sim_len: int, total_pool: float, bw_arr: np.array
):
    # Get goal bandwidth variables
    goal_committed_bw = get_goal_bandwidth(sim_step)
    total_bandwidth_goal = get_goal_bandwidth(sim_len)
    # Get commited bandwidth variables
    total_committed_bw = sum(bw_arr)
    # Get reward varibles
    committed_bw_ratio = (
        min(goal_committed_bw, total_committed_bw) / total_bandwidth_goal
    )
    cum_rewards = total_pool * committed_bw_ratio
    return cum_rewards


def get_goal_bandwidth(sim_step: int):
    """
    The bandwidth goal is computed with the following assumptions:
        1. Each operator contributes on average 1 TB per day
        2. We start with 50 operators
        3. Five operators enter the network every day
    """
    if sim_step < 0:
        goal_bw = 0.0
    elif sim_step == 0:
        goal_bw = 50.0
    else:
        goal_bw = (sim_step * 50.0) + (2.5 * sim_step * (sim_step + 1))
    return goal_bw


def generate_ops(num_ops: int) -> List[Operator]:
    op_types = ["honest_high_l1", "honest_normal_l1", "honest_low_l1", "cheating_l1"]
    op_types_probs = [0.1, 0.75, 0.1, 0.05]
    ops_list = []
    for i in range(num_ops):
        op_type = np.random.choice(op_types, p=op_types_probs)
        new_op = Operator(op_type)
        ops_list.append(new_op)
    return ops_list


def update_ops_bandwidth(ops_list: List[Operator]) -> None:
    for op in ops_list:
        op.generate_bandwidth()


def update_ops_rewards(
    ops_list: List[Operator],
    day_pool: float,
    k1: float,
    k2: float,
    penalty_multiplier: float,
) -> None:
    op_bw_arr = np.array([op.bandwidth_list[-1] for op in ops_list])
    op_speed_arr = np.array([op.speed_ratio for op in ops_list])
    op_uptime_arr = np.array([op.uptime for op in ops_list])
    reward_num = op_bw_arr**k1 * op_speed_arr**k2 * op_uptime_arr**k2
    op_reward_arr = day_pool * reward_num / sum(reward_num)
    for i, op in enumerate(ops_list):
        op.add_reward(op_reward_arr[i], penalty_multiplier)


def update_ops_flags(ops_list: List[Operator]) -> None:
    for op in ops_list:
        op.generate_flag()


def update_ops_payouts(ops_list: List[Operator]) -> None:
    for op in ops_list:
        op.compute_payout()
