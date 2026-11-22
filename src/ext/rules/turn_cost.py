"""转弯代价（E1）：每走一格代价 1，每转 90° 额外代价 λ（掉头算两次 90°）。

规则代价 = 步数 + λ × 90° 转向次数（与环境统计的 steps、turns_90 口径一致）。
λ = 0 时退化为基础规则的代价；λ 可由运动时间模型换算（motion_time.MotionTimeLayer.equivalent_weight）。
"""

from dataclasses import dataclass

from core.rules import CostLayer


@dataclass(frozen=True)
class TurnCostLayer(CostLayer):
    """代价 = 步数 + λ × 90° 转向。"""
    key = "turn_cost"
    title = "转弯代价"
    color = "#d9480f"
    summary = "每走一格代价 1，每转 90° 再加 λ；路线越直越便宜"
    formula = "代价 = 步数 + λ × 90°转向"
    param_labels = {"weight": ("λ", "")}

    weight: float = 1.0

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError("turn weight λ must be non-negative")

    def run_cost(self, cells: int) -> float:
        return float(cells)

    def turn_cost(self, quarters: int) -> float:
        return self.weight * quarters


LAYERS = [TurnCostLayer]
