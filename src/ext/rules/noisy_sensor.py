"""噪声观测层（E2，observation 维度）：每次观测中，每面内部墙的读数以一定概率出错。

传感器模型（独立同分布，按相对朝向区分准确率）：
    - 当前格的每个方向独立读数；前方、左右、后方的准确率分别为 p_front、p_side、p_back；
      读数出错时“有墙”读成“没墙”（漏报）或“没墙”读成“有墙”（误报），两者概率相同；
    - 地图外圈边界总是读对（电脑鼠知道地图尺寸）；
    - 撞墙的接触反馈总是可靠：撞墙后的观测一定包含撞到的方向（见 collision.py）。
默认参数（0.95 / 0.90 / 0.85）是待校准的仿真假设：前方红外传感器最准、侧向次之、后方最差，
与常见电脑鼠“前方两个、斜向两个”传感器布局的定性规律一致，具体数值没有实测来源。

噪声使传感器漏报墙时电脑鼠会撞墙，因此本层默认允许撞墙后继续（collision_limit = 不限），
叠加撞墙处理层可另设上限：noisy_sensor+collision:limit=5。
随机性：噪声由运行种子与地图 id 决定（同一种子、同一地图结果完全相同）；多种子重复后报告均值与离散程度。
本层改变观测，只对声明 supported_rules 包含 "noisy_sensor" 的探索算法开放（已知地图规划器不受影响）。
写法：noisy_sensor、noisy_sensor:p_front=0.9,p_side=0.8,p_back=0.7。
"""

import math
import random
from dataclasses import dataclass, replace
from typing import ClassVar

from core.environment import ContactObservation, Direction
from core.planning import quarter_turns, step
from core.rules import RuleLayer


@dataclass(frozen=True)
class NoisySensorLayer(RuleLayer):
    """墙读数按前 / 侧 / 后准确率随机出错；接触反馈可靠。"""

    key: ClassVar[str] = "noisy_sensor"
    title: ClassVar[str] = "噪声观测"
    dimension: ClassVar[str] = "observation"
    color: ClassVar[str] = "#7048e8"
    summary: ClassVar[str] = "每面内部墙的读数按方向准确率随机出错（漏报或误报）；撞墙反馈可靠"
    changes_observation: ClassVar[bool] = True
    param_labels: ClassVar[dict[str, tuple[str, str]]] = {
        "p_front": ("前", ""), "p_side": ("侧", ""), "p_back": ("后", "")}   # 准确率：前方 / 侧向 / 后方
    param_ranges: ClassVar[dict[str, tuple[float, float]]] = {
        "p_front": (0.51, 1.0), "p_side": (0.51, 1.0), "p_back": (0.51, 1.0)}

    p_front: float = 0.95
    p_side: float = 0.90
    p_back: float = 0.85

    def __post_init__(self):
        for name in ("p_front", "p_side", "p_back"):
            if not 0.5 < getattr(self, name) <= 1.0:
                raise ValueError(f"{name} must be in (0.5, 1]")

    def accuracy(self, heading: Direction, direction: Direction) -> float:
        """朝 heading 时，direction 方向读数正确的概率。"""
        return (self.p_front, self.p_side, self.p_back)[quarter_turns(heading, direction)]

    def evidence_weight(self, heading: Direction, direction: Direction) -> float:
        """一次读数的对数几率权重 w = ln(p / (1 − p))；p = 1 时为 inf（读数确定）。"""
        p = self.accuracy(heading, direction)
        return math.inf if p >= 1.0 else math.log(p / (1.0 - p))

    def env_options(self) -> dict:
        return {"collision_limit": None}   # 漏报必然导致撞墙：默认撞墙后继续

    def wrap_env(self, env):
        return NoisySensorEnv(env, self)


class NoisySensorEnv:
    """包装 MazeEnvironment：reset / step 返回的观测加噪声，其余属性原样转发。"""

    def __init__(self, base, layer: NoisySensorLayer):
        self._base = base
        self._layer = layer
        self._rng = random.Random()

    def __getattr__(self, name):
        return getattr(self._base, name)

    def reset(self):
        self._rng = random.Random(f"noisy_sensor:{self._base.seed}:{self._base.maze_id}")
        return self._noisy(self._base.reset())

    def step(self, direction):
        result = self._base.step(direction)
        return replace(result, observation=self._noisy(result.observation))

    def _noisy(self, observation):
        walls = set()
        for direction in Direction:
            truth = direction in observation.walls
            nx, ny = step(observation.position, direction)
            if not (0 <= nx < self._base.width and 0 <= ny < self._base.height):
                reading = truth                              # 边界总是读对
            elif self._rng.random() < self._layer.accuracy(observation.heading, direction):
                reading = truth
            else:
                reading = not truth
            if reading:
                walls.add(direction)
        if isinstance(observation, ContactObservation):
            walls.add(observation.collision_wall)            # 接触反馈可靠
        return replace(observation, walls=frozenset(walls))


LAYERS = [NoisySensorLayer]
