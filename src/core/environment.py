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
class ContactObservation(Observation):
    """碰撞后由接触确认的墙。"""
    collision_wall: Direction


@dataclass(frozen=True)
class StepResult:
    """一次移动后的观测、运行状态及是否成功移动。"""
    observation: Observation
    status: str
    moved: bool
    collided: bool = False


class Maze:
    """保存完整迷宫；未知地图策略只应接收 Observation，不应读取此对象。"""

    def __init__(self, data: dict):
        """根据 JSON 数据构建并验证迷宫。

        Args:
            data: 符合 src/README.md 约定的迷宫字典。

        Raises:
            ValueError: 字段缺失、类型错误、坐标越界或墙壁不合法。
        """
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
            """将 [x, y] 验证并转换为 (x, y)。

            Raises:
                ValueError: 不是两个整数或超出迷宫范围。
            """
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

    @property
    def walls(self) -> frozenset:
        """全部内部墙（真值，只读）：每面墙是两个相邻格组成的 frozenset。

        只有环境、已知地图规划器、规则代价计算和可视化可以使用；未知地图探索策略不得读取。
        """
        return self._walls

    @classmethod
    def from_json(cls, path):
        """从 JSON 文件读取地图，并通过构造函数验证内容。

        Args:
            path: 迷宫 JSON 文件路径。

        Returns:
            验证通过的 Maze 对象。
        """
        with Path(path).open(encoding="utf-8") as file:
            return cls(json.load(file))


class MazeEnvironment:
    """管理电脑鼠的位置、观测、移动和本次运行的统计。"""

    def __init__(self, maze: Maze, max_steps: int | None = None, *, collision_limit: int | None = 1,
                 seed: int | None = None, stop_at_goal: bool = True):
        """创建环境并回到起点。

        Args:
            maze: 真值迷宫，只由环境持有。
            max_steps: 动作预算（每次有效方向尝试计一次，含撞墙）；None 时为 20 × 格子数。
            collision_limit: 累计撞墙几次终止。1 为基础规则：首次撞墙即 invalid_action，且不计入转向；
                N > 1 时撞墙原地转向、不移动，第 N 次记为 collision_limit；None 为不限次数。
                由撞墙处理层（src/ext/rules/collision.py）或噪声观测层设置。
            seed: 运行的随机种子，只供规则层的环境包装（如噪声观测）读取，环境本身不使用随机数。
            stop_at_goal: True（基础规则）到达目标即 success；False（两阶段规则的探索阶段）到达目标只记
                goal_reached，由执行器在策略结束探索时调用 finish("success")；动作预算耗尽时，
                到过目标记为 success，否则 budget_exceeded。

        Raises:
            TypeError: maze 不是 Maze。
            ValueError: max_steps 不是正整数。
        """
        if not isinstance(maze, Maze):
            raise TypeError("maze must be a Maze")
        if max_steps is None:
            # 默认预算：每个格子平均允许 20 次移动。
            max_steps = 20 * maze.width * maze.height
        if type(max_steps) is not int or max_steps <= 0:
            raise ValueError("max_steps must be a positive integer")
        if collision_limit is not None and (type(collision_limit) is not int or collision_limit < 1):
            raise ValueError("collision_limit must be a positive integer or None")
        self.collision_limit = collision_limit
        self.seed = seed
        self.stop_at_goal = stop_at_goal
        self.maze_id, self.width, self.height = maze.maze_id, maze.width, maze.height  # 公开的地图尺寸，不含墙
        self._maze = maze
        self.max_steps = max_steps
        self.reset()

    def reset(self):
        """回到起点并清空统计。

        Returns:
            起点处的 Observation。
        """
        self.position = self._maze.start
        self.heading = self._maze.start_heading
        self.steps = self.repeat_visits = self.turns_90 = 0
        self.actions = self.collisions = 0
        self.collision_wall = None
        self.path = [self.position]
        # 起点已访问一次，但不算重复访问；起点也是目标时立即成功（两阶段规则下只记为到过目标）。
        self._visited = {self.position}
        self.goal_reached = self.position in self._maze.goals
        self.status = "success" if self.goal_reached and self.stop_at_goal else "running"
        return self.observe()

    def observe(self):
        """只返回当前位置四个方向的墙，不返回完整地图。

        Returns:
            当前格的 Observation；边界也算作墙。
        """
        walls = set()
        x, y = self.position
        for direction, (dx, dy) in _DELTAS.items():
            neighbour = (x + dx, y + dy)
            # 迷宫边界和地图中登记的内部墙都视为墙壁。
            if (not (0 <= neighbour[0] < self._maze.width and
                     0 <= neighbour[1] < self._maze.height)
                    or frozenset((self.position, neighbour)) in self._maze._walls):
                walls.add(direction)
        if self.collision_wall is not None and self.collision_limit != 1:
            return ContactObservation(self.position, self.heading, frozenset(walls), self.steps, self.collision_wall)
        return Observation(self.position, self.heading, frozenset(walls), self.steps)

    def step(self, direction):
        """尝试沿绝对方向移动一格，并更新统计。

        Args:
            direction: 目标绝对方向。

        Returns:
            StepResult；非法方向或穿墙时 moved 为 False，状态为 invalid_action。

        Raises:
            RuntimeError: 运行已经结束。
        """
        if self.status != "running":
            raise RuntimeError("cannot step after the run has ended")
        self.collision_wall = None
        if not isinstance(direction, Direction):
            self.status = "invalid_action"
            return StepResult(self.observe(), self.status, False)
        self.actions += 1
        collided = direction in self.observe().walls
        if collided:
            self.collisions += 1
            self.collision_wall = direction
            if self.collision_limit == 1:  # 兼容基础规则的终止状态与朝向统计
                self.status = "invalid_action"
                return StepResult(self.observe(), self.status, False, True)
        # 取顺时针与逆时针中较短的转向：直行 0，左右转 1，掉头 2。
        difference = abs(_DIRECTIONS.index(direction) - _DIRECTIONS.index(self.heading))
        self.turns_90 += min(difference, 4 - difference)
        self.heading = direction
        if collided:
            if self.collision_limit is not None and self.collisions >= self.collision_limit:
                self.status = "collision_limit"
            elif self.actions >= self.max_steps:
                self.status = self._budget_status()
            return StepResult(self.observe(), self.status, False, True)
        dx, dy = _DELTAS[direction]
        self.position = (self.position[0] + dx, self.position[1] + dy)
        self.steps += 1
        # 每次进入曾访问的格子，重复访问次数加一。
        if self.position in self._visited:
            self.repeat_visits += 1
        self._visited.add(self.position)
        self.path.append(self.position)
        # 到达目标优先于预算耗尽，因此最后一步到达目标仍算成功。
        if self.position in self._maze.goals:
            self.goal_reached = True
        if self.goal_reached and self.stop_at_goal:
            self.status = "success"
        elif self.actions >= self.max_steps:
            self.status = self._budget_status()
        return StepResult(self.observe(), self.status, True)

    def _budget_status(self) -> str:
        """动作预算耗尽时的状态：两阶段规则下到过目标视为探索结束（success）。"""
        return "success" if self.goal_reached and not self.stop_at_goal else "budget_exceeded"

    def finish(self, status):
        """由外部执行器记录无路、超时或异常等结束状态。

        Args:
            status: "no_path"、"loop_detected"、"timeout" 或 "error"；两阶段规则（stop_at_goal 为
                False）下到过目标后还可以是 "success"（策略结束探索）。

        Raises:
            RuntimeError: 运行已经结束。
            ValueError: status 不在允许范围内。
        """
        if self.status != "running":
            raise RuntimeError("run has already ended")
        allowed = {"no_path", "loop_detected", "timeout", "error"}
        if self.goal_reached and not self.stop_at_goal:
            allowed.add("success")
        if status not in allowed:
            raise ValueError("invalid externally supplied status")
        self.status = status

    def summary(self, *, compute_seconds=0.0, peak_memory_bytes=None):
        """返回本次运行指标；计算时间和内存由外部执行器测量。

        Args:
            compute_seconds: 策略累计计算时间（秒）。
            peak_memory_bytes: 峰值内存（字节），未测量时为 None。

        Returns:
            包含状态、步数、重复访问、转向、耗时、路径和内存的字典；允许撞墙后继续时
            （collision_limit ≠ 1）另含 actions（动作数）与 collisions（撞墙次数）。
            基础规则下字段与 basic-rules-v1 相同。
        """
        summary = {"status": self.status, "steps": self.steps,
                   "repeat_visits": self.repeat_visits, "turns_90": self.turns_90,
                   "compute_seconds": compute_seconds, "path": list(self.path),
                   "peak_memory_bytes": peak_memory_bytes}
        if self.collision_limit != 1:
            summary.update(actions=self.actions, collisions=self.collisions)
        if not self.stop_at_goal:
            summary["goal_reached"] = self.goal_reached
        return summary
