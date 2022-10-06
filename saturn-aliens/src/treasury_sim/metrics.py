import os
import sys
import numpy as np
import pandas as pd
from typing import List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))
sys.path.append(MODULE_DIR)

from treasury_sim.operator import Operator


def compute_op_metrics(op_list: List[Operator]) -> pd.DataFrame:
    op_dict = {
        "op_type": [op.op_type for op in op_list],
        "num_payouts": [op.get_payout_count() for op in op_list],
        "missed_payouts": [op.count_missed_payouts() for op in op_list],
        "total_payout": [op.get_total_payout() for op in op_list],
        "avg_payout": [op.get_avg_payout() for op in op_list],
        "median_payout": [op.get_median_payout() for op in op_list],
        "total_penalty": [op.get_total_penalty() for op in op_list],
        "num_penalties": [op.get_flag_count() for op in op_list],
        "avg_penalty": [op.get_avg_penalty() for op in op_list],
        "max_no_penalty_period": [
            op.get_max_consecutive_no_penalty() for op in op_list
        ],
        "collateral_balance": [op.collateral_balance for op in op_list],
        "total_bandwidth": [op.get_total_bandwidth for op in op_list],
    }
    op_df = pd.DataFrame(op_dict)
    return op_df


def compute_sim_metrics(op_list: List[Operator], **attrs) -> pd.DataFrame:
    sim_df = compute_op_metrics(op_list)
    for param, value in attrs.items():
        sim_df[param] = value
    return sim_df


def compute_ops_trajectory(
    op_list: List[Operator], sim_len: int, **attrs
) -> pd.DataFrame:
    # Init dataframe
    traj_df: pd.DataFrame = pd.DataFrame(
        columns=[
            "sim_step",
            "op_type",
            "payout",
            "flag",
            "penalty",
        ]
    )
    for op in op_list:
        num_steps = len(op.payout_list)
        op_df = pd.DataFrame(
            {
                "sim_step": np.arange(sim_len - num_steps, sim_len),
                "op_type": [op.op_type] * num_steps,
                "payout": op.payout_list,
                "flag": op.flag_list,
                "penalty": op.penalty_list,
                "bandwidth": op.bandwidth_list,
            }
        )
        traj_df = pd.concat([traj_df, op_df], ignore_index=True)
    for param, value in attrs.items():
        traj_df[param] = value
    return traj_df
