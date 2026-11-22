"""算法统一接口：算法文件只写算法，接入、运行和统计都由本文件负责。

本文件分四部分：
    1. 共用工具：方向、位移、转向、邻格、读取地图墙壁等，各算法文件直接导入，不要各自重写；
    2. 两类算法接口：
       - 未知地图探索（EXPLORE）：reset + choose_direction，只能看到每步的当前格观测，
         与 src/README.md 的 Strategy 接口完全一致；
       - 已知地图规划（KNOWN_MAP）：plan(maze) 一次拿到完整地图，返回整条路径。
         README 规定两类算法分开实验、分开比较；
    3. 自动发现：扫描 src/basic/algorithms/（基础规则）与 src/ext/algorithms/（扩展）中的算法类，
       新增算法文件无需修改任何其他文件；
    4. 驱动：Runner 逐步运行任意一类算法并生成快照，run_episode 一次跑完并返回统计。
       上位机（tools/MazesTest）、批量实验和测试都使用这里的驱动，保证规则只有一份。

新增算法：在 src/ext/algorithms/（基础规则已冻结，新算法一律放扩展层）中新建一个文件，写一个类，
设置 name（唯一名称），按类别实现对应方法（以及可选的 configure / debug_view / stats），
参考 src/basic/algorithms/ 中的 dfs.py、flood_fill.py、wall_follower.py、bfs.py；
需要按规则代价规划的算法用 core.planning（KnownWalls、heading_search、cost_lower_bound，本文件已转出）。
写法与检查清单见 src/ext/README.md。

本文件属于公共接口层（src/core/）：基础规则与扩展共用，修改时必须保持向后兼容，
并通过 tests/test_basic/test_regression.py（基础规则结果不变）。
"""

import importlib
import inspect
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Protocol

from core.environment import ContactObservation, Cell, Direction, Maze, MazeEnvironment, Observation
from core.planning import KnownWalls, SearchResult, cost_lower_bound, heading_search
from core.rules import BASIC, Ruleset

__all__ = [
    "Cell", "Edge", "Direction", "Maze", "MazeEnvironment", "Observation",
    "DELTAS", "OPPOSITE", "ORDER", "EXPLORE", "KNOWN_MAP",
    "turn_left", "turn_right", "step_cell", "inside", "direction_between",
    "maze_walls", "has_wall", "open_neighbours",
    "ExplorationStrategy", "KnownMapPlanner",
    "AlgorithmInfo", "discover_algorithms", "load_algorithm",
    "Snapshot", "Runner", "run_episode", "Ruleset", "BASIC",
    "KnownWalls", "SearchResult", "cost_lower_bound", "heading_search",
]

SRC = Path(__file__).resolve().parents[1]  # src/
# 自动发现扫描的算法包：(层, 包名)。基础规则在前，扩展在后；同名算法以先发现的为准并报错。
ALGORITHM_PACKAGES = (("basic", "basic.algorithms"), ("ext", "ext.algorithms"))
Edge = frozenset  # 两个相邻格组成的 frozenset，表示它们之间的一面墙

# ====================================================================== 1. 共用工具

DELTAS = {Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
          Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0)}
OPPOSITE = {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}
ORDER = tuple(Direction)  # N、E、S、W，同时也是顺时针顺序

EXPLORE = "explore"      # 未知地图探索
KNOWN_MAP = "known_map"  # 已知地图规划


def turn_left(heading: Direction) -> Direction:
    """朝向左转 90° 后的绝对方向。"""
    return ORDER[(ORDER.index(heading) - 1) % 4]


def turn_right(heading: Direction) -> Direction:
    """朝向右转 90° 后的绝对方向。"""
    return ORDER[(ORDER.index(heading) + 1) % 4]


def step_cell(cell: Cell, direction: Direction) -> Cell:
    """从 cell 沿 direction 走一格后的格子（不检查边界和墙）。"""
    dx, dy = DELTAS[direction]
    return (cell[0] + dx, cell[1] + dy)


def inside(cell: Cell, width: int, height: int) -> bool:
    """格子是否在 width × height 的地图范围内。"""
    return 0 <= cell[0] < width and 0 <= cell[1] < height


def direction_between(a: Cell, b: Cell) -> Direction:
    """从格子 a 走到相邻格子 b 的方向。

    Raises:
        ValueError: 两格不相邻。
    """
    for direction in ORDER:
        if step_cell(a, direction) == tuple(b):
            return direction
    raise ValueError(f"{a} and {b} are not adjacent")


def maze_walls(maze: Maze) -> frozenset[Edge]:
    """返回迷宫的全部内部墙（真值）。

    只有已知地图规划器、驱动统计和可视化可以使用；未知地图探索策略不得调用。
    """
    return maze.walls


def has_wall(maze: Maze, a: Cell, b: Cell) -> bool:
    """真值地图中两个相邻格之间是否有墙（仅限已知地图规划器使用）。"""
    return frozenset((tuple(a), tuple(b))) in maze_walls(maze)


def open_neighbours(maze: Maze, cell: Cell):
    """按 N/E/S/W 顺序生成真值地图中可以走到的 (方向, 邻格)（仅限已知地图规划器使用）。"""
    for direction in ORDER:
        neighbour = step_cell(cell, direction)
        if inside(neighbour, maze.width, maze.height) and not has_wall(maze, cell, neighbour):
            yield direction, neighbour


# ====================================================================== 2. 算法接口

class ExplorationStrategy(Protocol):
    """未知地图探索策略（mode = EXPLORE，默认）。与 src/README.md 的 Strategy 接口一致。

    必须实现：
        name: str                      唯一名称，显示在上位机和结果中
        reset(width, height, start, goals, initial_heading, seed) -> None
        choose_direction(observation) -> Direction | None   None 表示声明无路（no_path）
    可选实现：
        debug_view() -> dict           供上位机显示内部状态，格式见 tools/MazesTest/README.md
        stats() -> dict                额外指标（如 replans、expanded_nodes），每次决策后读取并并入运行统计；
                                       expanded_nodes 会写入实验 runs.csv
        configure(rule) -> None        每次 reset 前收到当前规则（core.rules.Ruleset）
    可选类属性：
        designed_for = ("turn_cost",)  为哪些规则层设计（层 key）；只用于界面标记与实验分组，不限制运行
        supported_rules = {...}        支持哪些改变观测的层；未声明时这类层拒绝运行
    """

    name: str

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清除上一轮状态。"""

    def choose_direction(self, observation: Observation) -> Direction | None:
        """返回下一步的绝对方向。"""


class KnownMapPlanner(Protocol):
    """已知地图规划器（mode = KNOWN_MAP）。一次拿到完整地图，返回整条路径。

    必须实现：
        name: str
        mode = KNOWN_MAP
        plan(maze) -> list[Cell] | None   从起点到某个目标的格子序列（含起点），无路时返回 None
    可选实现：
        debug_view() -> dict           例如搜索过的格子、距离
        stats() -> dict                额外指标，例如扩展节点数，会并入运行统计
    驱动会把路径交给环境逐格执行，步数、转向等统计与探索算法同口径；
    规划耗时计入 compute_seconds。读取地图请用本文件的 open_neighbours / has_wall。
    """

    name: str
    mode: str

    def plan(self, maze: Maze) -> list[Cell] | None:
        """返回从起点到目标的路径。"""


# ====================================================================== 3. 自动发现

@dataclass(frozen=True)
class AlgorithmInfo:
    """一个可用算法的登记信息。

    layer：所在层，"basic"（基础规则，冻结）或 "ext"（扩展）。
    ablation_of：消融变体所属的完整算法名（类属性 ablation_of）；非空时不进主图，只进消融图。
    ablation_baseline：完整算法的消融基线算法名（类属性 ablation_baseline）。
    supported_rules：声明支持的改变观测的层（类属性）；None 表示未声明。
    designed_for：为哪些规则层设计（类属性，层 key）；只用于界面标记和实验分组，不限制运行。
    """
    name: str
    module: str
    class_name: str
    mode: str = EXPLORE
    doc: str = ""
    layer: str = "basic"
    ablation_of: str = ""
    ablation_baseline: str = ""
    supported_rules: frozenset[str] | None = None
    designed_for: frozenset[str] = frozenset()

    def designed_for_rule(self, rule: Ruleset) -> bool:
        """算法是否为 rule 中叠加的某一层设计（基础规则下总为 False）。"""
        return any(layer.key in self.designed_for for layer in rule.layers)

    def create(self):
        """新建一个算法对象（每次运行使用独立对象）。"""
        return getattr(importlib.import_module(self.module), self.class_name)()


def algorithm_mode(obj) -> str | None:
    """判断一个类属于哪类算法；不是算法时返回 None。

    规则：类名不以下划线开头、name 为非空字符串；mode 为 KNOWN_MAP 时需实现 plan，
    否则需实现 reset 和 choose_direction。
    """
    if not inspect.isclass(obj) or obj.__name__.startswith("_"):
        return None
    name = getattr(obj, "name", None)
    if not isinstance(name, str) or not name:
        return None
    mode = getattr(obj, "mode", EXPLORE)
    if mode == KNOWN_MAP:
        return KNOWN_MAP if callable(getattr(obj, "plan", None)) else None
    if callable(getattr(obj, "reset", None)) and callable(getattr(obj, "choose_direction", None)):
        return EXPLORE
    return None


def discover_algorithms(*, mode: str | None = None, layer: str | None = None
                        ) -> tuple[dict[str, AlgorithmInfo], list[str]]:
    """扫描 ALGORITHM_PACKAGES（src/basic/algorithms/、src/ext/algorithms/）中的模块，找出所有算法类。

    组员新增算法文件后无需修改任何其他文件，重新启动上位机即可出现在列表中。

    Args:
        mode: 只返回某一类（EXPLORE 或 KNOWN_MAP）；None 时返回全部。
        layer: 只返回某一层（"basic" 或 "ext"）；None 时返回全部。

    Returns:
        (按名称排序的 {name: AlgorithmInfo}, 导入失败或重名的错误信息列表)。
        单个文件出错不影响其他算法。
    """
    found, errors = {}, []
    for pkg_layer, package in ALGORITHM_PACKAGES:
        if layer is not None and pkg_layer != layer:
            continue
        folder = SRC.joinpath(*package.split("."))
        for path in sorted(folder.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            module_name = f"{package}.{path.stem}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:  # 组员代码有错误时不影响其他算法
                errors.append(f"{path.relative_to(SRC)}: {type(exc).__name__}: {exc}")
                continue
            for obj in vars(module).values():
                if inspect.isclass(obj) and obj.__module__ != module_name:
                    continue  # 跳过从别处导入的类
                obj_mode = algorithm_mode(obj)
                if not obj_mode or (mode is not None and obj_mode != mode):
                    continue
                if obj.name in found:
                    errors.append(f"{path.relative_to(SRC)}: 算法名 {obj.name!r} 与 "
                                  f"{found[obj.name].module} 重复，已忽略")
                    continue
                doc = (inspect.getdoc(obj) or "").splitlines()
                supported = getattr(obj, "supported_rules", None)
                found[obj.name] = AlgorithmInfo(
                    obj.name, module_name, obj.__name__, obj_mode, doc[0] if doc else "",
                    pkg_layer, getattr(obj, "ablation_of", ""), getattr(obj, "ablation_baseline", ""),
                    frozenset(supported) if supported is not None else None,
                    frozenset(getattr(obj, "designed_for", ())))
    return dict(sorted(found.items())), errors


def load_algorithm(spec: str):
    """按名称创建算法对象。

    Args:
        spec: 算法名（如 "flood_fill"、"bfs"），或 "模块名:类名"（如 "basic.algorithms.dfs:DfsStrategy"）。

    Raises:
        ValueError: 找不到该算法。
    """
    if ":" in spec:
        module_name, _, class_name = spec.partition(":")
        return getattr(importlib.import_module(module_name), class_name)()
    algorithms, _ = discover_algorithms()
    if spec not in algorithms:
        raise ValueError(f"unknown algorithm {spec!r}; available: {', '.join(algorithms)}")
    return algorithms[spec].create()


# ====================================================================== 4. 驱动

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
        observed_walls: 已知的真实墙；探索算法为已观测到的墙，已知地图算法为全部墙。
        new_walls: 本次移动后新观测到的墙，用于高亮"被墙挡住"的瞬间。
        blocked: 策略试图穿墙时的 (格子, 方向)，否则为 None。
        replanned: 预测路线是否因新信息而改变（算法提供 plan 时才有意义）。
        debug: 算法 debug_view() 的返回值，可能为 None。
        stats: 实时统计，键与 MazeEnvironment.summary() 一致，另含 decisions、visited_cells、
            coverage、observed_walls，以及算法 stats() 提供的额外指标。
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


class _PlannedRoute:
    """把已知地图规划器包装成"逐步给出方向"的形式，让 Runner 用同一套流程驱动。"""

    def __init__(self, planner, maze: Maze):
        """记录规划器和地图；真正的规划在 reset 中进行（计入计算时间）。"""
        self.planner = planner
        self.maze = maze
        self.name = planner.name

    def reset(self, **_kwargs) -> None:
        """调用规划器得到路径，并检查路径从起点出发、逐格相邻。

        Raises:
            ValueError: 规划器返回的路径不合法。
        """
        path = self.planner.plan(self.maze)
        self._remaining: list[Cell] | None = None
        self._next: Cell | None = None
        if path is None:
            return
        path = [tuple(cell) for cell in path]
        if not path or path[0] != self.maze.start:
            raise ValueError(f"{self.name}: path must start at {self.maze.start}")
        for a, b in zip(path, path[1:]):
            direction_between(a, b)  # 不相邻时抛出 ValueError
        self._remaining = path[1:]

    def choose_direction(self, observation: Observation) -> Direction | None:
        """沿规划路径给出下一步；规划器声明无路或路径已走完时返回 None。"""
        if not self._remaining:
            self._next = None
            return None
        self._next = self._remaining.pop(0)
        return direction_between(observation.position, self._next)

    def debug_view(self) -> dict:
        """规划器自己的调试信息，加上剩余路线（从下一格开始）。"""
        view = getattr(self.planner, "debug_view", None)
        debug = dict(view()) if callable(view) else {}
        route = ([self._next] if self._next else []) + (self._remaining or [])
        debug["plan"] = [list(cell) for cell in route]
        return debug

    def stats(self) -> dict:
        """规划器提供的额外指标。"""
        stats = getattr(self.planner, "stats", None)
        return dict(stats()) if callable(stats) else {}


class Runner:
    """把一个算法（任意一类）放进 MazeEnvironment 中逐步运行。

    用法：
        runner = Runner(maze, load_algorithm("flood_fill"), seed=1)
        while not runner.finished:
            snapshot = runner.step()

    规则与 src/README.md 的调用示例一致：只累计算法 reset / plan / choose_direction 的耗时，
    超过 time_budget 记为 timeout；返回 None 记为 no_path（策略的 loop_detected 为真时记为 loop_detected）；抛出异常记为 error。
    debug_view() 不计时。
    """

    def __init__(self, maze: Maze, algorithm, *, seed: int | None = None,
                 max_steps: int | None = None, time_budget: float = 30.0, rule: Ruleset = BASIC):
        """创建环境并完成第一次 reset。

        rule 为比赛规则（core.rules）；默认基础规则，此时行为与 basic-rules-v1 完全相同。
        算法若实现 configure(rule)，会在每次 reset 前收到当前规则。

        Args:
            maze: 真值迷宫。探索算法拿不到它；已知地图规划器通过 plan(maze) 拿到。
            algorithm: 探索策略或已知地图规划器对象。
            seed: 传给探索策略的随机种子。
            max_steps: 移动预算；None 时使用环境默认值 20 × 格子数。
            time_budget: 算法累计计算时间上限（秒），超过记为 timeout。
        """
        self.maze = maze
        self.algorithm = algorithm
        self.mode = KNOWN_MAP if getattr(algorithm, "mode", EXPLORE) == KNOWN_MAP else EXPLORE
        self.strategy = _PlannedRoute(algorithm, maze) if self.mode == KNOWN_MAP else algorithm
        self.seed = seed
        self.time_budget = time_budget
        self.rule = rule
        self.name = getattr(algorithm, "name", type(algorithm).__name__)
        if not rule.supports(algorithm):
            raise ValueError(f"{self.name} does not support rule {rule.key}")
        self.env = rule.make_env(maze, max_steps)
        self.reset()

    # -- 状态 -------------------------------------------------------------
    @property
    def finished(self) -> bool:
        """运行是否已经结束（成功、无路、超预算、超时、非法动作或异常）。"""
        return self.env.status != "running"

    @property
    def debug(self) -> dict | None:
        """算法最近一次 debug_view() 的结果。"""
        return self._debug

    def reset(self) -> Snapshot:
        """回到起点、重新初始化算法（已知地图规划器在此规划），返回初始快照。"""
        self.error: str | None = None
        self.compute_seconds = 0.0
        self._decisions = 0
        self._debug = None
        self._plan: list[Cell] | None = None
        self._extra_stats: dict = {}
        self._meter = self.rule.new_meter(self.maze.start_heading)  # 规则代价的增量计价器
        observation = self.env.reset()
        self._observation = observation
        if self.mode == KNOWN_MAP:
            self._observed: set[Edge] = set(maze_walls(self.maze))  # 地图完全已知
            new_walls = frozenset()
        else:
            self._observed = set()
            new_walls = self._record_walls(observation)
        try:
            configure = getattr(self.algorithm, "configure", None)
            if configure is not None:
                configure(self.rule)
            started = perf_counter()
            self.strategy.reset(
                width=self.maze.width, height=self.maze.height, start=self.maze.start,
                goals=frozenset(self.maze.goals), initial_heading=self.maze.start_heading,
                seed=self.seed)
            self.compute_seconds += perf_counter() - started
            self._read_stats()
            if self.mode == KNOWN_MAP:
                self._update_debug()
        except Exception:
            self._fail()
        self._last = self._snapshot(moved=False, new_walls=new_walls,
                                    blocked=None, replanned=False)
        return self._last

    def snapshot(self) -> Snapshot:
        """返回最近一次的快照（不推进）。"""
        return self._last

    def summary(self) -> dict:
        """返回环境统计结果，compute_seconds 为本运行器测得的算法耗时。"""
        summary = self.env.summary(compute_seconds=self.compute_seconds)
        if self._meter is not None:  # 基础规则没有计价器，结果字段与 basic-rules-v1 完全相同
            summary["rule_cost"] = self._meter.total
        return summary

    # -- 推进 -------------------------------------------------------------
    def step(self) -> Snapshot:
        """让算法做一次决策并执行；运行已结束时直接返回最后的快照。"""
        if self.finished:
            return self._last
        moved, new_walls, blocked, replanned = False, frozenset(), None, False
        try:
            started = perf_counter()
            direction = self.strategy.choose_direction(self._observation)
            self.compute_seconds += perf_counter() - started
            self._decisions += 1
            replanned = self._update_debug()
            if self.mode == EXPLORE:
                self._read_stats()

            if self.compute_seconds > self.time_budget:
                self.env.finish("timeout")
            elif direction is None:
                # 策略可设 loop_detected = True，说明是判定陷入循环而不是确认无路
                self.env.finish("loop_detected" if getattr(self.strategy, "loop_detected", False)
                                else "no_path")
            else:
                result = self.env.step(direction)
                moved = result.moved
                self._observation = result.observation
                if result.collided and self.rule.collision_limit != 1:
                    # 接触证据优先于外层传感器包装产生的噪声。
                    obs = result.observation
                    self._observation = ContactObservation(obs.position, obs.heading, obs.walls | {direction},
                                                           obs.step_count, direction)
                if self._meter is not None and (moved or (result.collided and self.rule.collision_limit != 1)):
                    self._meter.add(direction, moved=moved)
                if result.collided:
                    blocked = (self.env.position, direction)
                if self.mode == EXPLORE and (moved or result.collided):
                    new_walls = self._record_walls(self._observation)
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
        """算法抛出异常：保存异常信息并按实验规则记为 error。"""
        self.error = traceback.format_exc(limit=4)
        if not self.finished:
            self.env.finish("error")

    def _read_stats(self) -> None:
        """读取算法 stats() 的额外指标（不计时）；没有实现时为空。"""
        stats = getattr(self.strategy, "stats", None)
        self._extra_stats = dict(stats()) if callable(stats) else {}

    def _record_walls(self, observation: Observation) -> frozenset[Edge]:
        """把当前格观测到的内部墙加入已观测集合，返回其中新出现的墙。"""
        new = set()
        for direction in observation.walls:
            neighbour = step_cell(observation.position, direction)
            if inside(neighbour, self.maze.width, self.maze.height):
                wall = frozenset((observation.position, neighbour))
                if wall not in self._observed:
                    new.add(wall)
        self._observed |= new
        return frozenset(new)

    def _update_debug(self) -> bool:
        """读取算法的 debug_view()，返回预测路线是否发生了非顺延的改变。"""
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
                     observed_walls=len(self._observed), **self._extra_stats)
        return Snapshot(self._decisions, env.position, env.heading, env.status, moved,
                        tuple(env.path), visited, frozenset(self._observed),
                        frozenset(new_walls), blocked, replanned, self._debug, stats)


def run_episode(maze: Maze, algorithm, *, seed: int | None = None,
                max_steps: int | None = None, time_budget: float = 30.0, rule: Ruleset = BASIC) -> dict:
    """把一个算法完整运行一次，返回统计结果（供批量实验使用）。

    Returns:
        MazeEnvironment.summary() 的全部字段，另含 algorithm、mode、maze_id、seed、error
        以及算法 stats() 的额外指标。
    """
    runner = Runner(maze, algorithm, seed=seed, max_steps=max_steps, time_budget=time_budget, rule=rule)
    runner.run()
    return {**runner.summary(), **runner._extra_stats, "algorithm": runner.name,
            "mode": runner.mode, "maze_id": maze.maze_id, "seed": seed, "error": runner.error}
