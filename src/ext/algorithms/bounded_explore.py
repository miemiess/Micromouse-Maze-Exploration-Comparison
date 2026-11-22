"""有界提前停止的探索（D5，两阶段规则下的近似算法）：冲刺代价 ≤ (1 + ε) × 最优时停止探索。

思路：探索的目的只是让冲刺足够好。设
    O = 乐观地图（未知边视为通路）上从起点到目标的最小代价，
    P = 确认地图（只走已确认可走的边）上从起点到目标的最小代价。
真实地图的通路介于两者之间，所以 O ≤ 真实最优代价 ≤ P，而 P 是现在就能保证跑出的冲刺代价。
一旦 P ≤ (1 + ε)·O，就有 P ≤ (1 + ε)·真实最优：冲刺代价有 (1 + ε) 倍的保证，可以停止探索。
ε = 0 时等价于“证明了最优路线后才停止”。两种代价都按当前规则的代价模型计算（基础规则为步数）。
信息假设：只用每步观测；理想观测下到过的格子四面都已确认（不支持噪声观测）。
决策规则：
    1. 还没到过目标：与朝向 A* 相同，在乐观地图上按规则代价规划到目标；
    2. 到过目标后，每到一个新格子（只有这时两张地图才会变化）重新计算 O 与 P；满足 P ≤ (1 + ε)·O 时返回 None（结束探索，环境记为 success）；
    3. 否则取乐观最优路线上还没到过的格子为候选，在乐观地图上走向最近的候选（到了就确认了它四周的墙），
       回到第 2 步。每到一个候选格，乐观路线上就少一个未知格，因此一定会停止。
变体：ε = 0、0.1、0.25（bounded_explore_e0 / e10 / e25），ε 事先固定，不调参。
复杂度：第 2 步每到一个新格子做两次朝向 A*，O(V (W + H) log V)。随机性：无。
"""

from core.algorithm_api import Cell, Direction, KnownWalls, Observation, cost_lower_bound, direction_between, \
    heading_search, inside, step_cell
from core.rules import BASIC


class BoundedExploreStrategy:
    """到达目标后继续探索，直到冲刺代价可证明不超过 (1 + ε) 倍最优（ε = 0）。"""

    name = "bounded_explore_e0"
    epsilon = 0.0
    designed_for = ("two_phase",)
    explores_after_goal = True

    def __init__(self):
        self.cost = BASIC.cost_model

    def configure(self, rule) -> None:
        self.cost = rule.cost_model

    def reset(self, *, width, height, start, goals, initial_heading, seed=None) -> None:
        self.size = (width, height)
        self.start, self.start_heading = tuple(start), initial_heading
        self.goals = frozenset(goals)
        self.walls = KnownWalls(width, height)
        self.visited: set[Cell] = set()
        self.plan: list[Cell] = []
        self.reached = False
        self.targets: frozenset = frozenset()
        self.lower = self.upper = None          # 最近一次的 O 与 P
        self.replans = self.expanded_nodes = self.bound_checks = 0

    # -- 两张地图 ------------------------------------------------------------
    def _confirmed_blocked(self, cell: Cell, direction: Direction) -> bool:
        """确认地图：只有到过的格子的四面是已知的（理想观测）。"""
        if self.walls.has_wall(cell, direction):
            return True
        return cell not in self.visited and step_cell(cell, direction) not in self.visited

    def _search(self, start, heading, goals, blocked):
        result = heading_search(start, heading, goals, blocked, self.cost,
                                heuristic=lambda c, h: cost_lower_bound(self.cost, c, h, goals))
        self.expanded_nodes += result.expanded
        return result

    # -- 决策 ---------------------------------------------------------------
    def choose_direction(self, observation: Observation) -> Direction | None:
        here = observation.position
        self.walls.observe(observation)
        new_cell = here not in self.visited
        self.visited.add(here)
        self.reached = self.reached or here in self.goals
        if self.plan and self.plan[0] == here:
            self.plan.pop(0)

        if not self.reached:
            targets = self.goals
        elif not new_cell and self.plan:
            targets = self.targets                             # 两张地图都没变：沿原计划继续
        else:
            self.bound_checks += 1
            optimistic = self._search(self.start, self.start_heading, self.goals, self.walls.blocked)
            confirmed = self._search(self.start, self.start_heading, self.goals, self._confirmed_blocked)
            self.lower, self.upper = optimistic.cost, confirmed.cost
            if confirmed.found and confirmed.cost <= (1 + self.epsilon) * optimistic.cost + 1e-9:
                self.plan = []
                return None                                   # 冲刺代价已有 (1 + ε) 倍保证
            targets = self.targets = frozenset(c for c in optimistic.route if c not in self.visited)
            if self.plan and self.plan[-1] not in targets:
                self.plan = []                                # 原目标已确认，换下一个候选
        if not self.plan or self.walls.route_blocked([here, *self.plan]):
            self.replans += 1
            result = self._search(here, observation.heading, targets, self.walls.blocked)
            if not result.found:
                self.plan = []
                return None
            self.plan = result.route[1:]
        return direction_between(here, self.plan[0])

    def stats(self) -> dict:
        return {"replans": self.replans, "expanded_nodes": self.expanded_nodes,
                "bound_checks": self.bound_checks, "lower_bound": self.lower, "upper_bound": self.upper}

    def debug_view(self) -> dict:
        return {"known_walls": self.walls.debug_walls(),
                "cell_color": [[x, y, "#e7f5e9"] for x, y in self.visited],
                "plan": [list(c) for c in self.plan]}


class BoundedExploreEps10(BoundedExploreStrategy):
    """冲刺代价可证明不超过 1.1 倍最优时停止探索（ε = 0.1）。"""
    name = "bounded_explore_e10"
    epsilon = 0.1


class BoundedExploreEps25(BoundedExploreStrategy):
    """冲刺代价可证明不超过 1.25 倍最优时停止探索（ε = 0.25）。"""
    name = "bounded_explore_e25"
    epsilon = 0.25

