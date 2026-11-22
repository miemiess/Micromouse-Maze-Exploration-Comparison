# 扩展层（ext）

**状态：开发中。** 在基础规则之上放宽假设（转弯代价、运动时间、两阶段比赛、传感器噪声），并加入启发式搜索与近似算法。路线图、任务与验收标准见 [`Docs/ext/dev-plan.md`](../../Docs/ext/dev-plan.md)。

## 放什么

| 目录 / 文件 | 内容 | 状态 |
| --- | --- | --- |
| `rules/` | 叠加层（`core.rules.RuleLayer` 子类，模块中列入 `LAYERS` 即被自动发现）：代价模型、观测模型、比赛流程 | 已有 `turn_cost.py`（转弯代价，E1）、`motion_time.py`（运动时间模型，E1） |
| `algorithms/` | 为扩展规则编写的算法，每个算法一个文件；自动发现扫描本目录。共用的搜索与已知墙在 `core/planning.py` | 已有 `rule_optimal.py`（已知地图上的规则最优参照）；E3 探索策略：`turn_aware_astar`、`turn_aware_astar_w2`、`dstar_lite`、`frontier`。后两项按步数选路，在代价叠加层中也可按相同规则评价 |
| `plan.py` | 扩展实验计划，定义 `PLANS = {名称: (构建函数, "ext/<名称>")}` | 待建 |

## 接入规则（人和 AI 都按这里做）

1. **只依赖公共接口**：从 `core.algorithm_api`、`core.environment`、`core.experiments` 导入；需要复用基础算法时从 `basic.algorithms.<模块>` 导入，不复制代码。
2. **不修改基础层**：不改 `src/basic/` 的行为。公共接口层 `src/core/` 可以扩展，但必须向后兼容（默认参数保持基础规则），并通过 `tests/test_basic/test_regression.py`。
3. **算法**：新建 `algorithms/<名称>.py`，类设置唯一 `name`（与已有算法重名会被拒绝），按 `src/README.md` 的接口实现；上位机重启后自动出现，带 `[EXT]` 标记。
4. **实验先写计划**：在 `Docs/ext/` 写好实验计划（问题、地图、开发 / 测试划分、参数候选与选取标准）后再运行；带参数的方法只在开发集上调参，开发集按地图来源分层。
5. **结果**：写到 `results/ext/<规则或实验名>/`；`metadata.json` 记录规则与参数。
6. **测试**：放在 `tests/test_ext/`，文件名以 `test_` 开头。扩展算法会自动进入
   `tests/test_ext/test_planning.py` 的接入检查：在每套预置规则下、几张固定地图上必须成功到达且规则代价口径一致。

## 写一个懂规则的探索算法（E3 起）

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
