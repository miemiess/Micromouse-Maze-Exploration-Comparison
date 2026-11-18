"""DFS 探索策略：优先进入未访问的相邻格，无路可走时沿原路逐格实际回溯。

信息假设：只使用每步的当前格四向墙壁观测，不读取真值地图。
决策规则：
    1. 把当前格标记为已访问；
    2. 按固定方向顺序（默认 N、E、S、W）找第一个"无墙且未访问"的相邻格，前进并把该方向压栈；
    3. 没有这样的格子时弹栈，沿反方向退回上一格（回溯是真实移动，计入步数）；
    4. 栈空仍无路可走，说明从起点可达的格子都已访问且没有遇到目标，返回 None（no_path）。
复杂度：每个格子最多进入一次、退出一次，移动步数不超过 2 × 可达格子数；每步决策 O(1)。
随机性：无，seed 参数被忽略。
"""

from environment import Cell, Direction, Observation

_DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
           Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}
_OPPOSITE = {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH,
             Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}


class DfsStrategy:
    """深度优先探索 + 实际回溯。"""

    name = "dfs"

    def __init__(self, order: tuple[Direction, ...] = tuple(Direction)):
        """设置尝试方向的顺序。

        Args:
            order: 选择未访问邻格时的方向优先级，默认 N、E、S、W。
        """
        self.order = tuple(order)

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清空上一轮的访问记录和回溯栈，参数含义见 src/README.md 的 Strategy 接口。"""
        self._size = (width, height)
        self._visited: set[Cell] = set()
        self._stack: list[Direction] = []      # 从起点到当前格的前进方向序列
        self._branch: list[Cell] = [start]     # 与栈对应的格子序列，仅用于显示
        self._walls: set[frozenset[Cell]] = set()
        self._order_seen: dict[Cell, int] = {}  # 首次访问的先后编号，仅用于显示

    def _inside(self, cell: Cell) -> bool:
        """判断格子是否在迷宫范围内。"""
        return 0 <= cell[0] < self._size[0] and 0 <= cell[1] < self._size[1]

    def choose_direction(self, observation: Observation) -> Direction | None:
        """根据当前观测返回下一步方向；所有可达格都已访问时返回 None。"""
        x, y = here = observation.position
        if here not in self._visited:
            self._visited.add(here)
            self._order_seen[here] = len(self._order_seen)
        for direction in observation.walls:
            dx, dy = _DELTAS[direction]
            if self._inside((x + dx, y + dy)):
                self._walls.add(frozenset((here, (x + dx, y + dy))))

        for direction in self.order:
            dx, dy = _DELTAS[direction]
            neighbour = (x + dx, y + dy)
            if direction not in observation.walls and neighbour not in self._visited:
                self._stack.append(direction)
                self._branch.append(neighbour)
                return direction

        if not self._stack:
            return None
        self._branch.pop()
        return _OPPOSITE[self._stack.pop()]

    def debug_view(self) -> dict:
        """供可视化工具显示：已知墙、首次访问顺序，并用底色标出当前分支（回溯栈对应的格子）。"""
        return {
            "known_walls": [sorted(map(list, wall)) for wall in self._walls],
            "cell_text": [[x, y, str(n)] for (x, y), n in self._order_seen.items()],
            "cell_color": [[x, y, "#c8b6ff"] for x, y in self._branch],
        }
