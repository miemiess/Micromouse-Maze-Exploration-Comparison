# 扩展层（ext）

**状态：已完成。** 在基础规则之上放宽假设（转弯代价、运动时间、两阶段比赛、传感器噪声），并加入启发式搜索与近似算法。设计与完成情况见 [`Docs/ext/design.md`](../../Docs/ext/design.md)，结果见报告第 3 章与 [`results/ext/`](../../results/ext/README.md)。

## 放什么

| 目录 / 文件 | 内容 | 状态 |
| --- | --- | --- |
| `rules/` | 叠加层（`core.rules.RuleLayer` 子类，模块中列入 `LAYERS` 即被自动发现）：代价模型、观测模型、撞墙处理、比赛流程 | 已有 `turn_cost.py`（转弯代价，E1）、`motion_time.py`（运动时间模型，E1）、`noisy_sensor.py`（噪声观测，E2）、`collision.py`（撞墙处理）、`two_phase.py`（两阶段比赛，D5） |
| `algorithms/` | 为扩展规则编写的算法，每个算法一个文件；自动发现扫描本目录。共用的搜索与已知墙在 `core/planning.py` | 已有 `rule_optimal.py`（已知地图上的规则最优参照）；E3 探索策略：`turn_aware_astar`、`turn_aware_astar_w2`、`dstar_lite`、`frontier`。后两项按步数选路，在代价叠加层中也可按相同规则评价 |
| `difficulty.py` | D4：迷宫难度特征（环路、死胡同、分岔、绕路、转向）与基础结果的 Spearman 相关；模拟退火生成对抗迷宫。`python src/ext/difficulty.py features` / `adversarial --algorithm <名称>` | 已完成，结果在 `results/ext/difficulty/` |
| `plan.py` | 扩展实验计划，定义 `PLANS`：`--plan ext_turn`（转弯代价 / 运动时间）、`--plan ext_noise`（噪声）、`--plan ext_two_phase`（两阶段）；地图划分见 `mazes/splits/ext_dev.json`；规则见 `Docs/ext/experiment-plan.md`；加 `--dry-run` 只预览设置与输出目录、不运行 | 已建，计划待冻结 |
| `posthoc.py` | 事后验证（看过正式结果之后做的，不属于冻结计划）：`soft` 在开发集上为 `belief_astar_soft` 选 K 并在噪声子集上评估；`divisor` 用 X3 数据重算不同探索折算系数下的两阶段成绩（发现 12）；`contact` 去掉接触反馈并分解撞墙来源，检验置信度融合没有优势的原因（发现 11）。输出 `results/ext/posthoc/` | 已完成 · `tests/test_ext/test_posthoc.py` |

## 已实现的算法

上位机的「实时运行」和「同屏对比」使用前五种探索策略，它们都从当前格的四向观测更新自己的地图；「已知地图规划」页提供 `rule_optimal`，作为代价参照。

| 算法 | 怎样选择下一步 | 适合比较的问题 |
| --- | --- | --- |
| [turn_aware_astar](algorithms/turn_aware_astar.py) | 假设未知内部边畅通，在（格子，朝向）上按当前规则求最低代价路线。继续沿缓存路线移动，直到新发现的墙阻断剩余路线。 | 把转向或直线段用时计入规划后，实际走出的路线有何变化？ |
| [turn_aware_astar_w2](algorithms/turn_aware_astar.py) | 沿用同一代价模型与重规划条件，把搜索优先级从 `g + h` 改为 `g + 2h`。 | 加大对剩余代价估计的权重后，扩展状态数和实际移动代价如何变化？两倍代价上界仅适用于当前乐观地图上的单次规划。 |
| [dstar_lite](algorithms/dstar_lite.py) | 在乐观地图上维护到目标的单位步长距离。发现新墙后，从被阻断边的端点开始修复距离，再沿当前最短路走一步。 | 增量修复与重复 A* 全量重算的计算耗时如何？平局时两者可能选不同路线。 |
| [frontier](algorithms/frontier.py) | 从当前位置用 BFS 沿确认通路寻找最近的未访问格。同距离的候选中优先选目标格。 | 逐步扩大已探索区域，与直接朝目标乐观规划相比，覆盖率、重复访问和到达步数有何差异？ |
| [belief_astar](algorithms/belief_astar.py) | 噪声观测下用对数几率融合多次读数判断墙（撞到的墙、走过的边为确定），在乐观地图上按规则代价做朝向 A*；消融 `belief_astar_naive` 只信最近一次读数。唯一声明支持 `noisy_sensor` 的探索算法。 | 累积证据比只信最近读数能少撞几次墙、少走多少步？准确率下降时如何变化？ |
| [belief_astar_soft](algorithms/belief_astar.py) | 冻结计划之后新增的改进（报告发现 11）：与 `belief_astar` 相同，但找不到路时的兜底规划不再无视全部读数，而是给“更可能有墙”的边加代价 K · e^S（K = 0.25，开发集选定）。噪声子集上撞墙减少 20%～68%，步数相当（`results/ext/posthoc/soft.md`） | `tests/test_ext/test_noisy_sensor.py` |
| [bounded_explore_e0 / e10 / e25](algorithms/bounded_explore.py) | 两阶段比赛（D5）：先像朝向 A* 一样到达目标，再继续探索乐观最优路线上没到过的格子，直到“只走已确认通路的冲刺代价 P ≤ (1 + ε) × 乐观下界 O”时停止。由于 O ≤ 真实最优 ≤ P，停止时冲刺代价可证明不超过 (1 + ε) 倍最优。 | 多探索换更好的冲刺值不值？成绩随 ε 如何变化？与“到达即停”相比如何？ |
| [rule_optimal](algorithms/rule_optimal.py) | 读取完整地图，按同一规则计算从起点到目标的最小代价。 | 给出 `optimal_rule_cost`，用于计算实际探索代价与已知地图最优代价之比。 |

**算法下拉框分组。** 上位机按“基础算法”和“扩展算法”列出可选项。启用转弯代价或运动时间后，两种朝向 A* 会移到“为当前规则设计”组；启用噪声观测后，只有 `belief_astar` 及其变体（消融 `belief_astar_naive`、改进 `belief_astar_soft`）可选，其余探索算法置灰。D* Lite 和最近前沿仍按格数选路，运行器会按所选规则给它们的实际轨迹计价。各策略的整体性能排名有待正式对照实验。

**可复核的样例。** 在仓库根目录运行以下命令，在「已知地图规划」页选择 `rule_optimal`。这张图有“6 步、5 次直角转向”和“8 步、3 次直角转向”两条路线。λ = 2 时，较长路线的代价为 14，短路线为 16；把 λ 调到 1，两条路线的代价均为 11。

```bash
python tools/MazesTest/maze_app.py tests/test_ext/fixtures/turn_cost_tradeoff.json --rule turn_cost:weight=2
```

测试分别覆盖[朝向 A* 与加权变体](../../tests/test_ext/test_turn_aware_astar.py)、[增量距离修复与确认通路](../../tests/test_ext/test_incremental_frontier.py)和[公共搜索与规则接入](../../tests/test_ext/test_planning.py)。

## 接入规则（人和 AI 都按这里做）

1. **只依赖公共接口**：从 `core.algorithm_api`、`core.environment`、`core.experiments` 导入；需要复用基础算法时从 `basic.algorithms.<模块>` 导入，不复制代码。
2. **不修改基础层**：不改 `src/basic/` 的行为。公共接口层 `src/core/` 可以扩展，但必须向后兼容（默认参数保持基础规则），并通过 `tests/test_basic/test_regression.py`。
3. **算法**：新建 `algorithms/<名称>.py`，类设置唯一 `name`（与已有算法重名会被拒绝），按 `src/README.md` 的接口实现；上位机重启后按当前规则和算法来源分组显示。
4. **实验先写计划**：在 `Docs/ext/` 写好实验计划（问题、地图、开发 / 测试划分、参数候选与选取标准）后再运行；带参数的方法只在开发集上调参，开发集按地图来源分层。
5. **结果**：写到 `results/ext/<规则或实验名>/`；`metadata.json` 记录规则与参数。
6. **测试**：放在 `tests/test_ext/`，文件名以 `test_` 开头。扩展算法会自动进入
   `tests/test_ext/test_planning.py` 的接入检查：在每套预置规则下、几张固定地图上必须成功到达且规则代价口径一致。

## 写一个懂规则的探索算法

算法照常实现探索接口；规则从 `configure(rule)` 拿，搜索用 `core.planning`，不要自己再写一套已知墙和 Dijkstra：

```python
from core.algorithm_api import (Cell, Direction, KnownWalls, Observation, cost_lower_bound,
                                direction_between, heading_search)
from core.rules import BASIC


class TurnAwareReplanner:
    """（示例）乐观地图上按规则代价重新规划。"""
    name = "turn_aware_replanner"
    designed_for = ("turn_cost", "motion_time")   # 上位机标记 + 实验分组；不限制运行

    def configure(self, rule):          # Runner 在每次 reset 前调用；基础规则下 cost_model 为单位代价
        self.cost = rule.cost_model

    def reset(self, *, width, height, start, goals, initial_heading, seed=None):
        self.walls, self.goals, self.plan = KnownWalls(width, height), frozenset(goals), []
        self.expanded = 0
        self.cost = getattr(self, "cost", BASIC.cost_model)

    def choose_direction(self, observation: Observation) -> Direction | None:
        here = observation.position
        self.walls.observe(observation)
        if self.plan and self.plan[0] == here:
            self.plan.pop(0)
        if not self.plan or self.walls.route_blocked([here, *self.plan]):
            result = heading_search(here, observation.heading, self.goals, self.walls.blocked, self.cost,
                                    heuristic=lambda c, h: cost_lower_bound(self.cost, c, h, self.goals))
            self.expanded += result.expanded
            if not result.found:
                return None
            self.plan = result.route[1:]
        return direction_between(here, self.plan[0])

    def stats(self):                    # expanded_nodes 会写入 runs.csv
        return {"expanded_nodes": self.expanded}
```

检查清单：

- 只用观测和自己的 `KnownWalls`，不读真值地图（`maze_walls` / `open_neighbours` 只限已知地图规划器）；
- 基础规则下也能运行（`cost_model` 为单位代价），λ = 0 时应与对应的基础算法行为一致或有说明；
- 带参数的变体（如加权 A* 的 w）写成同一文件里的多个类；消融变体用 `ablation_of`；
- 新算法补一个 `tests/test_ext/test_<名称>.py`，至少覆盖固定地图 `tests/test_ext/fixtures/turn_cost_tradeoff.json`。
