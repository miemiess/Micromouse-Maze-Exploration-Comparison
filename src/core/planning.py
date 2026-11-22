"""规划工具（公共接口层）：探索算法与已知地图规划器共用的已知墙记录、（格子, 朝向）代价搜索与启发式。

为扩展阶段（E3 起）的算法准备，避免每个算法各写一套：
    - KnownWalls：在线记录已观测到的墙，并按“未知边视为通路”的乐观假设给出可走方向；
    - heading_search：在（格子, 朝向）状态上按任意代价层（core.rules.CostLayer）搜索代价最小的路线，
      边为“原地转 1 / 2 个 90°”或“沿当前朝向直走 k 格”（走—停—转假设）；传入 heuristic 即为 A*，
      不传为 Dijkstra。Ruleset.optimal_plan 用真值地图调用它，探索算法用自己的已知墙调用它；
    - cost_lower_bound：不高估的启发式“曼哈顿直线代价 + 必需转向的代价下界”。

本模块不依赖 core.rules 与任何具体规则：代价层只要有 run_cost(格数) 与 turn_cost(90° 次数) 两个方法。
探索算法只能把自己的 KnownWalls 交给搜索，不得读取真值地图（规则见 src/README.md）。
"""

import heapq
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Protocol

from core.environment import Cell, Direction, Observation

DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
          Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}
ORDER = tuple(Direction)  # N、E、S、W，顺时针
Edge = frozenset          # 两个相邻格组成的 frozenset，表示它们之间的一面墙
Blocked = Callable[[Cell, Direction], bool]   # (格子, 方向) → 这一步是否走不通


class CostModel(Protocol):
    """搜索使用的代价模型（core.rules.CostLayer 及基础规则的单位代价都满足）。"""

    def run_cost(self, cells: int) -> float:
        """沿直线连续走 cells 格的代价。"""

    def turn_cost(self, quarters: int) -> float:
        """原地转 quarters 个 90°（1 或 2）的代价。"""


def quarter_turns(a: Direction, b: Direction) -> int:
    """从朝向 a 转到 b 需要的 90° 转向次数（0、1、2），与环境的 turns_90 计数一致。"""
    diff = abs(ORDER.index(a) - ORDER.index(b)) % 4
    return min(diff, 4 - diff)


def step(cell: Cell, direction: Direction) -> Cell:
    dx, dy = DELTAS[direction]
    return (cell[0] + dx, cell[1] + dy)


# ====================================================================== 已知墙

class KnownWalls:
    """未知地图探索时在线维护的已知墙（只含地图内部的墙，外圈边界由 inside 判断）。

    用法：
        walls = KnownWalls(width, height)
        new = walls.observe(observation)          # 每步调用，返回新发现的墙
        walls.blocked(cell, direction)             # 乐观假设：只有已知墙和地图边界走不通
        heading_search(..., blocked=walls.blocked, ...)
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.edges: set[Edge] = set()

    def inside(self, cell: Cell) -> bool:
        return 0 <= cell[0] < self.width and 0 <= cell[1] < self.height

    def observe(self, observation: Observation) -> set[Edge]:
        """把当前格观测到的内部墙加入已知墙，返回其中新出现的墙。"""
        here, new = observation.position, set()
        for direction in observation.walls:
            neighbour = step(here, direction)
            if self.inside(neighbour):
                edge = frozenset((here, neighbour))
                if edge not in self.edges:
                    new.add(edge)
        self.edges |= new
        return new

    def has_wall(self, cell: Cell, direction: Direction) -> bool:
        """cell 的 direction 一侧是否有已知墙或地图边界。"""
        neighbour = step(cell, direction)
        return not self.inside(neighbour) or frozenset((cell, neighbour)) in self.edges

    blocked = has_wall  # 乐观假设下“走不通” = 已知墙或边界；可直接交给 heading_search

    def open_moves(self, cell: Cell) -> Iterator[tuple[Direction, Cell]]:
        """乐观地图上按 N/E/S/W 顺序可走的 (方向, 邻格)。"""
        for direction in ORDER:
            if not self.has_wall(cell, direction):
                yield direction, step(cell, direction)

    def route_blocked(self, route: Iterable[Cell]) -> bool:
        """路线（相邻格序列）中是否有一步穿过已知墙。"""
        cells = [tuple(c) for c in route]
        return any(frozenset((a, b)) in self.edges for a, b in zip(cells, cells[1:]))

    def __len__(self) -> int:
        return len(self.edges)

    def __contains__(self, edge) -> bool:
        return frozenset(edge) in self.edges

    def debug_walls(self) -> list:
        """debug_view() 的 known_walls 字段格式。"""
        return [sorted(map(list, edge)) for edge in self.edges]


def maze_blocked(width: int, height: int, walls: frozenset[Edge]) -> Blocked:
    """真值地图的“走不通”判断（只限已知地图规划器与驱动统计使用）。"""
    def blocked(cell: Cell, direction: Direction) -> bool:
        neighbour = step(cell, direction)
        return not (0 <= neighbour[0] < width and 0 <= neighbour[1] < height) \
            or frozenset((cell, neighbour)) in walls
    return blocked


# ====================================================================== 启发式

def cost_lower_bound(cost: CostModel, cell: Cell, heading: Direction, goals: Iterable[Cell]) -> float:
    """从（cell, heading）到最近目标的代价下界（不高估，可作 A* 启发式）。

    直线部分：至少走曼哈顿距离 m 格，代价 ≥ run_cost(m)（要求 run_cost 单调不减且次可加，
    即连续直走不比分段走贵；现有代价层都满足，见 tests/test_ext/test_planning.py）。
    转向部分：目标在斜方向时至少要朝向两个方向，转向 ≥ 转到其中一个方向的次数 + 1；
    每个 90° 至少花 min(turn_cost(1), turn_cost(2) / 2)。
    基础规则（单位代价、转向 0）下退化为曼哈顿距离。
    """
    per_quarter = min(cost.turn_cost(1), cost.turn_cost(2) / 2)
    best = float("inf")
    for goal in goals:
        dx, dy = goal[0] - cell[0], goal[1] - cell[1]
        needed = ([Direction.EAST if dx > 0 else Direction.WEST] if dx else []) \
            + ([Direction.NORTH if dy > 0 else Direction.SOUTH] if dy else [])
        if not needed:
            return 0.0
        quarters = min(quarter_turns(heading, d) for d in needed) + (len(needed) - 1)
        best = min(best, cost.run_cost(abs(dx) + abs(dy)) + quarters * per_quarter)
    return best


# ====================================================================== 搜索

@dataclass(frozen=True)
class SearchResult:
    """heading_search 的结果。

    cost：最小代价；不可达时为 inf。
    route：从起点到目标的格子序列（含起点）；不可达时为 None。
    heading：到达目标时的朝向；不可达时为 None。
    expanded：扩展（出堆且未过期）的状态数，用于比较计算量。
    """
    cost: float
    route: list[Cell] | None
    heading: Direction | None
    expanded: int

    @property
    def found(self) -> bool:
        return self.route is not None


Heuristic = Callable[[Cell, Direction], float]


def heading_search(start: Cell, heading: Direction, goals: Iterable[Cell], blocked: Blocked,
                   cost: CostModel, *, heuristic: Heuristic | None = None,
                   weight: float = 1.0) -> SearchResult:
    """在（格子, 朝向）上搜索代价最小的路线。

    Args:
        start, heading: 起点格与当前朝向。
        goals: 目标格；进入任一目标格即结束（不能穿过目标继续直走，与环境一致）。
        blocked: (格子, 方向) → 是否走不通。探索算法传 KnownWalls.blocked（乐观地图），
            已知地图规划器传 maze_blocked(...)。
        cost: 代价模型（run_cost / turn_cost）。
        heuristic: (格子, 朝向) → 剩余代价估计；None 时为 Dijkstra。
            例如 lambda c, h: cost_lower_bound(cost, c, h, goals)。
        weight: 加权 A* 的 w（f = g + w·h）；w = 1 且启发式不高估时结果最优，w > 1 时代价 ≤ w 倍最优。

    边：原地转 1 或 2 个 90°（代价 turn_cost），或沿当前朝向直走 k 格（代价 run_cost(k)，中途不能穿墙）。
    同代价时按入堆先后出堆，结果确定（无随机性）。
    """
    goals = frozenset(tuple(g) for g in goals)
    start_state = (tuple(start), heading)
    h = heuristic or (lambda _cell, _heading: 0.0)
    best = {start_state: 0.0}
    parent: dict = {}
    heap = [(weight * h(*start_state), 0, 0.0, start_state)]
    counter = expanded = 0
    while heap:
        _, _, g, state = heapq.heappop(heap)
        if g > best.get(state, float("inf")):
            continue
        expanded += 1
        cell, facing = state
        if cell in goals:
            route = [cell]
            while state in parent:
                state, cells = parent[state]
                route[:0] = cells
            return SearchResult(round(g, 6), route, facing, expanded)
        moves = [((cell, other), cost.turn_cost(q), [])
                 for other in ORDER if (q := quarter_turns(facing, other))]
        here, run = cell, []
        while not blocked(here, facing):
            run.append(here)
            here = step(here, facing)
            moves.append(((here, facing), cost.run_cost(len(run)), list(run)))
            if here in goals:
                break
        for nxt, edge_cost, cells in moves:
            total = g + edge_cost
            if total < best.get(nxt, float("inf")) - 1e-12:
                best[nxt] = total
                parent[nxt] = (state, cells)
                counter += 1
                heapq.heappush(heap, (total + weight * h(*nxt), counter, total, nxt))
    return SearchResult(float("inf"), None, None, expanded)
