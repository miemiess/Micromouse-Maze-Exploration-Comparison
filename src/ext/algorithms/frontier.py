"""最近前沿探索：只沿已确认的通路前往最近的未访问格，再从新观测扩展前沿。

当前格的四向观测确认其出边；BFS 只穿过已访问格，首个未访问邻格就是前沿。
同距离优先进入可达的目标格，再按 BFS 发现顺序（北东南西）选择。无前沿返回 None。
每次规划时间、空间 O(V+E)，缓存路线每步 O(1) 推进；无随机性。
"""

from collections import deque

from core.algorithm_api import KnownWalls, direction_between


class FrontierStrategy:
    """沿已确认通路寻找最近的未访问格，逐步扩大已探索区域。"""

    name = "frontier"

    def reset(self, *, width, height, start, goals, initial_heading, seed=None):
        self.walls = KnownWalls(width, height)
        self.goals = frozenset(goals)
        self.visited = set()
        self.route = deque()
        self.expanded = 0
        self.replans = 0

    def _plan(self, here):
        parent = {here: None}
        layer = [here]
        while layer:
            next_layer = []
            frontier = []
            for cell in layer:
                self.expanded += 1
                for _, neighbour in self.walls.open_moves(cell):
                    if neighbour in parent:
                        continue
                    parent[neighbour] = cell
                    if neighbour in self.visited:
                        next_layer.append(neighbour)
                    else:
                        frontier.append(neighbour)
            if frontier:
                target = next((cell for cell in frontier if cell in self.goals), frontier[0])
                while target != here:
                    self.route.appendleft(target)
                    target = parent[target]
                return
            layer = next_layer

    def choose_direction(self, observation):
        here = observation.position
        self.walls.observe(observation)
        self.visited.add(here)
        if self.route and self.route[0] == here:
            self.route.popleft()
        if not self.route:
            self.replans += 1
            self._plan(here)
        return direction_between(here, self.route[0]) if self.route else None

    def debug_view(self):
        return {"known_walls": self.walls.debug_walls(), "plan": list(self.route)}

    def stats(self):
        return {"expanded_nodes": self.expanded, "replans": self.replans}
