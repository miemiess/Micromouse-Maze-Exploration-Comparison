# 扩展阶段结果

扩展实验按[扩展实验计划](../../Docs/ext/experiment-plan.md)运行，计划注册在 `src/ext/plan.py`。运行前可加 `--dry-run` 预览地图、种子、规则、CSV 字段和输出目录（不运行、不写文件）：

```bash
python src/run_experiments.py --plan ext_turn --dry-run
python src/run_experiments.py --plan ext_noise --dry-run
```

- `--plan ext_turn` → `results/ext/turn/<子实验>/`：`lambda_0.5`、`lambda_1`、`lambda_2`、`lambda_4`、`motion_time`，测试集 435 张地图 × 10 个探索算法，计时重复 3 次。
- `--plan ext_noise` → `results/ext/noise/<子实验>/`：`ideal`、`high`、`mid`、`low`，噪声子集 200 张地图 × 2 个算法 × 5 个种子。
- `--plan ext_two_phase` → `results/ext/two_phase/<子实验>/`：`steps`、`lambda_2`，测试集 435 张地图 × 6 个算法（到达即停 3 个、有界提前停止 3 个）。
- `difficulty/`（D4，已生成）：`features.csv`、`correlations.md`（难度特征与基础实验 1 的相关，描述性）、`adversarial_<算法>.json / .md`（模拟退火对抗迷宫，可用上位机打开）。由 `python src/ext/difficulty.py features` 与 `adversarial --algorithm <名称>` 生成。

每个子实验包含 `runs.csv`、`summary.csv`、`summary.md`、`metadata.json` 和 `figures/`，格式与 `results/basic/` 相同；规则参数、撞墙上限与地图清单记录在 `metadata.json`，字段含义见[结果说明](../README.md)。归档前可加 `--out results/local/<目录>` 先写到本地。

X1～X3 的正式结果待生成（计划确认冻结后运行）。算法实现与固定迷宫的验收示例见[扩展算法说明](../../src/ext/README.md#已实现的算法)。
