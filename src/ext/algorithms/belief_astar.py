"""置信度重规划（E2）：用对数几率融合多次噪声读数判断墙，在乐观地图上按规则代价重规划。

思路：噪声观测下一次读数不可信，但同一面墙会被反复看到（从两侧、不同朝向）。每面墙维护
对数几率分数 S（S > 0 表示“更可能有墙”）：
    - 读到“有墙”加 w，读到“没墙”减 w，w = ln(p / (1 − p))，p 为该方向传感器准确率
      （由噪声观测层给出；越准的方向权重越大）；P(有墙) = 1 / (1 + e^(−S))；
    - 确定证据：撞到的墙 S = +∞；实际走过的边 S = −∞；之后的读数不再改变它们；
    - 没有读数的边 S = 0，按乐观假设视为可走。
理想观测（没有噪声层）时每次读数都确定（w = ∞），算法退化为朝向 A* 的重复规划。
信息假设：只用每步观测（含撞墙反馈）和噪声层公开的传感器准确率；不读真值地图。
决策规则：
    1. 用当前观测更新分数（走过的边、撞到的墙记为确定）；
    2. 没有计划，或剩余计划穿过一面“更可能有墙”（S > 0）的边时重新规划：
       在“S > 0 视为墙”的地图上按当前规则代价做 A*（heading_search + cost_lower_bound）；
    3. 找不到路时只把确定的墙（S = +∞）当墙再规划一次（误报可能把路堵死）；仍找不到返回 None。
消融变体 belief_astar_naive：只相信最近一次读数（不累积证据），其余相同。
改进变体 belief_astar_soft（冻结计划之后新增，见报告发现 11）：第 3 步的兜底规划不再无视全部读数，
    而是只把确定的墙当墙、给“更可能有墙”（S > 0）的边加代价 K · P(有墙) / (1 − P(有墙)) = K · e^S，
    即按置信度优先绕开可疑的边，必要时才穿过；K 在开发集上选定（src/ext/posthoc.py soft）。
复杂度：每次观测 O(1)；每次规划与朝向 A* 相同，最坏 O(V (W + H) log V)；每步检查计划 O(计划长度)。
随机性：算法本身无随机性（噪声来自环境，由运行种子决定）。
"""

import math
from typing import ClassVar

from core.algorithm_api import (Cell, Direction, Observation, cost_lower_bound, direction_between,
                                heading_search, inside, step_cell)
from core.rules import BASIC


class BeliefAStarStrategy:
    """对数几率融合噪声读数判断墙，在乐观地图上按规则代价重规划。"""

    name = "belief_astar"
    supported_rules = {"noisy_sensor"}
    designed_for = ("noisy_sensor",)
    fusion = True   # False：只相信最近一次读数（消融）

    def __init__(self):
        self.cost = BASIC.cost_model
        self.sensor = None

    def configure(self, rule) -> None:
        """取规则的代价模型；有噪声观测层时取其传感器准确率（evidence_weight）。"""
        self.cost = rule.cost_model
        layer = rule.layer("observation")
        self.sensor = layer if hasattr(layer, "evidence_weight") else None

    def reset(self, *, width, height, start, goals, initial_heading, seed=None) -> None:
        self.size = (width, height)
        self.goals = frozenset(goals)
        self.score: dict[frozenset, float] = {}
        self.plan: list[Cell] = []
        self.previous: Cell | None = None
        self.replans = self.expanded_nodes = self.contacts = self.fallbacks = 0

    # -- 置信度 -------------------------------------------------------------
    def _weight(self, heading: Direction, direction: Direction) -> float:
        return math.inf if self.sensor is None else self.sensor.evidence_weight(heading, direction)

    def _observe(self, observation: Observation) -> None:
        here = observation.position
        if self.previous is not None and self.previous != here:
            self.score[frozenset((self.previous, here))] = -math.inf     # 走过：确定没墙
        self.previous = here
        contact = getattr(observation, "collision_wall", None)
        if contact is not None:
            self.contacts += 1
        for direction in Direction:
            neighbour = step_cell(here, direction)
            if not inside(neighbour, *self.size):
                continue
            edge = frozenset((here, neighbour))
            current = self.score.get(edge, 0.0)
            if math.isinf(current):
                continue                                                 # 已确定
            if direction == contact:
                self.score[edge] = math.inf                              # 撞到：确定有墙
                continue
            evidence = self._weight(observation.heading, direction)
            evidence = evidence if direction in observation.walls else -evidence
            self.score[edge] = current + evidence if self.fusion else evidence

    def _believed_wall(self, cell: Cell, direction: Direction) -> bool:
        neighbour = step_cell(cell, direction)
        return not inside(neighbour, *self.size) or self.score.get(frozenset((cell, neighbour)), 0.0) > 0

    def _certain_wall(self, cell: Cell, direction: Direction) -> bool:
        neighbour = step_cell(cell, direction)
        return not inside(neighbour, *self.size) or self.score.get(frozenset((cell, neighbour)), 0.0) == math.inf

    # -- 决策 ---------------------------------------------------------------
    def _search(self, here: Cell, heading: Direction, blocked, edge_penalty=None):
        result = heading_search(here, heading, self.goals, blocked, self.cost,
                                heuristic=lambda c, h: cost_lower_bound(self.cost, c, h, self.goals),
                                edge_penalty=edge_penalty)
        self.expanded_nodes += result.expanded
        return result

    def choose_direction(self, observation: Observation) -> Direction | None:
        here = observation.position
        self._observe(observation)
        if self.plan and self.plan[0] == here:
            self.plan.pop(0)
        route = [here, *self.plan]
        if not self.plan or any(self.score.get(frozenset(e), 0.0) > 0 for e in zip(route, route[1:])):
            self.replans += 1
            result = self._search(here, observation.heading, self._believed_wall)
            if not result.found:
                self.fallbacks += 1
                result = self._search(here, observation.heading, self._certain_wall, self._fallback_penalty())
            if not result.found:
                self.plan = []
                return None
            self.plan = result.route[1:]
        return direction_between(here, self.plan[0])

    def _fallback_penalty(self):
        """兜底规划的边代价；None 表示不加代价（原算法：无视全部读数）。"""
        return None

    def stats(self) -> dict:
        return {"replans": self.replans, "expanded_nodes": self.expanded_nodes,
                "contacts": self.contacts, "fallback_plans": self.fallbacks}

    def debug_view(self) -> dict:
        """已知墙为“更可能有墙”的边；格子文字不显示。"""
        return {"known_walls": [sorted(map(list, e)) for e, s in self.score.items() if s > 0],
                "plan": [list(c) for c in self.plan]}


class BeliefAStarNaive(BeliefAStarStrategy):
    """消融：只相信最近一次读数（不累积证据）的置信度重规划。"""

    name = "belief_astar_naive"
    fusion = False
    ablation_of = "belief_astar"


class BeliefAStarSoft(BeliefAStarStrategy):
    """改进：兜底规划按置信度给可疑的边加代价，而不是无视全部读数（冻结计划之后新增）。"""

    name = "belief_astar_soft"
    penalty_scale: ClassVar[float] = 0.25     # K，开发集选定（候选 0.25～4），见 results/ext/posthoc/soft.md
    MAX_SCORE: ClassVar[float] = 50.0         # e^S 的上限，避免溢出（S > 50 已几乎确定有墙）

    def _fallback_penalty(self):
        def penalty(cell: Cell, direction: Direction) -> float:
            s = self.score.get(frozenset((cell, step_cell(cell, direction))), 0.0)
            return self.penalty_scale * math.exp(min(s, self.MAX_SCORE)) if s > 0 else 0.0
        return penalty
