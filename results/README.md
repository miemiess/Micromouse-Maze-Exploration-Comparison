# 实验结果

结果由 `src/run_experiments.py`（命令行）或上位机“批量实验”页生成，规则见 [`Docs/experiment-plan.md`](../Docs/experiment-plan.md)。不要添加虚构数据，也不要把参考仓库的成绩当成本组结果。

## 目录

| 目录 | 内容 |
| --- | --- |
| `standard/main/` | 实验 1（主对比）：514 张地图 × 13 个算法（含 C2 新方案 `prior_astar` 及 3 个消融变体），每组合重复 3 次；`figures/ablation.png` 为 C2 消融图 |
| `standard/randomness/` | 实验 2（随机性）：随机游走在 3 张核心迷宫上用种子 0～9 |
| `standard/dev/` | C2 开发集（种子 101～110 的 120 张生成地图，不属于任何实验）的调参记录 `tuning.md` 与复现脚本 `tune_dev.py` |
| `demo/` | 演示用图片与 GIF（`Docs/demo-guide.md`） |
| `batch-<时间>/` | 上位机自选实验（按需生成） |

## 每个实验目录的文件

| 文件 | 内容 |
| --- | --- |
| `runs.csv` | 原始数据，每次运行一行 |
| `summary.csv`、`summary.md` | 按（地图组, 算法）汇总，`ALL` 为全部地图 |
| `metadata.json` | 代码提交号、Python 版本、平台、预算、计时范围、开始与结束时间 |
| `figures/*.png` | 图表，可用 `python src/run_experiments.py --plot <目录>` 从 CSV 重新生成 |

## runs.csv 字段

`run_id`、`experiment`、`maze_id`、`map_group`、`algorithm`、`experiment_mode`（unknown_exploration / known_map_planning）、`config_id`、`seed`、`status`、`steps`、`shortest`、`ratio`、`turns_90`、`repeat_visits`、`visited_cells`、`coverage`、`compute_ms`、`compute_ms_min`、`repeats`、`consistent`、`expanded_nodes`、`peak_memory_bytes`、`error`。

- 失败的运行保留状态与原因；`ratio` 等只与成功路径有关的指标留空，不填 0。
- 计时只含算法自身，不含读图、绘图、动画与写盘；随机方法记录种子。
- 未知地图探索与已知地图规划（参照）分开统计，不混排。
- 创新方案的消融变体用不同的 `config_id` 区分；开发集与测试集分开（见实验计划第 3 节）。
