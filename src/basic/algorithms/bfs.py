"""已知地图 BFS 最短路（已知地图规划，任务 C3）。

信息假设：一开始就拿到完整地图（KNOWN_MAP 模式），与未知地图探索算法分开实验、分开比较；
    作为参照，"探索步数 ÷ BFS 最短路长度"可衡量探索算法比全知最优多走了多少。
规则：从起点做广度优先搜索，按 N/E/S/W 顺序扩展邻格，第一次取出目标格时停止，
    沿父指针回溯得到路径。所有移动代价相同（不计转弯），因此得到的是步数最短的路径；
    步数相同的路径中，按扩展顺序取第一条，不保证转弯最少。
无路：目标不可达时返回 None（记为 no_path）。
复杂度：时间 O(V + E)，V 为格子数，E 为相邻无墙的边数；内存 O(V)。
额外指标：expanded_nodes（从队列取出并扩展的格子数），用于和 Dijkstra、A* 等比较搜索开销。
随机性：无。
"""

from collections import deque

from algorithm_api import KNOWN_MAP, Cell, Maze, open_neighbours


class BfsPlanner:
    """已知地图上的广度优先搜索最短路。"""

    name = "bfs"
    mode = KNOWN_MAP

    def __init__(self):
        """初始化空的搜索记录。"""
        self._depth: dict[Cell, int] = {}
        self._expanded = 0

    def plan(self, maze: Maze) -> list[Cell] | None:
        """返回从起点到最近目标的最短路径（含起点）；目标不可达时返回 None。"""
        start, goals = maze.start, frozenset(maze.goals)
        self._depth = {start: 0}
        self._expanded = 0
        parent: dict[Cell, Cell] = {}
        queue = deque([start])
        while queue:
            cell = queue.popleft()
            self._expanded += 1
            if cell in goals:
                path = [cell]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                return path[::-1]
            for _, neighbour in open_neighbours(maze, cell):
                if neighbour not in self._depth:
                    self._depth[neighbour] = self._depth[cell] + 1
                    parent[neighbour] = cell
                    queue.append(neighbour)
        return None

    def debug_view(self) -> dict:
        """供可视化工具显示：搜索到的格子及其离起点的距离。"""
        return {
            "cell_text": [[x, y, str(d)] for (x, y), d in self._depth.items()],
            "cell_color": [[x, y, "#e2ecff"] for x, y in self._depth],
        }

    def stats(self) -> dict:
        """额外指标：扩展节点数。"""
        return {"expanded_nodes": self._expanded}
