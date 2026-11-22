"""按规则代价和当前朝向在乐观地图上规划，仅在剩余路线失效时重新搜索。

只从当前格观测学习墙壁，未知内部边视为可通行。与基础重复 A* 同为乐观重规划，
但状态含朝向，平局时路线可能不同。使用确定性的公共搜索，无随机性。
w=1 求当前乐观地图上的最小代价，w=2 的界仅适用于单次规划。
缓存路径长 L 时每步检查 O(L)。重规划至多有 4WH 种不同状态；若实际扩展 K 次、
最长直道 D 格、目标 G 个、堆最多 Q 项，扩展部分时间 O(K(D²+D(G+log(Q+1))))，
含直道前缀复制与堆操作；另有路线重建开销。墙、搜索记录及路线占用额外空间。
"""

from core.algorithm_api import (Cell, Direction, KnownWalls, Observation, cost_lower_bound,
                                direction_between, heading_search)
from core.rules import BASIC


class TurnAwareAStarStrategy:
    """在乐观地图上按当前规则代价规划，发现剩余路线受阻时重新搜索。"""

    name = "turn_aware_astar"
    designed_for = ("turn_cost", "motion_time")
    weight = 1.0

    def __init__(self):
        self.cost = BASIC.cost_model

    def configure(self, rule):
        self.cost = rule.cost_model

    def reset(self, *, width, height, start, goals, initial_heading, seed=None):
        self.walls = KnownWalls(width, height)
        self.goals = frozenset(goals)
        self.plan: list[Cell] = []
        self.replans = 0
        self.expanded_nodes = 0

    def choose_direction(self, observation: Observation) -> Direction | None:
        here = observation.position
        self.walls.observe(observation)
        if self.plan and self.plan[0] == here:
            self.plan.pop(0)
        if not self.plan or self.walls.route_blocked([here, *self.plan]):
            result = heading_search(
                here, observation.heading, self.goals, self.walls.blocked, self.cost,
                heuristic=lambda cell, heading: cost_lower_bound(self.cost, cell, heading, self.goals),
                weight=self.weight,
            )
            self.replans += 1
            self.expanded_nodes += result.expanded
            self.plan = result.route[1:] if result.found else []
        return direction_between(here, self.plan[0]) if self.plan else None

    def stats(self):
        return {"replans": self.replans, "expanded_nodes": self.expanded_nodes}

    def debug_view(self):
        return {"known_walls": self.walls.debug_walls(), "plan": [list(cell) for cell in self.plan]}


class WeightedTurnAwareAStarStrategy(TurnAwareAStarStrategy):
    """以两倍启发式权重在乐观地图上按当前规则代价重规划。"""

    name = "turn_aware_astar_w2"
    weight = 2.0
