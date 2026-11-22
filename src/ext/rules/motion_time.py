"""运动时间模型（E1 控制层）：规则代价为预计用时（秒），采用“走—停—转”假设。

直线段：从静止加速、到段末减速到静止，梯形速度曲线（达不到最高速时为三角形）：
    段长 d = 格数 × 格子边长；加速到最高速所需距离 d* = v² / a（加速 + 减速各一半）；
    d ≥ d* 时 t = d / v + v / a；否则 t = 2 √(d / a)。
原地转向：转 90° 用 turn90 秒，掉头用 turn180 秒。

参数来源：格子边长 0.18 m 来自电脑鼠比赛迷宫规格（16×16 格，每格 18 cm）；最高速、加速度与转向时间
是本组为“探索阶段”设定的保守假设值（低于竞速冲刺），文献与实测校准待核查，可通过参数调整
（如 --rule motion_time:v_max=1.0,accel=3）。这些值只影响按时间的排名，不影响环境的移动与观测。
"""

import math
from dataclasses import dataclass

from core.rules import CostLayer


@dataclass(frozen=True)
class MotionTimeLayer(CostLayer):
    """代价 = 预计用时（秒）：梯形加减速的直线段 + 固定的原地转向时间。"""
    key = "motion_time"
    title = "运动时间模型"
    color = "#1971c2"
    summary = "按真实电脑鼠的加减速与转向耗时估算用时；长直道更快，转弯要停车"
    formula = "代价 = Σ 直线段用时（梯形加减速）+ Σ 转向用时"
    unit = "s"
    param_labels = {"cell": ("格长", " m"), "v_max": ("最高速", " m/s"), "accel": ("加速度", " m/s²"),
                    "turn90": ("转 90°", " s"), "turn180": ("掉头", " s")}
    label_params = ("v_max", "turn90")

    cell: float = 0.18
    v_max: float = 0.5
    accel: float = 2.0
    turn90: float = 0.3
    turn180: float = 0.5

    def __post_init__(self):
        if min(self.cell, self.v_max, self.accel) <= 0 or min(self.turn90, self.turn180) < 0:
            raise ValueError("motion parameters must be positive")

    def run_cost(self, cells: int) -> float:
        distance = cells * self.cell
        if distance >= self.v_max ** 2 / self.accel:
            return distance / self.v_max + self.v_max / self.accel
        return 2 * math.sqrt(distance / self.accel)

    def turn_cost(self, quarters: int) -> float:
        return self.turn90 if quarters == 1 else self.turn180

    def equivalent_weight(self) -> float:
        """换算成转弯代价的 λ：转 90° 的时间相当于走多少格（以单格直线段用时为 1 格）。"""
        return self.turn90 / self.run_cost(1)


LAYERS = [MotionTimeLayer]
