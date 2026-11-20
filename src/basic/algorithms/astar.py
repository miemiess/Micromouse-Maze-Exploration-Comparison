"""已知地图 A* 最短路（已知地图规划，任务 C3），并提供通用 A* 搜索函数供 repeated_astar.py 复用。

信息假设：一开始就拿到完整地图（KNOWN_MAP 模式），与探索算法分开比较。
规则：f = g + h，g 为已走步数，h 为到最近目标的曼哈顿距离。每步代价为 1 时 h 不会高估
    （可采纳）且满足一致性，因此第一次取出目标时得到的就是最短路。
与 BFS 的关系：基础规则下所有移动代价相同，A* 与 BFS 的最短路长度一定相同，
    区别只在扩展节点数（expanded_nodes）：启发式能少搜多少格子。迷宫中墙壁常使曼哈顿
    距离严重低估真实距离，节省可能有限，这正是要用实验回答的问题。
平局规则：f 相同时优先 h 小（更靠近目标），再按加入队列的先后，结果确定。
复杂度：最坏 O(V log V)（V 为格子数，堆操作）；内存 O(V)。
随机性：无。
"""

import heapq
from collections.abc import Callable, Iterable

from algorithm_api import KNOWN_MAP, Cell, Maze, open_neighbours


def manhattan_to_goals(cell: Cell, goals: Iterable[Cell]) -> int:
    """格子到最近目标的曼哈顿距离（不考虑墙），作为 A* 的启发函数。"""
    return min(abs(cell[0] - gx) + abs(cell[1] - gy) for gx, gy in goals)


def astar_search(start: Cell, goals: frozenset[Cell],
                 neighbours: Callable[[Cell], Iterable[Cell]]
                 ) -> tuple[list[Cell] | None, dict[Cell, int], int]:
    """在任意网格图上做 A* 搜索（每步代价为 1）。

    Args:
        start: 起点。
        goals: 目标格集合，到达任意一个即停止。
        neighbours: 给定格子，返回可以一步走到的相邻格子。

    Returns:
        (路径（含起点，无路时为 None）, 已确定的 g 值 {格子: 步数}, 扩展节点数)。
    """
    g = {start: 0}
    parent: dict[Cell, Cell] = {}
    closed: set[Cell] = set()
    counter = 0
    heap = [(manhattan_to_goals(start, goals), manhattan_to_goals(start, goals), counter, start)]
    expanded = 0
    while heap:
        _, _, _, cell = heapq.heappop(heap)
        if cell in closed:
            continue
        closed.add(cell)
        expanded += 1
        if cell in goals:
            path = [cell]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return path[::-1], {c: g[c] for c in closed}, expanded
        for neighbour in neighbours(cell):
            cost = g[cell] + 1
            if neighbour not in closed and cost < g.get(neighbour, cost + 1):
                g[neighbour] = cost
                parent[neighbour] = cell
                h = manhattan_to_goals(neighbour, goals)
                counter += 1
                heapq.heappush(heap, (cost + h, h, counter, neighbour))
    return None, {c: g[c] for c in closed}, expanded


class AStarPlanner:
    """已知地图上的 A* 最短路（曼哈顿距离启发式）。"""

    name = "astar"
    mode = KNOWN_MAP

    def __init__(self):
        """初始化空的搜索记录。"""
        self._closed: dict[Cell, int] = {}
        self._expanded = 0

    def plan(self, maze: Maze) -> list[Cell] | None:
        """返回从起点到最近目标的最短路径（含起点）；目标不可达时返回 None。"""
        path, self._closed, self._expanded = astar_search(
            maze.start, frozenset(maze.goals),
            lambda cell: (n for _, n in open_neighbours(maze, cell)))
        return path

    def debug_view(self) -> dict:
        """供可视化工具显示：扩展过的格子及其离起点的步数。"""
        return {
            "cell_text": [[x, y, str(d)] for (x, y), d in self._closed.items()],
            "cell_color": [[x, y, "#e2ecff"] for x, y in self._closed],
        }

    def stats(self) -> dict:
        """额外指标：扩展节点数。"""
        return {"expanded_nodes": self._expanded}
