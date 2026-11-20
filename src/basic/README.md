# 基础规则层（basic）

**状态：已完成并冻结**，对应 git 标签 `basic-rules-v1`。只修 bug，不改行为；任何改变结果的修改都会被 `tests/test_basic/test_regression.py` 拦下。

**规则**：16×16 地图，起点 (0, 0) 朝北，中央 2×2 目标；每次跨格移动代价 1，转向只计数、不计入代价；理想观测（到达一格即知道该格四面墙）；移动预算 20 × 格子数，计算预算 30 秒。

| 文件 | 内容 |
| --- | --- |
| `algorithms/dfs.py`、`greedy_dfs.py` | DFS＋实际回溯；贪心 DFS（只改邻格顺序的消融对照） |
| `algorithms/flood_fill.py` | Flood-Fill：乐观未知边，每步全量 BFS 重算 |
| `algorithms/repeated_astar.py` | 重复 A*：乐观地图上按需重新规划（基础规则下推荐的算法） |
| `algorithms/wall_follower.py` | 左手 / 右手沿墙法，判定循环时记为 `loop_detected` |
| `algorithms/random_walk.py` | 随机游走（下界基线，带种子） |
| `algorithms/bfs.py`、`astar.py` | 已知地图参照（BFS 最短路、A*；`astar.py` 还提供通用 `astar_search`） |
| `algorithms/prior_astar.py` | 本组新方案：先验增强重复 A* 及 3 个消融变体（C1/C2） |
| `plan.py` | 实验计划：实验 1（514 张 × 13 个算法）、实验 2（随机性）；`--plan basic` |
| `dev_tuning.py` | C2 开发集（种子 101～110）调参 → `results/basic/dev/tuning.md` |
| `posthoc_stratified.py` | 事后分析：按来源分层的开发集 → `results/basic/dev/posthoc.md`（不是正式结论） |

文档：实验计划 `Docs/basic/experiment-plan.md`，算法登记 `Docs/basic/algorithm-methods.md`，新方案设计 `Docs/basic/algorithm-design.md`，报告 `Docs/Result.md` 第 1、2、4 章。结果：`results/basic/`。

复现：

```bash
python src/run_experiments.py --plan basic     # 实验 1、2（约 8 分钟）
python src/basic/dev_tuning.py                 # 开发集调参记录
python src/basic/posthoc_stratified.py         # 事后分析
```
