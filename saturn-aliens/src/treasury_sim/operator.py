import numpy as np
from typing import List, Tuple


class Operator:
    def __init__(self, op_type: str) -> None:
        self.op_type: str = op_type
        self.set_performance()
        self.set_detection_prob()
        self.payout_list: List[float] = []
        self.reward_list: List[float] = []  # rewards before penalties
        self.bandwidth_list: List[float] = []  # bandwidth in TBs per day
        self.flag_list: List[bool] = []
        self.collateral_balance: float = 0.0
        self.penalty: float = None
        self.penalty_list: List[float] = []

    def set_performance(self) -> None:
        if self.op_type in ["honest_high_l1", "cheating_l1"]:
            self.mu_bandwidth: float = 1.2
            self.sigma_bandwidth: float = 0.1
            self.uptime: float = 1.0
            self.speed_ratio: float = 1.0
        elif self.op_type == "honest_normal_l1":
            self.mu_bandwidth: float = 0.9
            self.sigma_bandwidth: float = 0.1
            self.uptime: float = 1.0
            self.speed_ratio: float = 0.9
        elif self.op_type == "honest_low_l1":
            self.mu_bandwidth: float = 0.6
            self.sigma_bandwidth: float = 0.1
            self.uptime: float = 0.9
            self.speed_ratio: float = 0.5
        else:
            raise ValueError("Invalid op_type")

    def set_detection_prob(self) -> None:
        honest_ops = ["honest_high_l1", "honest_normal_l1", "honest_low_l1"]
        cheating_ops = ["cheating_l1"]
        if self.op_type in honest_ops:
            self.detection_prob: float = 0.01
        elif self.op_type in cheating_ops:
            self.detection_prob: float = 0.25
        else:
            raise ValueError("Invalid op_type")

    def generate_bandwidth(self) -> None:
        bw: float = max(0.0, np.random.normal(self.mu_bandwidth, self.sigma_bandwidth))
        self.bandwidth_list.append(bw)

    def generate_flag(self) -> None:
        flag: bool = np.random.choice(
            [True, False], p=[self.detection_prob, 1 - self.detection_prob]
        )
        self.flag_list.append(flag)

    def add_reward(self, reward: float, penalty_multiplier: float) -> None:
        self.reward_list.append(reward)
        self.penalty = penalty_multiplier * np.mean(self.reward_list)

    def compute_payout(self) -> None:
        is_flagged: bool = self.flag_list[-1]
        curr_reward: float = self.reward_list[-1]
        # Apply penalty in case of detection
        if is_flagged:
            self.collateral_balance -= self.penalty
            self.penalty_list.append(self.penalty)
        else:
            self.penalty_list.append(0.0)
        # Update saved collateral and compute payout
        if self.collateral_balance < self.penalty:
            missing_collateral = self.penalty - self.collateral_balance
            payout: float = max(0.0, curr_reward - missing_collateral)
            self.collateral_balance += curr_reward - payout
        else:
            payout: float = curr_reward
        # Update payout list
        self.payout_list.append(payout)

    def get_payout_count(self) -> float:
        non_zero_payouts = [p for p in self.payout_list if p > 0]
        return len(non_zero_payouts)

    def count_missed_payouts(self) -> int:
        zero_payouts = [p for p in self.payout_list if p == 0.0]
        return len(zero_payouts)

    def get_total_payout(self) -> float:
        return sum(self.payout_list)

    def get_avg_payout(self) -> float:
        non_zero_payouts = [p for p in self.payout_list if p > 0]
        if len(non_zero_payouts) == 0:
            return 0.0
        else:
            return np.mean(non_zero_payouts)

    def get_median_payout(self) -> float:
        if len(self.payout_list) == 0:
            return 0.0
        else:
            return np.median(self.payout_list)

    def get_total_penalty(self) -> float:
        return sum(self.penalty_list)

    def get_flag_count(self) -> int:
        return sum(self.flag_list)

    def get_avg_penalty(self) -> float:
        non_zero_penalties = [p for p in self.penalty_list if p > 0]
        if len(non_zero_penalties) == 0:
            return 0.0
        else:
            return np.mean(non_zero_penalties)

    def get_max_consecutive_no_penalty(self) -> int:
        max_no_p_count = 0
        curr_no_p_count = 0
        for flag in self.flag_list:
            if flag == False:
                curr_no_p_count += 1
            else:
                if curr_no_p_count > max_no_p_count:
                    max_no_p_count = curr_no_p_count
                curr_no_p_count = 0
        if curr_no_p_count > max_no_p_count:
            max_no_p_count = curr_no_p_count
        return max_no_p_count

    def get_total_bandwidth(self) -> float:
        return sum(self.bandwidth_list)
