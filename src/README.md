# 代码目录与统一接口

本文件是环境、探索策略和实验执行器之间的第一版接口约定。A2、B、C、D
模块均按此约定接入；需要修改公共字段或计数规则时，先在任务 Issue 中说明影响，
再同步修改调用方和本文件。

下文的 Strategy 接口固定未知迷宫探索的公共规则。已知完整地图的 BFS、Dijkstra、A* 属于独立实验模式，
不直接读取本接口中的未知迷宫状态，其接口见“统一接口文件 algorithm_api.py”一节。

## 文件职责

代码目录保持扁平，每个算法使用一个文件：

| 文件 | 责任 |
| --- | --- |
| `environment.py` | 地图读取与验证、真值墙壁、观测、移动、访问及转向统计 |
| `algorithm_api.py` | **统一接口**：共用方向工具、两类算法接口、自动发现、逐步驱动 `Runner` 与 `run_episode`（已实现） |
| `dfs.py` | DFS＋实际移动回溯（已实现） |
| `greedy_dfs.py` | 贪心 DFS：只把 DFS 的邻格顺序改为离目标近的优先，用于消融对比（已实现） |
| `flood_fill.py` | 在线地图、距离传播与动作选择（已实现） |
| `repeated_astar.py` | 乐观地图上按需重新规划的 A*，与 Flood-Fill 对比计算量（已实现） |
| `wall_follower.py` | 左手／右手沿墙策略及循环终止（已实现） |
| `random_walk.py` | 随机游走，下界基线，使用种子（已实现） |
| `bfs.py` | 已知地图 BFS 最短路，独立实验模式的参照（已实现） |
| `astar.py` | 已知地图 A* 最短路（曼哈顿启发式），并提供通用 `astar_search`（已实现） |
| `frontier.py`（可选） | 前沿选择与已知通路导航 |
| `prior_astar.py` | 本组提出的先验增强重复 A*（柱子规则推断墙 + 自适应未知边惩罚）及 3 个消融变体（C1/C2，已实现） |
| `run_experiments.py` | 批量实验：统一预算、地图输入、批量运行，导出 CSV、汇总、元数据与图表（`--plot` 可只从 CSV 重画）；命令行与上位机共用（已实现） |

实验执行器通过统一策略接口注册算法，不写死算法数量。随机策略必须接收并记录种子。

## 统一接口文件 algorithm_api.py

算法文件**只写算法**；方向工具、算法的发现、运行和统计都由 `algorithm_api.py` 负责。上位机
（`tools/MazesTest`）、批量实验和测试都调用它，规则只有一份。

**新增算法的步骤**：在 `src/` 中新建一个文件，写一个类，设置唯一的 `name`，按类别实现下面的方法。
共用工具（`DELTAS`、`OPPOSITE`、`turn_left`、`step_cell` 等）从 `algorithm_api` 导入，不要各自重写。
不需要修改任何其他文件：上位机重启后自动发现，探索算法出现在“实时运行”和“同屏对比”页，
已知地图算法出现在“已知地图规划”页。类名以下划线开头的内部基类不会被发现。

| 类别 | `mode` | 必须实现 | 可选实现 | 能看到什么 |
| --- | --- | --- | --- | --- |
| 未知地图探索 | `EXPLORE`（默认，可不写） | `reset`、`choose_direction`（即下文的 Strategy 接口，未改变） | `debug_view` | 只有每步的 `Observation` |
| 已知地图规划 | `KNOWN_MAP` | `plan(maze) -> list[Cell] \| None` | `debug_view`、`stats` | 完整地图（用 `open_neighbours`、`has_wall` 读取） |

**已知地图规划器（新增接口，待组内确认）**：`plan` 返回从起点到目标的格子序列（含起点），无路时返回
`None`。驱动先检查路径从起点出发且逐格相邻，再交给环境逐格执行，因此步数、转向等统计与探索算法同口径；
规划耗时计入 `compute_seconds`；`stats()` 返回的额外指标（如 BFS 的 `expanded_nodes`）并入结果。
两类算法按 README 约定分开比较。

**驱动**：`Runner(maze, algorithm, seed=..., max_steps=..., time_budget=...)` 逐步运行并生成快照，
供上位机显示；`run_episode(...)` 一次跑完并返回统计字典，`run_experiments.py` 应直接使用它，
不要另写一套运行规则。两者的计时、预算和终止状态都按下文“调用示例”的规则执行。

## 坐标、方向与单元格

- 单元格坐标统一为整数二元组 `(x, y)`。
- 左下角是 `(0, 0)`；向东移动时 `x` 加一，向北移动时 `y` 加一。
- 宽为 `width`、高为 `height` 时，合法范围为
  `0 <= x < width`、`0 <= y < height`。
- 绝对方向统一使用字符串枚举 `N`、`E`、`S`、`W`，分别表示北、东、南、西。
- 对应位移为 `N: (0, 1)`、`E: (1, 0)`、`S: (0, -1)`、`W: (-1, 0)`。
- 迷宫外边界始终是墙，不在地图文件中重复列出。

建议在 `environment.py` 中提供下列公共类型；算法应导入这些类型，不各自定义另一套方向：

```python
from enum import Enum

Cell = tuple[int, int]


class Direction(str, Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
```

## 迷宫 JSON 格式

仓库内统一使用 JSON 作为内部地图格式。外部迷宫集合必须先转换并验证，算法不负责
解析第三方格式。示例：

```json
{
  "maze_id": "dev_4x4_01",
  "width": 4,
  "height": 4,
  "start": [0, 0],
  "start_heading": "N",
  "goals": [[1, 1]],
  "blocked_edges": [
    [[0, 0], [1, 0]],
    [[1, 0], [1, 1]]
  ],
  "metadata": {
    "source": "handmade",
    "seed": null,
    "notes": "用于小地图调试"
  }
}
```

字段约定：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `maze_id` | `str` | 地图唯一标识，进入实验结果 CSV |
| `width`、`height` | `int` | 正整数网格尺寸 |
| `start` | `[int, int]` | 起始单元格 |
| `start_heading` | `N/E/S/W` | 起始朝向 |
| `goals` | `list[[int, int]]` | 一个或多个目标格，到达任意一个即成功 |
| `blocked_edges` | `list[[cell, cell]]` | 两个相邻格之间的内部墙 |
| `metadata` | `object` | 来源、随机种子和说明，不参与策略决策 |

`blocked_edges` 中每条边是无向的，`[a, b]` 与 `[b, a]` 表示同一面墙，文件中只能保留
一次。加载器至少验证：

1. 所有坐标均在地图范围内；
2. 起点合法且目标列表非空；
3. 墙两端的曼哈顿距离恰好为一；
4. 不存在重复墙或反向重复墙；
5. `maze_id`、尺寸、方向及字段类型合法。

16×16 主实验建议使用角落起点和中央 2×2 目标区，但实际起点、目标与朝向始终以
地图文件为准，不在环境中写死。

## 信息可见范围

`MazeEnvironment` 独占完整真值地图。未知迷宫策略不得接收地图对象、
`blocked_edges`、未到达格的墙壁或任何由完整真值计算出的最短路。

每次决策时，策略只获得：

- 地图宽度、高度、起点、目标和初始朝向（在 `reset` 时提供）；
- 当前坐标和当前朝向；
- 当前格四个绝对方向中的墙壁集合；
- 已执行的合法移动步数。

墙壁观测是本项目的理想传感器假设：到达一个格子后，一次得到该格四个方向的墙壁。
策略自行维护在线地图，并将相邻格共享的墙壁双向同步。未观测的内部边保持
`UNKNOWN`，不能当作已知真值；Flood-Fill 可以按其已登记的规则暂时将未知边视为可通行。

## Observation 观测结构

建议由 `environment.py` 提供不可变观测对象：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    position: Cell
    heading: Direction
    walls: frozenset[Direction]
    step_count: int
```

例如：

```python
Observation(
    position=(0, 0),
    heading=Direction.NORTH,
    walls=frozenset({Direction.SOUTH, Direction.WEST}),
    step_count=0,
)
```

表示电脑鼠位于左下角、朝北，南侧和西侧有墙，尚未跨格移动。观测中不提供全局访问
记录；需要访问标记的策略自行维护，环境另行维护一份只用于统一指标统计的访问记录。

## Strategy 统一接口

每个未知迷宫策略提供唯一 `name`，并实现相同的初始化和单步决策接口：

```python
from typing import Protocol


class Strategy(Protocol):
    name: str

    def reset(
        self,
        *,
        width: int,
        height: int,
        start: Cell,
        goals: frozenset[Cell],
        initial_heading: Direction,
        seed: int | None = None,
    ) -> None:
        """清除上一轮状态，并初始化该策略自己的未知地图。"""

    def choose_direction(self, observation: Observation) -> Direction | None:
        """返回下一次移动的绝对方向；确认无法继续时返回 None。"""
```

规则：

- 返回值是绝对方向，不是左转、右转等相对动作；环境统一换算转弯次数。
- 策略每次只能决定跨向一个相邻格，不能一次返回整条路径让电脑鼠瞬移。
- DFS 回溯也必须逐格返回并调用相同接口，回溯移动计入步数。
- `None` 表示策略根据自身已知信息声明无法继续，运行状态记为 `no_path`；若策略返回 `None` 前把
  属性 `loop_detected` 设为 `True`（例如沿墙法判定陷入循环），则记为 `loop_detected`。
- 策略不得修改传入的观测，也不得通过私有属性引用环境或真值地图。
- `reset` 后同一个策略对象可以安全地用于下一张地图或下一次重复实验。

## Environment 环境接口

A2 至少实现以下行为；具体类内部结构可以调整，但公开语义保持一致：

```python
env = MazeEnvironment(maze, max_steps=20 * maze.width * maze.height)
observation = env.reset()
step_result = env.step(direction)
```

建议的单步结果：

```python
@dataclass(frozen=True)
class StepResult:
    observation: Observation
    status: str
    moved: bool
```

`reset()` 将位置与朝向恢复到地图起点，清空计数，路径初始化为 `[start]`，并返回起点
观测。起点算第一次访问，但不算重复访问，也不计移动步数。

`step(direction)` 按以下顺序执行：

1. 检查运行是否已经终止及方向类型是否合法；
2. 检查当前观测已知的墙壁和地图边界；
3. 对合法移动计算转弯、更新朝向并跨入相邻格；
4. 更新步数、访问次数、路径和新位置观测；
5. 先判断是否到达目标，再判断是否用完移动预算。

策略返回非法类型、越界方向或尝试穿过已观测墙壁时，本轮记为 `invalid_action` 并立即
终止；该动作不增加移动步数、转弯数或路径。环境不得静默忽略错误或替策略选择其他方向。

## 运行与终止状态

统一使用以下状态字符串：

| 状态 | 含义 |
| --- | --- |
| `running` | 尚未结束 |
| `success` | 到达任意目标格 |
| `no_path` | 策略返回 `None`，声明无法继续 |
| `loop_detected` | 策略返回 `None` 且 `loop_detected` 为真：判定陷入循环（目标可能可达，只是该策略到不了） |
| `budget_exceeded` | 达到移动预算仍未到达目标 |
| `timeout` | 累计策略计算时间超过统一预算 |
| `invalid_action` | 非法方向、越界或尝试穿墙 |
| `error` | 策略或环境出现未处理异常 |

默认移动预算为 `20 × width × height`，默认策略计算预算为每次运行累计 30 秒。
最终实验可以通过配置修改，但同一实验中的所有算法必须使用相同预算并记录配置。

若一次合法移动同时到达目标并用完移动预算，优先记为 `success`。`no_path` 只是算法基于
当前知识的判断，不等同于证明真值地图无解。异常应记录类型与简短原因，不能将失败样本
从结果中删除。

## 统一统计指标

环境和实验执行器统一生成以下结果：

| 指标 | 统计规则 |
| --- | --- |
| `status` | 上表中的最终状态 |
| `steps` | 成功执行的跨格移动次数；非法动作不计步 |
| `repeat_visits` | 每次进入此前访问过的格子加一；起点首次出现不计 |
| `turns_90` | 90° 等效转向次数：直行 0、左/右转 1、掉头 2 |
| `compute_seconds` | 策略 `reset` 与所有 `choose_direction` 的累计墙钟时间 |
| `path` | 从起点开始的实际位置序列，长度应为 `steps + 1` |
| `peak_memory_bytes` | 按实验计划指定工具测得的峰值；说明测量范围 |

计时不包括地图文件读取、环境移动检查、绘图和结果写盘。为降低计时与内存测量互相干扰，
两者可以分轮执行，但必须使用相同地图、参数、种子和算法版本。失败运行保留状态和原因；
不存在的成功路径指标留空，不用零代替。

## 调用示例

下面展示执行器与策略的最小交互；A2/D2 实现时可封装成函数，但语义保持一致：

```python
from time import perf_counter

env = MazeEnvironment(maze, max_steps=20 * maze.width * maze.height)
strategy = DfsStrategy()

started = perf_counter()
strategy.reset(
    width=maze.width,
    height=maze.height,
    start=maze.start,
    goals=frozenset(maze.goals),
    initial_heading=maze.start_heading,
    seed=42,
)
compute_seconds = perf_counter() - started

observation = env.reset()
while env.status == "running":
    started = perf_counter()
    direction = strategy.choose_direction(observation)
    compute_seconds += perf_counter() - started

    if compute_seconds > 30.0:
        env.finish("timeout")
        break
    if direction is None:
        env.finish("loop_detected" if getattr(strategy, "loop_detected", False) else "no_path")
        break

    result = env.step(direction)
    observation = result.observation

summary = env.summary(compute_seconds=compute_seconds)
```

`finish`、`summary` 的内部实现由 A2/D2 决定，但不得改变上述状态和指标含义。批量实验还需
记录 `maze_id`、算法名、配置 ID、运行编号、随机种子、实验模式、代码提交和失败原因。

## 接入检查清单

新环境或算法接入时至少确认：

- [ ] 策略只能通过 `Observation` 获得墙壁，不读取真值地图；
- [ ] 不同记录使用相同坐标、方向、预算和目标定义；
- [ ] DFS 回溯为真实移动，路径长度等于 `steps + 1`；
- [ ] 墙壁在策略在线地图中双向同步；
- [ ] 死路、环路、非法动作和预算终止不会造成无限循环；
- [ ] 失败运行及原因会进入原始结果；
- [ ] 随机策略保存种子，运行可以复现；
- [ ] 已知地图规划和未知地图探索使用不同实验模式与结果表。

本接口完成组内审阅后，A2 实现 `environment.py`，B/C 模块实现策略，D 模块实现批量执行
与结果输出。实现发现接口缺项时更新本文件，并在对应 Issue 中记录理由和受影响模块。
