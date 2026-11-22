"""D* Lite：仅根据当前观测，在乐观的单位步长地图上增量维护到目标的距离。

g 是上次扩展得到的距离，rhs 是用邻格重新估算的一步前瞻距离。
新墙删除一条双向边，只从两个端点开始修复；起点移动用 km 修正队列键。
多目标均以 rhs=0 初始化。平局按固定方向，算法无随机性。
每次有效扩展更新至多四邻，每次堆操作 O(log Q)，Q 包含等待清理的过期项。
距离表与有效队列索引 O(格子数)，堆另占 O(Q)。
"""

from heapq import heappop, heappush
from math import inf

from core.algorithm_api import KnownWalls


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class DStarLiteStrategy:
    """发现新墙后增量修复单位步长距离，沿当前最短路前进一步。"""

    name = "dstar_lite"

    def reset(self, *, width, height, start, goals, initial_heading, seed=None):
        self.walls = KnownWalls(width, height)
        self.goals = frozenset(goals)
        self.here = self.last_repair = start
        self.km = 0
        self.g = {}
        self.rhs = dict.fromkeys(goals, 0)
        self.heap = []
        self.pending = {}
        self.expanded = 0
        self.repairs = 0
        self.next_cell = None
        for goal in self.goals:
            self._enqueue(goal)

    def _key(self, cell):
        best = min(self.g.get(cell, inf), self.rhs.get(cell, inf))
        return (best + manhattan(self.here, cell) + self.km, best)

    def _enqueue(self, cell):
        key = self._key(cell)
        self.pending[cell] = key
        heappush(self.heap, (key, cell))

    def _update(self, cell):
        if cell not in self.goals:
            self.rhs[cell] = min((1 + self.g.get(n, inf)
                                  for _, n in self.walls.open_moves(cell)), default=inf)
        self.pending.pop(cell, None)
        if self.g.get(cell, inf) != self.rhs.get(cell, inf):
            self._enqueue(cell)

    def _repair(self):
        while self.heap:
            old_key, cell = self.heap[0]
            if self.pending.get(cell) != old_key:
                heappop(self.heap)
                continue
            if old_key >= self._key(self.here) and self.rhs.get(self.here, inf) == self.g.get(self.here, inf):
                break
            heappop(self.heap)
            del self.pending[cell]
            if old_key < self._key(cell):
                self._enqueue(cell)
                continue
            self.expanded += 1
            if self.g.get(cell, inf) > self.rhs.get(cell, inf):
                self.g[cell] = self.rhs[cell]
            else:
                self.g[cell] = inf
                self._update(cell)
            for _, neighbour in self.walls.open_moves(cell):
                self._update(neighbour)

    def choose_direction(self, observation):
        self.here = observation.position
        new = self.walls.observe(observation)
        if new or not self.repairs:
            self.km += manhattan(self.last_repair, self.here)
            self.last_repair = self.here
            for cell in sorted({cell for edge in new for cell in edge}):
                self._update(cell)
            self._repair()
            self.repairs += 1
        self.next_cell = None
        if self.here in self.goals or self.g.get(self.here, inf) == inf:
            return None
        direction, self.next_cell = min(self.walls.open_moves(self.here),
                                        key=lambda move: self.g.get(move[1], inf))
        return direction

    def debug_view(self):
        return {"known_walls": self.walls.debug_walls(),
                "plan": [list(self.next_cell)] if self.next_cell is not None else []}

    def stats(self):
        return {"expanded_nodes": self.expanded, "replans": self.repairs}
