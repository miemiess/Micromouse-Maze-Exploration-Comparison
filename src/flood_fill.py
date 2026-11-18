"""Flood-Fill 探索策略：在线维护已知墙，把未知边视为可通行，按到目标的距离下降方向前进。

信息假设：只使用每步的当前格四向墙壁观测，不读取真值地图。
未知边处理：未观测到的内部边乐观地视为无墙；观测到墙后立即写入在线地图（两侧格子共享同一面墙）。
决策规则：
    1. 用当前观测更新在线地图；
    2. 从所有目标格出发做 BFS（即 Flood-Fill 距离传播），得到每格在"已知墙 + 未知视为通路"下到目标的步数；
    3. 在当前格无墙的方向中选距离最小的邻格；距离相同时依次优先未访问的格子、
       保持当前朝向（少转弯）、N/E/S/W 顺序（与 README 基础实验约定一致）；
    4. 当前格在已知墙下无法到达任何目标（距离为无穷）时返回 None（no_path）。
复杂度：每步重新传播一次，O(格子数)；16×16 地图每步约 256 个格子。
随机性：无，seed 参数被忽略。
"""

from collections import deque

from environment import Cell, Direction, Observation

_DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
           Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}
_ORDER = tuple(Direction)


class FloodFillStrategy:
    """乐观假设未知边可通行的 Flood-Fill 探索。"""

    name = "flood_fill"

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清空在线地图并记录目标，参数含义见 src/README.md 的 Strategy 接口。"""
        self._size = (width, height)
        self._goals = frozenset(goals)
        self._walls: set[frozenset[Cell]] = set()
        self._distance: dict[Cell, int] = {}
        self._plan: list[Cell] = []
        self._visited: set[Cell] = set()

    def _inside(self, cell: Cell) -> bool:
        """判断格子是否在迷宫范围内。"""
        return 0 <= cell[0] < self._size[0] and 0 <= cell[1] < self._size[1]

    def _open_neighbours(self, cell: Cell):
        """按方向顺序生成 (方向, 邻格)：邻格在迷宫内，且两格之间没有已知墙。"""
        x, y = cell
        for direction in _ORDER:
            dx, dy = _DELTAS[direction]
            neighbour = (x + dx, y + dy)
            if self._inside(neighbour) and frozenset((cell, neighbour)) not in self._walls:
                yield direction, neighbour

    def _flood(self) -> dict[Cell, int]:
        """从所有目标格做 BFS，返回可到达格子到最近目标的步数。"""
        distance = {goal: 0 for goal in self._goals}
        queue = deque(self._goals)
        while queue:
            cell = queue.popleft()
            for _, neighbour in self._open_neighbours(cell):
                if neighbour not in distance:
                    distance[neighbour] = distance[cell] + 1
                    queue.append(neighbour)
        return distance

    def _best_move(self, cell: Cell, heading: Direction) -> tuple[Direction, Cell] | None:
        """在当前已知地图下选择距离最小的邻格；同距离时优先未访问、直行、N/E/S/W。

        Returns:
            (方向, 邻格)；没有可到达目标的邻格时返回 None。
        """
        options = [(self._distance[n], n in self._visited, d != heading, _ORDER.index(d), d, n)
                   for d, n in self._open_neighbours(cell) if n in self._distance]
        if not options:
            return None
        *_, direction, neighbour = min(options)
        return direction, neighbour

    def choose_direction(self, observation: Observation) -> Direction | None:
        """更新在线地图、重新传播距离，返回距离下降最快的方向。"""
        here, heading = observation.position, observation.heading
        self._visited.add(here)
        x, y = here
        for direction in observation.walls:
            dx, dy = _DELTAS[direction]
            if self._inside((x + dx, y + dy)):
                self._walls.add(frozenset((here, (x + dx, y + dy))))

        self._distance = self._flood()
        if here not in self._distance:
            self._plan = []
            return None
        move = self._best_move(here, heading)
        if move is None:
            self._plan = []
            return None

        # 预测路线（仅用于显示）：从下一格开始沿距离下降方向走到目标。
        direction, cell = move
        self._plan, step_heading = [cell], direction
        while self._distance[cell] > 0:
            step_heading, cell = self._best_move(cell, step_heading)
            self._plan.append(cell)
        return direction

    def debug_view(self) -> dict:
        """供可视化工具显示：已知墙、每格距离、预测到目标的路线。"""
        return {
            "known_walls": [sorted(map(list, wall)) for wall in self._walls],
            "cell_text": [[x, y, str(d)] for (x, y), d in self._distance.items()],
            "plan": [list(cell) for cell in self._plan],
        }
