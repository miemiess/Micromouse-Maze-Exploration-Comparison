# 扩展阶段结果

E1/E3 代价对照和 E2 多种子[扩展实验计划](../../Docs/ext/experiment-plan.md)已接入命令行。

```bash
python src/run_experiments.py --plan ext --dry-run
python src/run_experiments.py --plan ext-noise --dry-run
```

`--plan ext` 运行后默认生成 `baseline/`、`turn_cost/` 和 `motion_time/` 三个条件目录。三个条件使用同一批 435 张测试地图和 7 个探索策略。归档前可加 `--out results/local/ext-review` 将结果写入单独目录。

`--plan ext-noise` 默认写入 `noise/` 下的三个观测条件目录，比较置信度融合与只信最近读数的消融。启动前可用预览核对地图、种子、规则和 CSV 字段。

各条件包含 `runs.csv`、`summary.csv`、`summary.md`、`metadata.json` 和 `figures/`。参数和碰撞上限记录在元数据里，字段含义见[结果说明](../README.md)。报告用各条件自己的已知地图参照解释代价比。

当前正式结果待生成。算法实现与固定迷宫的验收示例可见[扩展算法说明](../../src/ext/README.md#已实现的算法)。
