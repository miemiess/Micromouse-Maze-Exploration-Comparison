# 实验结果

正式结果按规则层分区：基础规则在 `basic/`（冻结），扩展在 `ext/`。结果由 `python src/run_experiments.py --plan <名称>` 生成，规则见各层的实验计划。不要添加虚构数据，也不要把参考仓库的成绩当成本组结果。

## 目录

| 目录 | 内容 |
| --- | --- |
| `basic/main/` | 基础规则实验 1（主对比）：514 张地图 × 13 个算法（含 C2 新方案 `prior_astar` 及 3 个消融变体），每组合重复 3 次；`figures/ablation_prior_astar.png` 为 C2 消融图。计划：[`Docs/basic/experiment-plan.md`](../Docs/basic/experiment-plan.md) |
| `basic/randomness/` | 基础规则实验 2（随机性）：随机游走在 3 张核心迷宫上用种子 0～9 |
| `basic/dev/` | C2 开发集（种子 101～110，不属于任何实验）：调参记录 `tuning.md`（`src/basic/dev_tuning.py`）；事后分析 `posthoc.md`（`src/basic/posthoc_stratified.py`，看过测试结果后做的，不是正式结论） |
| `basic/demo/` | 基础规则演示图片与 GIF（[`Docs/demo-guide.md`](../Docs/demo-guide.md)） |
| `ext/` | 扩展阶段的正式结果，按规则或实验分子目录（见 [`ext/README.md`](ext/README.md)） |
| `local/` | 自选实验、上位机批量实验与导出图片的默认位置；**不提交**（`.gitignore`） |

## 每个实验目录的文件

| 文件 | 内容 |
| --- | --- |
| `runs.csv` | 每个地图、算法和种子组合一行。多次重复的计算耗时取中位数，`consistent` 记录行为是否一致 |
| `summary.csv`、`summary.md` | 按（地图组, 算法）汇总，`ALL` 为全部地图 |
| `metadata.json` | 代码提交号、运行环境、预算和计时范围。当前导出还记录 `rule.spec`、`rule.collision_limit` 与 `algorithm_info` |
| `figures/*.png` | 图表，可用 `python src/run_experiments.py --plot <目录>` 从 CSV 重新生成 |

## runs.csv 字段

`run_id`、`experiment`、`maze_id`、`map_group`、`algorithm`、`experiment_mode`（unknown_exploration / known_map_planning）、`config_id`、`seed`、`status`、`steps`、`shortest`、`ratio`、`turns_90`、`repeat_visits`、`visited_cells`、`coverage`、`compute_ms`、`compute_ms_min`、`repeats`、`consistent`、`expanded_nodes`、`peak_memory_bytes`、`error`。

- 有代价层时，追加 `rule`、`rule_cost`、`optimal_rule_cost`、`rule_cost_ratio`。参数以 `metadata.json` 中的 `rule.spec` 为准。
- 上位机批量实验、扩展计划和开启碰撞恢复的实验导出 `actions` 与 `collisions`。命令行自选实验可加 `--collision-stats` 统一导出口径。汇总包含平均动作数、平均碰撞数和至少撞墙一次的运行比例。碰撞上限为 `null` 表示不限次数。
- 基础结果的元数据记录了原始运行时的版本 `4e768cb+dirty`。复现时建议用 `--out` 输出到独立目录，便于比较原始产物与新产物。
- 失败的运行保留状态与原因；`ratio` 等只与成功路径有关的指标留空，不填 0。
- 计时只含算法自身，不含读图、绘图、动画与写盘；随机方法记录种子。
- 未知地图探索与已知地图规划（参照）分开统计，不混排。
- 消融变体由算法类属性 `ablation_of` 声明，不进主图，自动画入 `ablation_<算法名>.png`；开发集与测试集分开（见各层实验计划）。
