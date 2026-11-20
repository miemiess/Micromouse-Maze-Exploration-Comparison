# 扩展阶段结果

扩展规则下的正式结果放在这里，每个规则或实验一个子目录（例如 `turn_cost/main/`），由 `src/ext/plan.py` 中注册的计划生成：

```bash
python src/run_experiments.py --plan <名称>
```

每个目录的文件格式与 `results/basic/` 相同（`runs.csv`、`summary.*`、`metadata.json`、`figures/`），`metadata.json` 另外记录规则与参数。实验计划与开发 / 测试划分见 [`Docs/ext/dev-plan.md`](../../Docs/ext/dev-plan.md)。

目前尚无结果。
