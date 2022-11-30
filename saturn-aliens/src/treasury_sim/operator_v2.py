import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))
sys.path.append(MODULE_DIR)

from treasury_sim.operator import Operator


class OperatorV2(Operator):
    def set_performance(self) -> None:
        # Ansgar estimates a bandwidth of 45TB/mo/node
        if self.op_type in ["honest_high_l1", "cheating_l1"]:
            self.mu_bandwidth: float = 1.2
            self.sigma_bandwidth: float = 0.05
            self.uptime: float = 1.0
            self.speed_ratio: float = 1.0
        elif self.op_type == "honest_normal_l1":
            self.mu_bandwidth: float = 0.9
            self.sigma_bandwidth: float = 0.05
            self.uptime: float = 1.0
            self.speed_ratio: float = 0.9
        elif self.op_type == "honest_low_l1":
            self.mu_bandwidth: float = 0.6
            self.sigma_bandwidth: float = 0.05
            self.uptime: float = 0.9
            self.speed_ratio: float = 0.5
        else:
            raise ValueError("Invalid op_type")
