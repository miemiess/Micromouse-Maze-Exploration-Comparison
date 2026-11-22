# E3-1：懂规则的重复 A*（turn_aware_astar）

| 项 | 内容 |
| --- | --- |
| 状态 | 已完成 |
| 负责人 | zhouying682 |
| 依赖 | E0、E1（已完成）；`src/core/planning.py`（已完成） |
| 预计工作量 | 1 个算法文件（约 100 行）+ 文件头说明；验收测试已写好 |
| 验收测试 | `tests/test_ext/test_turn_aware_astar.py`（算法文件建立前自动跳过） |

开始前先读根目录 `AGENTS.md`。

## 1. 背景（为什么做）

基础阶段最好的探索算法是**重复 A***（`src/basic/algorithms/repeated_astar.py`）：把没看到过的墙当作不存在（乐观假设），从当前位置用 A* 规划到终点，被新发现的墙挡住时才重新规划。但它只数步数，不管转了几次弯。

扩展阶段加了**转弯代价**（代价 = 步数 + λ × 90° 转向次数）和**运动时间模型**（直道加减速 + 转向用时）。本任务写重复 A* 的“懂规则”版本：搜索时按当前规则的代价规划，而不是按步数。之后的实验要回答：在未知地图上，“按规则代价规划”是否真的比“只数步数”的重复 A* 代价更低？（初步试跑发现不一定，见 §6。）

## 2. 要做什么

新建 **`src/ext/algorithms/turn_aware_astar.py`**，包含两个类：

| 类 | `name` | 加权 A* 的 w | 说明 |
| --- | --- | --- | --- |
| `TurnAwareAStarStrategy` | `turn_aware_astar` | 1.0 | 主算法：每次规划都是当前已知地图上的规则最优 |
| `WeightedTurnAwareAStarStrategy` | `turn_aware_astar_w2` | 2.0 | 加权变体：f = g + 2·h，规划更快，单次规划代价 ≤ 2 倍最优 |

两个类都要：

- `designed_for = ("turn_cost", "motion_time")`；文档字符串第一行一句话说明。
- `configure(rule)`：保存 `rule.cost_model`（基础规则下是单位代价）。**同一个对象会先后在不同规则下运行**，每次都要用最新的规则。
- `reset(...)`：清空所有状态（已知墙、计划、计数器）。
- `choose_direction(observation)`：
  1. 用 `KnownWalls.observe` 记录新墙；
  2. 已经走到计划的下一格时把它从计划里去掉；
  3. 没有计划，或剩余计划被已知墙挡住（`KnownWalls.route_blocked`）时，调用 `heading_search` 重新规划：起点是当前格和**当前朝向**（`observation.heading`），`blocked=已知墙.blocked`，代价模型是 `cost_model`，启发式是 `cost_lower_bound`，`weight` 用表中的 w；
  4. 找不到路时返回 `None`；否则返回去计划下一格的方向。
- `stats()`：返回 `{"replans": 规划次数, "expanded_nodes": 累计扩展状态数}`（`expanded_nodes` 会写入实验结果表）。
- `debug_view()`：返回 `{"known_walls": 已知墙.debug_walls(), "plan": 剩余计划的格子列表}`，上位机用它画图。

`src/ext/README.md` 里“写一个懂规则的探索算法”的示例 `TurnAwareReplanner` 已经是 w = 1 版本的骨架，可以直接照着改。注意：类名、`name` 要按上表改，加上 `replans`、`weight`、`debug_view`；示例本身不要以 `turn_aware_replanner` 的名字提交。

文件头按 `AGENTS.md` 第 6 条写：思路、信息假设（只用观测）、决策规则、复杂度、随机性（无）。并说明与 `repeated_astar` 的关系：基础规则下两者都是乐观重规划，但本算法的状态里有朝向，同代价时的选路可能不同，路线不保证一样。

## 3. 允许修改的文件

- 新建：`src/ext/algorithms/turn_aware_astar.py`
- 追加一行：`Docs/log.txt`
- 更新本文件的“状态 / 负责人 / 完成记录”，以及根目录 `README.md` 任务表 E3 那一行的状态

**不要改**：`src/core/`、`src/basic/`、任何已有测试（包括验收测试）。觉得公共接口不够用，写进下面的“问题记录”，停下来问负责人。

## 4. 验收标准

1. `python -m unittest tests.test_ext.test_turn_aware_astar`：7 个测试全部通过，**不能有 skipped**（有 skipped 说明文件名或位置不对）。验收测试检查：
   - 两个算法被自动发现，属于扩展层、探索类，`designed_for` 正确；
   - 源码中没有读取真值地图的工具；
   - 无墙地图上：w = 1 的代价等于规则最优，w = 2 不超过 2 倍，都只规划一次；
   - 5 张固定地图、4 套规则（基础、λ = 2、λ = 0、运动时间）下都到达目标；
   - `stats()` 的两个字段合理，重复运行路线相同；
   - 同一个对象换规则后重新运行，用的是新规则；
   - `debug_view()` 提供 `known_walls` 和 `plan`。
2. `python -m unittest discover -s tests`：全部 `OK`（含基础规则回归测试与扩展算法接入检查）。
3. 上位机里选中“基础规则 + 转弯代价”时，两个新算法在算法列表中以规则颜色加粗显示，实时运行能画出计划路线（人工看一眼即可，不强制）。

## 5. 不在本任务范围

- 不调 λ、w，不跑正式实验、不写结果（这些在实验计划写好之后另开任务）。
- 不做 D* Lite、前沿探索（后续任务）。

## 6. 参考信息

- 负责人用同样思路的试跑（λ = 2）：uk2011f 上规则代价 261，比重复 A* 的 311 好；1stworld 上 253，反而比重复 A* 的 221 差。乐观假设下按转弯代价规划会被误导，这正是后续实验要研究的现象，**不需要在本任务里“修好”**。
- 接口细节：`src/core/planning.py` 的文档字符串；规则接口：`src/core/rules.py`。

## 问题记录

（实现中遇到的疑问、与本说明不一致的地方写在这里。）

## 完成记录

- 新增 `src/ext/algorithms/turn_aware_astar.py`，更新本任务、README 的 E3 状态与 Docs/log.txt。
- 专项：Ran 7 tests in 0.969s，OK，无跳过。全量：Ran 113 tests in 16.875s，OK。
- 两种权重在 5 张固定地图、4 套规则下均到达目标；无墙验收地图上均只规划一次。
- 按任务范围完成；界面数据经自动测试验证，未人工检查配色。
