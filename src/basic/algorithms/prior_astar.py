"""先验增强的重复 A*（本组提出的变体，C1 / C2）：在重复 A* 的基础上增加两个可开关的机制。

背景：重复 A* 把未知边全部视为通路（乐观假设），被新墙挡住后才修正。在单位步长代价下，
它被"看起来能走、其实有墙"的未知边误导，是多走路的主要原因（Docs/Result.md 发现 2、6）。
本策略用两种办法减少这种误导，设计说明见 Docs/basic/algorithm-design.md。

机制 1：柱子规则推断墙（结构先验，use_post_rule）
    比赛迷宫规则：除目标区中心外，每根内部柱子至少连着一面墙（因此除目标区外没有 2×2 的空地）。
    当一根柱子连着的 4 条边中有 3 条已确认无墙、第 4 条未知时，推断第 4 条是墙（"软墙"）。
    - 软墙只用于规划，不会让地图断开：软墙两端的格子已由另外 3 条观测到的通路相连，
      而观测到的通路永远不会被推断为墙，因此推断错误最多让路线变长，不会导致失败。
    - 观测到违反规则的情况（某根柱子 4 条边都无墙）时，说明这张迷宫不遵守比赛规则，
      本次运行剩余部分自动关闭机制 1，退化为普通的乐观假设。
机制 2：自适应未知边惩罚（penalty_scale = c）
    已确认无墙的边代价为 1，未知边代价为 1 + δ（软墙和已知墙不可走）。δ > 0 时，规划会在
    "已知可走的路"和"看起来更短但没确认的路"之间权衡；δ = 0 时与重复 A* 相同。
    δ 不是常数：按已观测的内部边估计墙的比例 p，取 δ = c · p / (1 − p)。墙密的迷宫（如无环迷宫）
    未知边更可能是墙，惩罚更大；开阔的迷宫惩罚更小。c 只在开发集（种子 101～110 的生成地图）
    上选取，选定后冻结（见实验计划）。

其余规则与重复 A* 相同：只在计划为空或被（软）墙挡住时重新规划；乐观地图上也找不到路时返回
None（no_path）。两个机制都关闭时，每一步的决策与 repeated_astar 完全相同（有测试验证）。

信息假设：只使用每步观测，在线维护已知墙与已知通路；不读取真值地图。
复杂度：每次规划最坏 O(V log V)；每步推断只检查当前格的 4 根柱子，O(1)。额外内存 O(V)。
随机性：无。
"""

import heapq

from core.algorithm_api import Cell, Direction, Observation, direction_between, inside, step_cell
from basic.algorithms.astar import manhattan_to_goals

Edge = frozenset


class _PriorAStar:
    """先验增强的重复 A* 的共同实现；子类设定 name 和两个机制的开关。"""

    name = ""
    use_post_rule = True
    unknown_penalty = 0.0
    penalty_scale: float | None = None  # 不为 None 时按墙密度自适应计算 δ（见 current_penalty）

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清空在线地图与计划，参数含义见 src/README.md 的 Strategy 接口。"""
        self._size = (width, height)
        self._goals = frozenset(goals)
        self._walls: set[Edge] = set()      # 观测到的墙
        self._open: set[Edge] = set()       # 观测到的通路
        self._inferred: set[Edge] = set()   # 由柱子规则推断的软墙
        self._plan: list[Cell] = []
        self._searched: dict[Cell, float] = {}
        self.post_rule_active = self.use_post_rule
        self.replans = 0
        self.inferred_total = 0             # 累计推断的软墙数
        self.expanded_total = 0

    # -- 在线地图 ----------------------------------------------------------
    def _observe(self, observation: Observation) -> None:
        """记录当前格四面的墙和通路；软墙若被观测推翻，说明本图不守柱子规则。"""
        here = observation.position
        for direction in Direction:
            neighbour = step_cell(here, direction)
            if not inside(neighbour, *self._size):
                continue
            edge = Edge((here, neighbour))
            if direction in observation.walls:
                self._walls.add(edge)
                self._inferred.discard(edge)
            else:
                self._open.add(edge)
                if edge in self._inferred:
                    self._disable_post_rule()
        if self.post_rule_active:
            self._apply_post_rule(here)

    def _post_edges(self, px: int, py: int) -> list[Edge] | None:
        """柱子 (px, py) 连着的 4 条边（柱子位于格子 (px-1..px, py-1..py) 的公共角）。

        外边界上的柱子和目标区中心的柱子不受规则约束，返回 None。
        """
        width, height = self._size
        if not (0 < px < width and 0 < py < height):
            return None
        sw, se, nw, ne = (px - 1, py - 1), (px, py - 1), (px - 1, py), (px, py)
        if {sw, se, nw, ne} <= self._goals:
            return None
        return [Edge((sw, se)), Edge((nw, ne)), Edge((sw, nw)), Edge((se, ne))]

    def _apply_post_rule(self, here: Cell) -> None:
        """检查当前格四个角上的柱子：3 条边已知无墙时推断第 4 条为墙；4 条都无墙时关闭规则。"""
        x, y = here
        for px, py in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            edges = self._post_edges(px, py)
            if edges is None or any(e in self._walls or e in self._inferred for e in edges):
                continue
            unknown = [e for e in edges if e not in self._open]
            if not unknown:
                self._disable_post_rule()
                return
            if len(unknown) == 1:
                self._inferred.add(unknown[0])
                self.inferred_total += 1

    def _disable_post_rule(self) -> None:
        """观测证明本图不遵守柱子规则：丢弃所有软墙，本次运行不再推断。"""
        self.post_rule_active = False
        self._inferred.clear()

    # -- 规划 --------------------------------------------------------------
    def _blocked(self, edge: Edge, use_inferred: bool) -> bool:
        return edge in self._walls or (use_inferred and edge in self._inferred)

    def current_penalty(self) -> float:
        """本次规划使用的未知边惩罚 δ。

        penalty_scale = c 为 None 时用固定的 unknown_penalty；否则按已观测的内部边估计墙的比例
        p = (墙数 + 1) / (墙数 + 通路数 + 2)（Beta(1, 1) 平滑），取 δ = c · p / (1 − p)：
        墙越密，未知边越可能是墙，越应该偏向已确认的通路。
        """
        if self.penalty_scale is None:
            return self.unknown_penalty
        walls, opens = len(self._walls), len(self._open)
        p = (walls + 1) / (walls + opens + 2)
        return self.penalty_scale * p / (1 - p)

    def _search(self, start: Cell, use_inferred: bool) -> list[Cell] | None:
        """乐观地图上的 A*：已知通路代价 1，未知边代价 1 + δ；曼哈顿距离不高估，因此结果最优。

        堆的排序键与 astar.astar_search 相同（f, h, 入堆序号），δ = 0 且不用软墙时路线一致。
        """
        goals, penalty = self._goals, self.current_penalty()
        g: dict[Cell, float] = {start: 0.0}
        parent: dict[Cell, Cell] = {}
        closed: set[Cell] = set()
        counter = 0
        h0 = manhattan_to_goals(start, goals)
        heap = [(h0, h0, counter, start)]
        while heap:
            _, _, _, cell = heapq.heappop(heap)
            if cell in closed:
                continue
            closed.add(cell)
            self.expanded_total += 1
            if cell in goals:
                self._searched = {c: g[c] for c in closed}
                path = [cell]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                return path[::-1]
            for direction in Direction:
                neighbour = step_cell(cell, direction)
                if not inside(neighbour, *self._size) or neighbour in closed:
                    continue
                edge = Edge((cell, neighbour))
                if self._blocked(edge, use_inferred):
                    continue
                cost = g[cell] + (1.0 if edge in self._open else 1.0 + penalty)
                if cost < g.get(neighbour, cost + 1):
                    g[neighbour] = cost
                    parent[neighbour] = cell
                    h = manhattan_to_goals(neighbour, goals)
                    counter += 1
                    heapq.heappush(heap, (cost + h, h, counter, neighbour))
        self._searched = {c: g[c] for c in closed}
        return None

    def _plan_blocked(self, here: Cell) -> bool:
        """剩余计划是否为空，或其中某一步已知有墙 / 有软墙。"""
        if not self._plan:
            return True
        route = [here] + self._plan
        return any(self._blocked(Edge((a, b)), self.post_rule_active)
                   for a, b in zip(route, route[1:]))

    def choose_direction(self, observation: Observation) -> Direction | None:
        """更新在线地图（含推断），必要时重新规划，然后沿计划走一步。"""
        here = observation.position
        self._observe(observation)
        if self._plan and self._plan[0] == here:
            self._plan.pop(0)
        if self._plan_blocked(here):
            self.replans += 1
            path = self._search(here, use_inferred=self.post_rule_active)
            if path is None:
                self._plan = []
                return None
            self._plan = path[1:]
        return direction_between(here, self._plan[0])

    def stats(self) -> dict:
        """额外指标：规划次数、推断的软墙数、规则是否被关闭。"""
        return {"replans": self.replans,
                "inferred_walls": self.inferred_total,
                "post_rule_disabled": self.use_post_rule and not self.post_rule_active}

    def debug_view(self) -> dict:
        """供可视化工具显示：已知墙（含软墙）、最近一次搜索的格子与代价、计划路线。"""
        return {
            "known_walls": [sorted(map(list, wall)) for wall in self._walls | self._inferred],
            "cell_color": [[x, y, "#e2ecff"] for x, y in self._searched],
            "cell_text": [[x, y, f"{d:g}"] for (x, y), d in self._searched.items()],
            "plan": [list(cell) for cell in self._plan],
        }


# 开发集（种子 101～110 的 120 张生成地图）上按"步数 / 最短路"均值选定，之后冻结，不再按测试结果修改。
# 调参记录见 results/basic/dev/tuning.md（复现脚本 src/basic/dev_tuning.py）。
FROZEN_SCALE = 2.5   # 自适应惩罚系数 c（候选 0.5～5）
FROZEN_FIXED = 2.5   # 固定惩罚 δ 的最佳值（候选 0～4），只用于消融对照


class PriorAStarStrategy(_PriorAStar):
    """先验增强的重复 A*（完整版）：柱子规则推断墙 + 按墙密度自适应的未知边惩罚。"""

    name = "prior_astar"
    ablation_baseline = "repeated_astar"  # 消融基线：两个机制都关闭时与它逐格相同
    use_post_rule = True
    penalty_scale = FROZEN_SCALE


class PriorAStarNoPostRule(_PriorAStar):
    """消融：去掉柱子规则，只保留自适应未知边惩罚。"""

    name = "prior_astar_no_post"
    ablation_of = "prior_astar"
    use_post_rule = False
    penalty_scale = FROZEN_SCALE


class PriorAStarNoPenalty(_PriorAStar):
    """消融：去掉未知边惩罚（δ = 0），只保留柱子规则。"""

    name = "prior_astar_no_penalty"
    ablation_of = "prior_astar"
    use_post_rule = True
    penalty_scale = None
    unknown_penalty = 0.0


class PriorAStarFixedPenalty(_PriorAStar):
    """消融：自适应惩罚换成开发集上最好的固定 δ，检验"自适应"本身的作用。"""

    name = "prior_astar_fixed"
    ablation_of = "prior_astar"
    use_post_rule = True
    penalty_scale = None
    unknown_penalty = FROZEN_FIXED
