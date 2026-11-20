"""重复 A*：在"未知边视为通路"的乐观地图上，从当前位置规划到目标；计划被新墙挡住时才重新规划。

与 Flood-Fill 的对比：两者对未知边的乐观假设相同，但
    - Flood-Fill 每一步都从目标反向传播，重算所有格子的距离；
    - 重复 A* 只在需要时从当前位置正向搜一条路，搜索范围由启发式引导。
    走出的路线可能相近，计算量（重新规划次数、扩展节点数）不同。
信息假设：只使用每步观测，在线维护已知墙；不读取真值地图。
决策规则：
    1. 用当前观测更新已知墙；
    2. 没有计划，或剩余计划中的某条边已知有墙时，用 A*（曼哈顿启发式）重新规划；
    3. 沿计划走一步；A* 在乐观地图上也找不到路时返回 None（no_path）。
复杂度：每次规划最坏 O(V log V)；不需要重新规划的步为 O(计划长度)（检查计划是否被挡）。
随机性：无。
"""

from core.algorithm_api import Cell, Direction, Observation, direction_between, inside, step_cell
from basic.algorithms.astar import astar_search


class RepeatedAStarStrategy:
    """乐观地图上按需重新规划的 A* 探索。"""

    name = "repeated_astar"

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清空已知墙和当前计划，参数含义见 src/README.md 的 Strategy 接口。"""
        self._size = (width, height)
        self._goals = frozenset(goals)
        self._walls: set[frozenset[Cell]] = set()
        self._plan: list[Cell] = []       # 从下一格开始的计划路线
        self._searched: dict[Cell, int] = {}
        self.replans = 0                  # 规划次数（含第一次）
        self.expanded_total = 0           # 所有规划累计扩展的节点数

    def _neighbours(self, cell: Cell):
        """乐观地图上的相邻格：在地图内，且两格之间没有已知墙（未知边视为通路）。"""
        for direction in Direction:
            neighbour = step_cell(cell, direction)
            if inside(neighbour, *self._size) and frozenset((cell, neighbour)) not in self._walls:
                yield neighbour

    def _plan_blocked(self, here: Cell) -> bool:
        """剩余计划是否为空，或其中某一步已知有墙。"""
        if not self._plan:
            return True
        route = [here] + self._plan
        return any(frozenset((a, b)) in self._walls for a, b in zip(route, route[1:]))

    def choose_direction(self, observation: Observation) -> Direction | None:
        """更新已知墙，必要时重新规划，然后沿计划走一步。"""
        here = observation.position
        for direction in observation.walls:
            neighbour = step_cell(here, direction)
            if inside(neighbour, *self._size):
                self._walls.add(frozenset((here, neighbour)))

        if self._plan and self._plan[0] == here:
            self._plan.pop(0)  # 已经走到计划中的这一格
        if self._plan_blocked(here):
            path, self._searched, expanded = astar_search(here, self._goals, self._neighbours)
            self.replans += 1
            self.expanded_total += expanded
            if path is None:
                self._plan = []
                return None
            self._plan = path[1:]
        return direction_between(here, self._plan[0])

    def debug_view(self) -> dict:
        """供可视化工具显示：已知墙、最近一次搜索扩展的格子、计划路线。"""
        return {
            "known_walls": [sorted(map(list, wall)) for wall in self._walls],
            "cell_color": [[x, y, "#e2ecff"] for x, y in self._searched],
            "cell_text": [[x, y, str(d)] for (x, y), d in self._searched.items()],
            "plan": [list(cell) for cell in self._plan],
        }
