"""规则最优（已知地图参照，E1）：完整地图已知时，当前规则代价最小的路线。

它在扩展规则下扮演基础规则中 BFS 的角色：给出“规则代价 / 最优代价”的分母，并在上位机
“已知地图规划”页展示规则下的最优路线。
    - 基础规则：单位代价，路线长度等于 BFS 最短路；
    - 转弯代价：在（格子, 朝向）上的 Dijkstra，代价 = 步数 + λ × 90° 转向；
    - 运动时间：同一搜索，代价为梯形加减速直线段用时 + 转向用时。
搜索本身在公共接口 core.rules.Ruleset.optimal_plan 中实现（实验框架计算最优代价时也用它），
本文件只把它接入统一的已知地图规划器接口。

复杂度：状态 4V 个，每个状态最多 3 个转向边和 O(W + H) 个直线段边，Dijkstra 为 O(V (W + H) log V)。
随机性：无。
"""

from core.algorithm_api import KNOWN_MAP, Cell, Maze
from core.rules import BASIC, Ruleset


class RuleOptimalPlanner:
    """完整地图已知时当前规则代价最小的路线（扩展规则下的最优参照）。"""

    name = "rule_optimal"
    mode = KNOWN_MAP

    def __init__(self):
        self.rule: Ruleset = BASIC
        self.optimal_cost: float | None = None

    def configure(self, rule: Ruleset) -> None:
        """由 Runner 在规划前调用，告知当前规则。"""
        self.rule = rule

    def plan(self, maze: Maze) -> list[Cell] | None:
        """返回从起点到目标的格子序列（含起点）；不可达时返回 None。"""
        result = self.rule.optimal_plan(maze)
        self.optimal_cost = result[0] if result else None
        return result[1] if result else None

    def stats(self) -> dict:
        """额外指标：规则下的最优代价。"""
        return {"optimal_cost": self.optimal_cost}
