"""撞墙处理层（contact 维度）：撞墙后不立即判负，原地转向后继续；可设累计撞墙上限。

基础规则：首次撞墙即 invalid_action（理想观测下只有写错的算法才会撞墙）。
噪声观测（noisy_sensor）下传感器会漏报墙，撞墙成为正常事件，因此需要本层：
    - 撞墙：电脑鼠原地转向撞墙方向、不移动；步数、路径、访问次数不变，转向照常计数；
      结束当前直线段（代价层按“停下再起步”计价）；
    - 接触反馈可靠：撞墙后的观测是 ContactObservation，collision_wall 标出撞到的方向，
      且 walls 一定包含该方向（优先于噪声传感器读数）；
    - 每次撞墙也消耗一次动作预算（max_steps 计的是动作数）；
    - 累计撞墙达到 limit 次时终止，状态 collision_limit；limit = inf（默认）为不限次数。
      同时触发时优先报告 collision_limit。
写法：collision（不限次数）、collision:limit=3；可与代价层、观测层组合，
如 turn_cost:weight=2+noisy_sensor+collision:limit=5。
运行结果与 runs.csv 另含 actions（动作数）与 collisions（撞墙次数）。
"""

import math
from dataclasses import dataclass
from typing import ClassVar

from core.rules import RuleLayer


@dataclass(frozen=True)
class CollisionLayer(RuleLayer):
    """撞墙后原地转向继续，累计撞墙 limit 次终止（inf 为不限）。"""

    key: ClassVar[str] = "collision"
    title: ClassVar[str] = "撞墙后继续"
    dimension: ClassVar[str] = "contact"
    color: ClassVar[str] = "#c2255c"
    summary: ClassVar[str] = "撞墙不判负：原地转向、不移动，接触反馈可靠；累计撞墙达到上限才终止"
    param_labels: ClassVar[dict[str, tuple[str, str]]] = {"limit": ("撞墙上限", " 次")}
    param_ranges: ClassVar[dict[str, tuple[float, float]]] = {"limit": (1, 999)}

    limit: float = math.inf

    def __post_init__(self):
        if self.limit != math.inf and (self.limit < 2 or self.limit != int(self.limit)):
            raise ValueError("collision limit must be an integer ≥ 2 or unlimited "
                             "(limit = 1 is the basic rule: omit the layer)")

    def label(self) -> str:
        return "撞墙后继续" if self.limit == math.inf else f"撞墙后继续（{int(self.limit)} 次终止）"

    def env_options(self) -> dict:
        return {"collision_limit": None if self.limit == math.inf else int(self.limit)}


LAYERS = [CollisionLayer]
