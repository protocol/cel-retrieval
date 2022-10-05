import numpy as np
from typing import List, Tuple


class Operator:
    def __init__(self, op_type: str) -> None:
        self.op_type: str = op_type
        self.set_performance()
        self.set_detection_prob()
        self.payout_list: List[float] = []
        self.reward_list: List[float] = []  # rewards before penalties
        self.bandwidth_list: List[float] = []
        self.flag_list: List[bool] = []
        self.collateral_balance: float = 0.0
        self.penalty: float = None
        self.penalty_list: List[float] = []

    def set_performance(self) -> None:
        if self.op_type == "honest_high_l1":
            self.mu_bandwidth: float = 100.0
            self.sigma_bandwidth: float = 1.0
            self.uptime: float = 1.0
            self.speed_ratio: float = 1.0
        elif self.op_type in ["honest_normal_l1", "cheating_l1"]:
            self.mu_bandwidth: float = 80.0
            self.sigma_bandwidth: float = 1.0
            self.uptime: float = 1.0
            self.speed_ratio: float = 0.9
        elif self.op_type == "honest_low_l1":
            self.mu_bandwidth: float = 50.0
            self.sigma_bandwidth: float = 1.0
            self.uptime: float = 0.9
            self.speed_ratio: float = 0.5
        else:
            raise ValueError("Invalid op_type")

    def set_detection_prob(self) -> None:
        honest_ops = ["honest_high_l1", "honest_normal_l1", "honest_low_l1"]
        cheating_ops = ["cheating_l1"]
        if self.op_type in honest_ops:
            self.detection_prob: float = 0.02
        elif self.op_type in cheating_ops:
            self.detection_prob: float = 0.25
        else:
            raise ValueError("Invalid op_type")

    def generate_bandwidth(self) -> None:
        bw: float = np.random.normal(self.mu_bandwidth, self.sigma_bandwidth)
        self.bandwidth_list.append(bw)

    def generate_flag(self) -> None:
        flag: bool = np.random.choice(
            [True, False], p=[self.detection_prob, 1 - self.detection_prob]
        )
        self.flag_list.append(flag)

    def add_reward(self, reward: float, penalty_multiplier: float) -> None:
        self.reward_list.append(reward)
        self.penalty = penalty_multiplier * np.mean(self.reward_list)

    def compute_current_payout(self) -> None:
        is_flagged: bool = self.flag_list[-1]
        curr_reward: float = self.reward_list[-1]
        # Apply penalty in case of detection
        if is_flagged:
            self.collateral_balance -= self.penalty
            self.penalty_list.append(self.penalty)
        # Update saved collateral and compute payout
        if self.collateral_balance < self.penalty:
            missing_collateral = self.penalty - self.collateral_balance
            payout: float = max(0.0, curr_reward - missing_collateral)
            self.collateral_balance += curr_reward - payout
        else:
            payout: float = curr_reward
        # Update payout list
        self.payout_list.append(payout)
