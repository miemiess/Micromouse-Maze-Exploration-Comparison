"""运行核心（不依赖任何界面库）：发现策略、逐步驱动"环境 + 策略"、生成每步的状态快照。

桌面应用、图片导出和测试都通过本模块运行算法，保证三者看到的是同一套规则：
    - 环境：src/environment.py 的 MazeEnvironment（步数、转向、重复访问、预算由它统计）；
    - 策略：src/ 中实现 Strategy 接口（name / reset / choose_direction）的类；
    - 计时：只累计策略 reset 与 choose_direction 的耗时，超过预算记为 timeout，
      与 src/README.md 的调用示例一致；debug_view() 不计时。
"""

import importlib
import inspect
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]  # tools/MazesTest/simulation.py → 项目根目录
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from environment import Direction, Maze, MazeEnvironment  # noqa: E402

Cell = tuple[int, int]
Edge = frozenset  # 两个相邻格组成的 frozenset，表示它们之间的一面墙

DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
          Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}

# src/ 中不是策略的模块，发现策略时跳过。
_NOT_STRATEGIES = {"environment", "run_experiments", "plot_results"}


def maze_walls(maze: Maze) -> frozenset[Edge]:
    """返回迷宫的全部内部墙。

    environment.Maze 目前没有公开墙壁的属性，这里是上位机中唯一读取其私有字段
    的位置。可视化和统计发生在环境之外，不经过策略，不违反真值隔离；
    若以后 Maze 增加公开属性，只需修改本函数。
    """
    return maze._walls


def wall_segment(a: Cell, b: Cell) -> tuple[tuple[int, int], tuple[int, int]]:
    """计算两个相邻格之间那面墙的线段端点（迷宫坐标，格子 (x, y) 占 [x, x+1] × [y, y+1]）。

    Returns:
        线段两端 ((x1, y1), (x2, y2))。
    """
    (x1, y1), (x2, y2) = sorted((tuple(a), tuple(b)))
    if x1 != x2:  # 东西相邻：墙是 x = x2 处的竖线
        return (x2, y1), (x2, y1 + 1)
    return (x1, y2), (x1 + 1, y2)  # 南北相邻：墙是 y = y2 处的横线


# ---------------------------------------------------------------- 策略发现

@dataclass(frozen=True)
class StrategyInfo:
    """一个可用策略的登记信息。"""
    name: str
    module: str
    class_name: str
    doc: str = ""

    def create(self):
        """新建一个策略对象（每次运行使用独立对象）。"""
        return getattr(importlib.import_module(self.module), self.class_name)()


def _is_strategy_class(obj, module_name: str) -> bool:
    """判断是否为在该模块中定义、实现了 Strategy 接口的类。"""
    return (inspect.isclass(obj) and obj.__module__ == module_name
            and isinstance(getattr(obj, "name", None), str)
            and callable(getattr(obj, "reset", None))
            and callable(getattr(obj, "choose_direction", None)))


def discover_strategies(src_dir: Path = SRC) -> tuple[dict[str, StrategyInfo], list[str]]:
    """扫描 src/ 下的模块，找出所有实现 Strategy 接口的类。

    组员新增算法文件后无需修改工具，重新启动即可出现在列表中。

    Args:
        src_dir: 策略所在目录。

    Returns:
        (按策略名排序的 {name: StrategyInfo}, 导入失败的错误信息列表)。
    """
    found, errors = {}, []
    for path in sorted(Path(src_dir).glob("*.py")):
        module_name = path.stem
        if module_name.startswith("_") or module_name in _NOT_STRATEGIES:
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # 组员代码有语法错误时不影响其他策略
            errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        for obj in vars(module).values():
            if _is_strategy_class(obj, module_name):
                doc = (inspect.getdoc(obj) or "").splitlines()
                found[obj.name] = StrategyInfo(obj.name, module_name, obj.__name__,
                                               doc[0] if doc else "")
    return dict(sorted(found.items())), errors


def load_strategy(spec: str):
    """按名称创建策略对象。

    Args:
        spec: 策略名（如 "flood_fill"，由 discover_strategies 查找），
            或 "模块名:类名"（如 "dfs:DfsStrategy"）。

    Raises:
        ValueError: 找不到该策略。
    """
    if ":" in spec:
        module_name, _, class_name = spec.partition(":")
        return getattr(importlib.import_module(module_name), class_name)()
    strategies, _ = discover_strategies()
    if spec not in strategies:
        raise ValueError(f"unknown strategy {spec!r}; available: {', '.join(strategies)}")
    return strategies[spec].create()


# ---------------------------------------------------------------- 逐步运行

@dataclass(frozen=True)
class Snapshot:
    """某一时刻供界面绘制和统计的完整状态（只读）。

    Attributes:
        decision: 已做出的决策次数（含未移动的非法动作）。
        position、heading: 电脑鼠当前位置和朝向。
        status: 环境运行状态，见 src/README.md。
        moved: 最近一次决策是否真的移动了。
        path: 从起点开始的实际位置序列。
        visited: 到过的格子。
        observed_walls: 已被观测到的真实墙（迷雾模式下只显示这些）。
        new_walls: 本次移动后新观测到的墙，用于高亮"被墙挡住"的瞬间。
        blocked: 策略试图穿墙时的 (格子, 方向)，否则为 None。
        replanned: 策略的预测路线是否因新信息而改变（策略提供 plan 时才有意义）。
        debug: 策略 debug_view() 的返回值，可能为 None。
        stats: 实时统计，键与 MazeEnvironment.summary() 一致，另含 visited_cells、coverage。
    """
    decision: int
    position: Cell
    heading: Direction
    status: str
    moved: bool
    path: tuple[Cell, ...]
    visited: frozenset[Cell]
    observed_walls: frozenset[Edge]
    new_walls: frozenset[Edge]
    blocked: tuple[Cell, Direction] | None
    replanned: bool
    debug: dict | None
    stats: dict = field(default_factory=dict)


class Runner:
    """把一个策略放进 MazeEnvironment 中逐步运行。

    用法：
        runner = Runner(maze, FloodFillStrategy(), seed=1)
        while not runner.finished:
            snapshot = runner.step()
    """

    def __init__(self, maze: Maze, strategy, *, seed: int | None = None,
                 max_steps: int | None = None, time_budget: float = 30.0):
        """创建环境并完成第一次 reset。

        Args:
            maze: 真值迷宫，只交给环境，策略拿不到。
            strategy: 实现 Strategy 接口的对象。
            seed: 传给策略的随机种子。
            max_steps: 移动预算；None 时使用环境默认值 20 × 格子数。
            time_budget: 策略累计计算时间上限（秒），超过记为 timeout。
        """
        self.maze = maze
        self.strategy = strategy
        self.seed = seed
        self.time_budget = time_budget
        self.env = MazeEnvironment(maze, max_steps=max_steps)
        self.name = getattr(strategy, "name", type(strategy).__name__)
        self.reset()

    # -- 状态 -------------------------------------------------------------
    @property
    def finished(self) -> bool:
        """运行是否已经结束（成功、无路、超预算、超时、非法动作或异常）。"""
        return self.env.status != "running"

    @property
    def debug(self) -> dict | None:
        """策略最近一次 debug_view() 的结果。"""
        return self._debug

    def reset(self) -> Snapshot:
        """回到起点、重新初始化策略，返回初始快照。"""
        self.error: str | None = None
        self.compute_seconds = 0.0
        self._decisions = 0
        self._debug = None
        self._plan: list[Cell] | None = None
        observation = self.env.reset()
        self._observation = observation
        self._observed: set[Edge] = set()
        new_walls = self._record_walls(observation)
        try:
            started = perf_counter()
            self.strategy.reset(
                width=self.maze.width, height=self.maze.height, start=self.maze.start,
                goals=frozenset(self.maze.goals), initial_heading=self.maze.start_heading,
                seed=self.seed)
            self.compute_seconds += perf_counter() - started
        except Exception:
            self._fail()
        self._last = self._snapshot(moved=False, new_walls=new_walls,
                                    blocked=None, replanned=False)
        return self._last

    def snapshot(self) -> Snapshot:
        """返回最近一次的快照（不推进）。"""
        return self._last

    def summary(self) -> dict:
        """返回环境统计结果，compute_seconds 为本运行器测得的策略耗时。"""
        return self.env.summary(compute_seconds=self.compute_seconds)

    # -- 推进 -------------------------------------------------------------
    def step(self) -> Snapshot:
        """让策略做一次决策并执行；运行已结束时直接返回最后的快照。"""
        if self.finished:
            return self._last
        moved, new_walls, blocked, replanned = False, frozenset(), None, False
        try:
            started = perf_counter()
            direction = self.strategy.choose_direction(self._observation)
            self.compute_seconds += perf_counter() - started
            self._decisions += 1
            replanned = self._update_debug()

            if self.compute_seconds > self.time_budget:
                self.env.finish("timeout")
            elif direction is None:
                self.env.finish("no_path")
            else:
                result = self.env.step(direction)
                moved = result.moved
                self._observation = result.observation
                if moved:
                    new_walls = self._record_walls(result.observation)
                else:
                    blocked = (self.env.position, direction)
        except Exception:
            self._fail()
        self._last = self._snapshot(moved=moved, new_walls=new_walls,
                                    blocked=blocked, replanned=replanned)
        return self._last

    def run(self, max_decisions: int | None = None) -> Snapshot:
        """连续推进直到结束，或最多 max_decisions 次决策。"""
        count = 0
        while not self.finished and (max_decisions is None or count < max_decisions):
            self.step()
            count += 1
        return self._last

    # -- 内部 -------------------------------------------------------------
    def _fail(self) -> None:
        """策略抛出异常：保存异常信息并按实验规则记为 error。"""
        self.error = traceback.format_exc(limit=4)
        if not self.finished:
            self.env.finish("error")

    def _record_walls(self, observation) -> frozenset[Edge]:
        """把当前格观测到的内部墙加入已观测集合，返回其中新出现的墙。"""
        x, y = observation.position
        new = set()
        for direction in observation.walls:
            dx, dy = DELTAS[direction]
            neighbour = (x + dx, y + dy)
            if 0 <= neighbour[0] < self.maze.width and 0 <= neighbour[1] < self.maze.height:
                wall = frozenset((observation.position, neighbour))
                if wall not in self._observed:
                    new.add(wall)
        self._observed |= new
        return frozenset(new)

    def _update_debug(self) -> bool:
        """读取策略的 debug_view()，返回预测路线是否发生了非顺延的改变。"""
        view = getattr(self.strategy, "debug_view", None)
        if not callable(view):
            return False
        self._debug = view()
        plan = self._debug.get("plan") if isinstance(self._debug, dict) else None
        if plan is None:
            return False
        plan = [tuple(cell) for cell in plan]
        previous, self._plan = self._plan, plan
        # 正常情况下新路线 = 旧路线去掉已走过的第一格；不一致说明新观测改变了计划。
        return previous is not None and plan != previous[1:]

    def _snapshot(self, *, moved, new_walls, blocked, replanned) -> Snapshot:
        """根据环境当前状态组装快照。"""
        env = self.env
        visited = frozenset(env.path)
        stats = {key: value for key, value in self.summary().items() if key != "path"}
        stats.update(decisions=self._decisions, visited_cells=len(visited),
                     coverage=len(visited) / (self.maze.width * self.maze.height),
                     observed_walls=len(self._observed))
        return Snapshot(self._decisions, env.position, env.heading, env.status, moved,
                        tuple(env.path), visited, frozenset(self._observed),
                        frozenset(new_walls), blocked, replanned, self._debug, stats)
