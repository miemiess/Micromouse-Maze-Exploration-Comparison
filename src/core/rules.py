"""规则层的公共接口：规则 = 基础规则 + 若干叠加层（公共接口层，与具体规则无关）。

基础规则（BASIC）没有叠加层：每步代价 1、转向只计数、理想观测、到达目标即结束。
扩展规则在基础规则上叠加“层”，每层属于一个维度，同一维度最多一层：
    - cost（代价模型）：如转弯代价、运动时间模型（src/ext/rules/turn_cost.py、motion_time.py）；
    - observation（观测模型）：如传感器噪声（src/ext/rules/noisy_sensor.py，会改变观测，只对声明支持的算法开放）；
    - contact（撞墙处理）：撞墙后是否继续、累计几次终止（src/ext/rules/collision.py）；
    - flow（比赛流程）：如两阶段探索 + 冲刺（规划中）。
层通过两个钩子影响运行：env_options() 返回创建 MazeEnvironment 的关键字参数（按维度顺序合并，后者覆盖前者），
wrap_env(env) 包装环境（观测层在这里加噪声）。
具体的层写在 src/ext/rules/ 的模块里，模块中的 LAYERS 列表会被 available_layers() 自动发现，
本模块不导入任何具体规则，因此基础规则不依赖扩展层。

代价模型采用“走—停—转”假设：电脑鼠沿直线连续前进，只在改变方向时停下原地转向。
一条路线因此拆成若干直线段和转向，总代价 = Σ run_cost(段长) + Σ turn_cost(90° 转向次数)；
同一套拆分既用于给实际路线计价（Ruleset.cost），也用于求规则下的最优路线（Ruleset.optimal_plan）。

基础规则保证：不叠加任何层时，Runner / run_episode / 实验框架的结果与 basic-rules-v1 完全相同
（tests/test_basic/test_regression.py）。
"""

import importlib
from collections.abc import Iterable
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import ClassVar

from core.environment import Cell, Direction, Maze
from core.planning import DELTAS, heading_search, maze_blocked, quarter_turns

SRC = Path(__file__).resolve().parents[1]
LAYER_PACKAGE = "ext.rules"   # 自动发现叠加层的包：每个模块定义 LAYERS = [层类, ...]
DIMENSIONS = {"cost": "代价模型", "observation": "观测模型", "contact": "撞墙处理", "flow": "比赛流程"}

__all__ = ["DIMENSIONS", "RuleLayer", "CostLayer", "CostMeter", "Ruleset", "BASIC", "BASIC_COLOR",
           "quarter_turns", "segments", "turn_points", "available_layers", "parse_rule", "preset_rules"]


def _direction(a: Cell, b: Cell) -> Direction:
    """相邻格 a → b 的方向。"""
    delta = (b[0] - a[0], b[1] - a[1])
    return next(d for d, v in DELTAS.items() if v == delta)


def segments(path: Iterable[Cell], start_heading: Direction) -> list[tuple[int, int]]:
    """把实际路线拆成 [(转向次数, 直线段格数), ...]。

    每段先原地转向（第一段相对初始朝向），再沿直线走若干格；同方向的连续移动合并为一段。
    转向次数之和等于环境统计的 turns_90，段长之和等于 steps。
    """
    cells = [tuple(c) for c in path]
    result: list[tuple[int, int]] = []
    heading = start_heading
    for a, b in zip(cells, cells[1:]):
        move = _direction(a, b)
        if result and move == heading:
            turns, length = result[-1]
            result[-1] = (turns, length + 1)
        else:
            result.append((quarter_turns(heading, move), 1))
        heading = move
    return result


def turn_points(path: Iterable[Cell], start_heading: Direction) -> list[tuple[Cell, int]]:
    """路线上发生转向的格子及转向次数 [(格子, 1 或 2), ...]，供界面标记转弯点。"""
    cells = [tuple(c) for c in path]
    points, heading = [], start_heading
    for a, b in zip(cells, cells[1:]):
        move = _direction(a, b)
        if move != heading:
            points.append((a, quarter_turns(heading, move)))
        heading = move
    return points


# ====================================================================== 叠加层

@dataclass(frozen=True)
class RuleLayer:
    """叠加在基础规则上的一层修改。子类用类属性描述自己，用 dataclass 字段声明参数。

    类属性：
        key：唯一标识（命令行与 metadata 使用，如 "turn_cost"）；
        title：界面名称（如 "转弯代价"）；
        dimension：所属维度，DIMENSIONS 的键之一；
        color：界面中代表这一层的颜色（横幅、标签、转弯点）；
        summary：一句话说明规则改了什么（界面横幅显示）；
        changes_observation：是否改变观测（改变观测的层只对声明支持它的算法开放）。
    """
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""
    dimension: ClassVar[str] = ""
    color: ClassVar[str] = "#6c757d"
    summary: ClassVar[str] = ""
    changes_observation: ClassVar[bool] = False
    # 参数的界面名称与单位：{字段名: (名称, 单位)}；未列出的字段直接显示字段名。
    param_labels: ClassVar[dict[str, tuple[str, str]]] = {}
    # 界面标签里显示的参数（None 表示全部）；完整参数见 param_text(full=True)。
    label_params: ClassVar[tuple[str, ...] | None] = None
    # 参数的取值范围（上位机输入框使用）：{字段名: (最小, 最大)}；未列出时为 0～100。
    # 默认值为 inf 的字段在界面上用最小值表示“不限”。
    param_ranges: ClassVar[dict[str, tuple[float, float]]] = {}

    def params(self) -> dict:
        """参数字典（写入 metadata）。"""
        return asdict(self)

    def param_text(self, full: bool = False) -> str:
        """参数文字，如 "λ = 1"；full 为 False 时只含 label_params；没有参数时为空字符串。"""
        parts = []
        for f in fields(self):
            if not full and self.label_params is not None and f.name not in self.label_params:
                continue
            name, unit = self.param_labels.get(f.name, (f.name, ""))
            value = getattr(self, f.name)
            parts.append(f"{name} = 不限" if value == float("inf") else f"{name} = {value:g}{unit}")
        return "，".join(parts)

    def label(self) -> str:
        """界面标签，如 "转弯代价（λ = 1.0）"。"""
        text = self.param_text()
        return f"{self.title}（{text}）" if text else self.title

    def env_options(self) -> dict:
        """创建 MazeEnvironment 时的关键字参数（如 collision_limit）；默认无。"""
        return {}

    def wrap_env(self, env):
        """改变环境行为的层在这里包装环境（观测、流程层使用）；默认不改。

        需要随机数的包装读取 env.seed（Runner 的种子，可能为 None），以保证可复现。
        """
        return env


@dataclass(frozen=True)
class CostLayer(RuleLayer):
    """代价模型层：给“直线段”和“原地转向”定价（走—停—转假设）。"""
    dimension: ClassVar[str] = "cost"
    unit: ClassVar[str] = ""          # 代价单位，如 "s"；空字符串表示无量纲
    formula: ClassVar[str] = ""       # 代价公式（界面显示）

    def run_cost(self, cells: int) -> float:
        """沿直线连续走 cells 格的代价。"""
        raise NotImplementedError

    def turn_cost(self, quarters: int) -> float:
        """原地转 quarters 个 90°（1 或 2）的代价。"""
        raise NotImplementedError


class _UnitCost(CostLayer):
    """基础规则的代价：每步 1，转向不计代价（不对外注册，只用于基础规则的最优路线计算）。"""
    key = "unit"

    def run_cost(self, cells: int) -> float:
        return float(cells)

    def turn_cost(self, quarters: int) -> float:
        return 0.0


_UNIT = _UnitCost()


class CostMeter:
    """按“走—停—转”假设增量计价：每次移动 O(1)，供 Runner 在运行中实时显示规则代价。

    total = 已结束的直线段与转向的代价 + 当前直线段（尚未结束）的代价。
    """

    def __init__(self, layer: CostLayer, start_heading: Direction):
        self.layer = layer
        self.heading = start_heading
        self._closed = 0.0      # 已结束的直线段与全部转向的代价
        self._run = 0           # 当前直线段的格数

    def add(self, move: Direction, *, moved: bool = True) -> None:
        """记录一次朝 move 方向的动作：先原地转向（方向改变时），moved 为真时再前进一格。

        moved 为假表示撞墙（撞墙处理层允许继续时）：只计转向，并结束当前直线段。
        """
        if moved and self._run and move == self.heading:
            self._run += 1
            return
        if self._run:
            self._closed += self.layer.run_cost(self._run)
        turns = quarter_turns(self.heading, move)
        if turns:
            self._closed += self.layer.turn_cost(turns)
        self.heading, self._run = move, int(moved)

    @property
    def total(self) -> float:
        return round(self._closed + (self.layer.run_cost(self._run) if self._run else 0.0), 6)


# ====================================================================== 规则

@dataclass(frozen=True)
class Ruleset:
    """一套比赛规则：基础规则 + 叠加层（每个维度最多一层）。不可变，可比较、可哈希。"""
    layers: tuple[RuleLayer, ...] = ()

    def __post_init__(self):
        dims = [layer.dimension for layer in self.layers]
        duplicated = {d for d in dims if dims.count(d) > 1}
        if duplicated:
            raise ValueError(f"每个维度最多叠加一层：{', '.join(sorted(duplicated))}")
        unknown = set(dims) - set(DIMENSIONS)
        if unknown:
            raise ValueError(f"未知的规则维度：{', '.join(sorted(unknown))}")
        # 按维度固定顺序排列，使相同组合得到相同的 key
        order = list(DIMENSIONS)
        object.__setattr__(self, "layers", tuple(sorted(self.layers, key=lambda l: order.index(l.dimension))))

    # -- 描述 --------------------------------------------------------------
    @property
    def is_basic(self) -> bool:
        return not self.layers

    @property
    def key(self) -> str:
        """唯一标识：基础规则为 "basic"，否则为各层 key 用 "+" 连接。"""
        return "+".join(layer.key for layer in self.layers) or "basic"

    @property
    def spec(self) -> str:
        """可复现的写法（parse_rule 能还原），如 "basic"、"turn_cost:weight=2"。"""
        if self.is_basic:
            return "basic"
        parts = []
        for layer in self.layers:
            args = ",".join(f"{f.name}={getattr(layer, f.name):g}" for f in fields(layer))
            parts.append(f"{layer.key}:{args}" if args else layer.key)
        return "+".join(parts)

    @property
    def title(self) -> str:
        """界面标题，如 "基础规则" 或 "基础规则 + 转弯代价（λ = 1.0）"。"""
        return " + ".join(["基础规则", *(layer.label() for layer in self.layers)])

    @property
    def color(self) -> str:
        """代表这套规则的颜色：基础规则为中性灰，否则为第一层的颜色。"""
        return self.layers[0].color if self.layers else BASIC_COLOR

    @property
    def cost_layer(self) -> CostLayer | None:
        return next((l for l in self.layers if isinstance(l, CostLayer)), None)

    @property
    def cost_model(self) -> CostLayer:
        """规划用的代价模型：有代价层时为该层，基础规则为单位代价（每步 1、转向 0）。

        算法在 configure(rule) 中取它交给 core.planning.heading_search，基础规则下也能运行。
        """
        return self.cost_layer or _UNIT

    @property
    def env_options(self) -> dict:
        """各层 env_options() 按维度顺序合并的环境参数（后面的维度覆盖前面的）。"""
        options: dict = {}
        for layer in self.layers:
            options.update(layer.env_options())
        return options

    @property
    def collision_limit(self) -> int | None:
        """累计撞墙几次终止：1 为基础规则（首次撞墙即 invalid_action），None 为不限次数。"""
        return self.env_options.get("collision_limit", 1)

    @property
    def changes_observation(self) -> bool:
        return any(layer.changes_observation for layer in self.layers)

    def layer(self, dimension: str) -> RuleLayer | None:
        """某个维度上叠加的层；没有时返回 None。"""
        return next((l for l in self.layers if l.dimension == dimension), None)

    def with_layer(self, layer: RuleLayer | None, dimension: str | None = None) -> "Ruleset":
        """替换（或用 None 移除）某个维度上的层，返回新规则。"""
        dim = layer.dimension if layer is not None else dimension
        kept = [l for l in self.layers if l.dimension != dim]
        return Ruleset(tuple(kept + ([layer] if layer is not None else [])))

    def metadata(self) -> dict:
        """写入 metadata.json 的规则描述。"""
        return {"key": self.key, "spec": self.spec, "title": self.title,
                "collision_limit": self.collision_limit,
                "layers": [{"key": l.key, "dimension": l.dimension, "params": l.params()}
                           for l in self.layers]}

    # -- 运行 --------------------------------------------------------------
    def make_env(self, maze: Maze, max_steps: int | None, seed: int | None = None):
        """创建环境：用合并后的 env_options 创建基础环境，再依次经过各层的 wrap_env。"""
        from core.environment import MazeEnvironment
        env = MazeEnvironment(maze, max_steps=max_steps, seed=seed, **self.env_options)
        for layer in self.layers:
            env = layer.wrap_env(env)
        return env

    def supports(self, algorithm) -> bool:
        """算法（对象或 AlgorithmInfo）能否在本规则下运行。

        不改变观测的层对所有算法开放（算法可以不理会代价，只是代价会被如实计算）；
        改变观测的层只对 supported_rules 中列出该层 key 的算法开放；
        已知地图规划器（mode = "known_map"）不使用观测，不受观测层限制。
        """
        if getattr(algorithm, "mode", "explore") == "known_map":
            return True
        declared = getattr(algorithm, "supported_rules", None)
        return all(not layer.changes_observation or (declared is not None and layer.key in declared)
                   for layer in self.layers)

    # -- 代价 --------------------------------------------------------------
    def new_meter(self, start_heading: Direction) -> CostMeter | None:
        """新建增量计价器；没有代价层（基础规则）时返回 None。"""
        layer = self.cost_layer
        return CostMeter(layer, start_heading) if layer is not None else None

    def cost(self, path: Iterable[Cell], start_heading: Direction) -> float | None:
        """按本规则的代价模型给一条实际路线计价；没有代价层（基础规则）时返回 None。"""
        meter = self.new_meter(start_heading)
        if meter is None:
            return None
        cells = [tuple(c) for c in path]
        for a, b in zip(cells, cells[1:]):
            meter.add(_direction(a, b))
        return meter.total

    def optimal_plan(self, maze: Maze) -> tuple[float, list[Cell]] | None:
        """已知完整地图时，本规则代价最小的路线（含起点）及其代价；不可达时返回 None。

        用 core.planning.heading_search 在（格子, 朝向）上做 Dijkstra：原地转 1 或 2 个 90°，
        或沿当前朝向直走 k 格（中途不能穿墙）。基础规则用单位代价，结果长度等于 BFS 最短路。
        """
        result = heading_search(maze.start, maze.start_heading, maze.goals,
                                maze_blocked(maze.width, maze.height, maze.walls), self.cost_model)
        return (result.cost, result.route) if result.found else None

    def optimal_cost(self, maze: Maze) -> float | None:
        """optimal_plan 的代价部分。"""
        plan = self.optimal_plan(maze)
        return plan[0] if plan else None


BASIC = Ruleset()
BASIC_COLOR = "#6c757d"


# ====================================================================== 注册与解析

def available_layers() -> dict[str, type[RuleLayer]]:
    """自动发现 src/ext/rules/ 中各模块 LAYERS 列出的层类：{key: 层类}。"""
    found: dict[str, type[RuleLayer]] = {}
    folder = SRC.joinpath(*LAYER_PACKAGE.split("."))
    for path in sorted(folder.glob("*.py")):
        if path.stem.startswith("_"):
            continue
        module = importlib.import_module(f"{LAYER_PACKAGE}.{path.stem}")
        for cls in getattr(module, "LAYERS", []):
            if cls.key in found:
                raise ValueError(f"规则层 key 重复：{cls.key}")
            found[cls.key] = cls
    return found


def parse_rule(spec: str) -> Ruleset:
    """把命令行写法解析为规则。

    写法：``basic``；``turn_cost``；``turn_cost:weight=2``；多层用 "+" 连接，
    如 ``turn_cost:weight=0.5+noisy_sensor+collision:limit=3``（每个维度最多一层）。
    参数值 ``unlimited`` / ``inf`` 表示不限。
    """
    spec = spec.strip()
    if spec in ("", "basic"):
        return BASIC
    layers_by_key = available_layers()
    layers = []
    for part in spec.split("+"):
        key, _, args = part.partition(":")
        if key not in layers_by_key:
            raise ValueError(f"unknown rule layer {key!r}; available: basic, {', '.join(layers_by_key)}")
        cls = layers_by_key[key]
        kwargs = {}
        types = {f.name: f.type for f in fields(cls)}
        for item in filter(None, args.split(",")):
            name, _, value = item.partition("=")
            if name not in types:
                raise ValueError(f"layer {key!r} has no parameter {name!r}; parameters: {', '.join(types)}")
            kwargs[name] = float("inf") if value in ("unlimited", "inf") else float(value)
        layers.append(cls(**kwargs))
    return Ruleset(tuple(layers))


def preset_rules() -> dict[str, Ruleset]:
    """常用规则：基础规则 + 每个已发现的层（默认参数）各一套。键为 Ruleset.key。"""
    rules = {"basic": BASIC}
    for cls in available_layers().values():
        rule = Ruleset((cls(),))
        rules[rule.key] = rule
    return rules
