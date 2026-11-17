"""加载并验证迷宫，提供电脑鼠逐步探索所需的环境。"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# 格子使用 (x, y) 坐标；左下角是 (0, 0)。
Cell = tuple[int, int]


class Direction(str, Enum):
    """地图中的四个绝对方向。"""
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


# 按顺时针排列，后面用于计算转向；位移中的 y 向北增加。
_DIRECTIONS = tuple(Direction)
_DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
           Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}


@dataclass(frozen=True)
class Observation:
    """策略能看到的当前格信息；frozen=True 防止意外修改。"""
    position: Cell
    heading: Direction
    walls: frozenset[Direction]
    step_count: int


@dataclass(frozen=True)
class StepResult:
    """一次移动后的观测、运行状态及是否成功移动。"""
    observation: Observation
    status: str
    moved: bool


class Maze:
    """保存完整迷宫；未知地图策略只应接收 Observation，不应读取此对象。"""

    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError("maze must be a JSON object")
        self.maze_id = data.get("maze_id")
        self.width = data.get("width")
        self.height = data.get("height")
        if not isinstance(self.maze_id, str) or not self.maze_id.strip():
            raise ValueError("maze_id must be a non-empty string")
        if any(type(n) is not int or n <= 0 for n in (self.width, self.height)):
            raise ValueError("width and height must be positive integers")

        # 统一验证坐标的类型和范围，并转换为不可变元组。
        def cell(value):
            if (not isinstance(value, (list, tuple)) or len(value) != 2
                    or any(type(n) is not int for n in value)):
                raise ValueError("cell must contain two integers")
            x, y = value
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError("cell outside maze")
            return (x, y)

        self.start = cell(data.get("start"))
        try:
            self.start_heading = Direction(data.get("start_heading"))
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid start_heading") from exc
        goals = data.get("goals")
        if not isinstance(goals, list) or not goals:
            raise ValueError("goals must be a non-empty list")
        self.goals = frozenset(cell(goal) for goal in goals)
        edges = data.get("blocked_edges")
        if not isinstance(edges, list):
            raise ValueError("blocked_edges must be a list")
        # 每面内部墙用两个相邻格表示；无序集合让正反方向视为同一面墙。
        walls = set()
        for edge in edges:
            if not isinstance(edge, list) or len(edge) != 2:
                raise ValueError("wall must have two endpoints")
            a, b = (cell(endpoint) for endpoint in edge)
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
                raise ValueError("wall endpoints must be adjacent")
            wall = frozenset((a, b))
            if wall in walls:
                raise ValueError("duplicate wall")
            walls.add(wall)
        self._walls = frozenset(walls)
        self.metadata = data.get("metadata", {})
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object")

    @classmethod
    def from_json(cls, path):
        """从 JSON 文件读取地图，并通过构造函数验证内容。"""
        with Path(path).open(encoding="utf-8") as file:
            return cls(json.load(file))


class MazeEnvironment:
    """管理电脑鼠的位置、观测、移动和本次运行的统计。"""

    def __init__(self, maze: Maze, max_steps: int | None = None):
        if not isinstance(maze, Maze):
            raise TypeError("maze must be a Maze")
        if max_steps is None:
            # 默认预算：每个格子平均允许 20 次移动。
            max_steps = 20 * maze.width * maze.height
        if type(max_steps) is not int or max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        self._maze = maze
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        """回到起点并清空统计，返回初始观测。"""
        self.position = self._maze.start
        self.heading = self._maze.start_heading
        self.steps = self.repeat_visits = self.turns_90 = 0
        self.path = [self.position]
        # 起点已访问一次，但不算重复访问；起点也是目标时立即成功。
        self._visited = {self.position}
        self.status = "success" if self.position in self._maze.goals else "running"
        return self.observe()

    def observe(self):
        """只返回当前位置四个方向的墙，不返回完整地图。"""
        walls = set()
        x, y = self.position
        for direction, (dx, dy) in _DELTAS.items():
            neighbour = (x + dx, y + dy)
            # 迷宫边界和地图中登记的内部墙都视为墙壁。
            if (not (0 <= neighbour[0] < self._maze.width and
                     0 <= neighbour[1] < self._maze.height)
                    or frozenset((self.position, neighbour)) in self._maze._walls):
                walls.add(direction)
        return Observation(self.position, self.heading, frozenset(walls), self.steps)

    def step(self, direction):
        """尝试沿绝对方向移动一格，更新统计并返回结果。"""
        if self.status != "running":
            raise RuntimeError("cannot step after the run has ended")
        if not isinstance(direction, Direction) or direction in self.observe().walls:
            self.status = "invalid_action"
            return StepResult(self.observe(), self.status, False)
        # 取顺时针与逆时针中较短的转向：直行 0，左右转 1，掉头 2。
        difference = abs(_DIRECTIONS.index(direction) - _DIRECTIONS.index(self.heading))
        self.turns_90 += min(difference, 4 - difference)
        dx, dy = _DELTAS[direction]
        self.position = (self.position[0] + dx, self.position[1] + dy)
        self.heading = direction
        self.steps += 1
        # 每次进入曾访问的格子，重复访问次数加一。
        if self.position in self._visited:
            self.repeat_visits += 1
        self._visited.add(self.position)
        self.path.append(self.position)
        # 到达目标优先于预算耗尽，因此最后一步到达目标仍算成功。
        if self.position in self._maze.goals:
            self.status = "success"
        elif self.steps >= self.max_steps:
            self.status = "budget_exceeded"
        return StepResult(self.observe(), self.status, True)

    def finish(self, status):
        """由外部执行器记录无路、超时或异常等结束状态。"""
        if self.status != "running":
            raise RuntimeError("run has already ended")
        if status not in {"no_path", "timeout", "error"}:
            raise ValueError("invalid externally supplied status")
        self.status = status

    def summary(self, *, compute_seconds=0.0, peak_memory_bytes=None):
        """返回本次运行指标；计算时间和内存由外部执行器测量。"""
        return {"status": self.status, "steps": self.steps,
                "repeat_visits": self.repeat_visits, "turns_90": self.turns_90,
                "compute_seconds": compute_seconds, "path": list(self.path),
                "peak_memory_bytes": peak_memory_bytes}
