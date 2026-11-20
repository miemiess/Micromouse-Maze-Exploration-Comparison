# 实验计划（D1）

本计划在实验运行**之前**确定规则，运行后不根据结果修改；如需修改，在本文末尾“变更记录”中写明原因，并重新运行全部实验。所有实验都用项目自己的仿真（`src/algorithm_api.py` 的统一驱动）完成，上位机“批量实验”页与命令行运行的是同一套代码。

## 1. 要回答的问题（对应课程要求）

| # | 问题 | 对应课程交付项 | 用到的结果 |
| --- | --- | --- | --- |
| Q1 | 在同样的迷宫和规则下，各探索算法走了多少步、比已知地图最短路多走多少？ | 实验评估、算法选择理由 | 实验 1：步数 / 最短路 |
| Q2 | 哪些算法会失败，失败在什么样的迷宫上？ | 实验评估、局限 | 实验 1：成功率（按地图组） |
| Q3 | 迷宫结构（生成方式、环路多少）如何影响算法表现？ | 算法选择理由、局限 | 实验 1：按地图组对比 |
| Q4 | 移动成本与计算成本是否一致？算法要算多久？ | 复杂度分析 | 实验 1：计算时间 |
| Q5 | 已知地图时，启发式（A*）比 BFS 少搜多少？ | 复杂度分析、启发式 | 实验 1：扩展节点数 |
| Q6 | 随机算法的结果波动有多大？ | 实验评估的可靠性 | 实验 2：随机游走多种子 |
| Q7 | 本组提出的先验增强重复 A* 是否比重复 A* 少走路？每个机制各贡献多少？ | 算法设计、启发式、实验评估 | 实验 1：新方案与消融变体（调参只用开发集，见第 4 节） |

## 2. 实验一览

| 实验 | 地图 | 算法 | 种子 | 重复 | 输出目录 |
| --- | --- | --- | --- | --- | --- |
| 实验 1：主对比 | 外部迷宫库 394 张 + 计划生成地图 120 张 = 514 张 | 全部 13 个（第 4 节） | 0 | 3 次（计时取中位数） | `results/standard/main/` |
| 实验 2：随机性 | 核心比赛迷宫 3 张（1stworld、japan2017ef、uk2011f） | 随机游走 | 0～9 | 1 次 | `results/standard/randomness/` |

Q3 不需要单独的实验：实验 1 的结果按“地图组”拆开统计即可。

## 3. 地图

全部地图在 `mazes/classic/`（来源见 `mazes/README.md`）。

| 地图组 | 数量 | 说明 |
| --- | --- | --- |
| `external` | 394 | 外部迷宫库（`external_*`，来自 micromouse_maze_tool）：以历届比赛迷宫为主，另含少量上游提供的测试 / 练习图（如 `external_empty`、`external_8x8-practice`）；16×16，中央 2×2 目标 |
| `backtracker_loop0/10/30` | 各 10 | 递归回溯生成，环路比例 0% / 10% / 30%，种子 1～10（文件名见下方命名规范） |
| `wilson_loop0/10/30` | 各 10 | Wilson（无偏）生成，同上 |
| `prim_loop0/10/30` | 各 10 | 随机 Prim 生成，同上 |
| `kruskal_loop0/10/30` | 各 10 | 随机 Kruskal 生成，同上 |

- **命名规范**：外部地图为 `external_<上游文件名>`；生成地图统一为 `gen_<生成算法>_<宽>x<高>_s<种子>[_l<环路百分比>]`，例如 `gen_backtracker_16x16_s1`、`gen_wilson_16x16_s3_l10`；地图组为 `external` 或 `<生成算法>_loop<环路百分比>`。
- 生成地图全部为 16×16、起点 (0,0) 朝北、中央 2×2 目标。“loop0”指生成树本身无环；生成后会拆掉中央 2×2 目标区内部的墙（与比赛迷宫一致），因此目标区内有一个小环。生成命令（同名文件会跳过）：
  `python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 1 10`
- **开发集**：目前没有需要调参的算法，上述 514 张全部作为测试集。以后 C2 新方案需要调参时，只能使用种子 **101～110** 生成的地图作为开发集，调好后冻结参数，再在上述测试集上评估。
- 地图库中其他地图（手工编辑、临时生成的）不进入标准实验。

## 4. 算法

| 类别 | 算法 |
| --- | --- |
| 未知地图探索（参与比较） | `dfs`、`greedy_dfs`、`flood_fill`、`repeated_astar`、`wall_follower_left`、`wall_follower_right`、`random_walk` |
| 已知地图规划（只作参照，不参与排名） | `bfs`、`astar` |
| 未知地图探索：本组新方案（C2，参与比较） | `prior_astar`（完整版） |
| 未知地图探索：新方案的消融变体（只用于消融分析，不进主图） | `prior_astar_no_post`（去掉柱子规则）、`prior_astar_no_penalty`（去掉未知边惩罚）、`prior_astar_fixed`（自适应惩罚换成固定 δ）；基线为 `repeated_astar` |

算法规则与复杂度见 `Docs/algorithm-methods.md`；新方案的设计见 `Docs/algorithm-design.md`。

**C2 新方案的调参与冻结**（在看测试集结果之前确定）：

- 只调一个参数：自适应惩罚系数 c（候选 0.5、1、1.5、2、2.5、3、4、5）；固定 δ 的消融变体另调 δ（候选 0、0.25、0.5、0.75、1、1.5、2、2.5、3）。
- 选取标准：开发集 120 张地图上“步数 / 最短路”的**均值**最低；相差不到 0.001 时取较小的值。
- 结果：c = 2.5，固定 δ = 2.5，写入 `src/prior_astar.py` 的 `FROZEN_SCALE`、`FROZEN_FIXED` 后冻结；测试集结果出来后不再修改。
- 柱子规则没有可调参数，规则本身来自比赛规程，不来自数据。
- 新方案与消融变体和其他算法一起在实验 1 中运行（同一批地图、同一次运行、同一计时口径）；开发集只用于调参，不属于任何实验，其唯一记录是 `results/standard/dev/`（`tuning.md` 与复现脚本 `tune_dev.py`）。

## 5. 统一规则

- **移动预算**：20 × 格子数（16×16 时为 5120 步）；超出记为 `budget_exceeded`。
- **计算预算**：每次运行算法累计计算 30 秒；超出记为 `timeout`。
- **计时范围**：只计算法自身的 `reset` / `plan` / `choose_direction`；不含读图、环境检查、绘图、动画和写盘（由测试 `tests/test_experiments.py` 验证）。
- **重复**：实验 1 每个组合运行 3 次，计算时间取中位数；同时检查 3 次的路线完全相同（`consistent` 列）。
- **种子**：只影响随机算法；所有运行都记录种子。
- **失败**：保留状态和原因；只与成功路径有关的指标（`ratio`）留空，不填 0。成功率和失败原因都要报告，不能只展示成功的运行。
- **两类算法分开**：已知地图算法只作参照，汇总表和图中与探索算法分开。

## 6. 指标

| 指标 | 定义 | CSV 字段 |
| --- | --- | --- |
| 成功率 | 预算内到达目标的运行数 / 总运行数 | `status`（汇总为 `success_rate`） |
| 步数 | 实际跨格移动次数（失败的运行也记录） | `steps` |
| 步数 / 最短路 | 成功运行的步数 ÷ 已知地图 BFS 最短路长度，1 为最优 | `ratio`、`shortest` |
| 转向次数 | 90° 等效转向次数（掉头记 2） | `turns_90` |
| 重复访问 | 进入已访问格子的次数 | `repeat_visits` |
| 覆盖率 | 到过的格子数 / 总格子数 | `coverage`、`visited_cells` |
| 计算时间 | 算法计算毫秒数（重复运行的中位数与最小值） | `compute_ms`、`compute_ms_min` |
| 扩展节点 | 已知地图算法从队列中取出并扩展的格子数 | `expanded_nodes` |
| 峰值内存（可选） | tracemalloc 测得的 Python 对象峰值，另跑一轮测量，不代表进程总内存 | `peak_memory_bytes` |

每行还记录 `run_id`、`experiment`、`maze_id`、`map_group`、`algorithm`、`experiment_mode`、`config_id`、`seed`、`repeats`、`consistent`、`error`。

## 7. 输出

每个实验目录包含：

| 文件 | 内容 |
| --- | --- |
| `runs.csv` | 原始数据，每次运行一行 |
| `summary.csv` / `summary.md` | 按（地图组, 算法）汇总，另有 `ALL` 表示全部地图 |
| `metadata.json` | 代码提交号、Python 版本、平台、设置、开始与结束时间 |
| `figures/` | `ratio_by_group.png`、`success_by_group.png`、`compute_time.png`、`expanded_nodes.png`；实验 1 另有 `ablation.png`（C2 消融） |

图表随时可以从 CSV 重新生成：`python src/run_experiments.py --plot results/standard/main`。

## 8. 如何运行

**命令行（推荐用于正式结果）**：

```bash
python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 1 10
python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 101 110   # C2 开发集
python src/run_experiments.py --plan standard   # 全部实验（实验 1、2）
python results/standard/dev/tune_dev.py         # C2 开发集调参记录（不属于实验）
python results/standard/dev/posthoc_stratified.py  # 事后分析：按地图来源分层的开发集（不属于实验计划，结论不进入正式结果）
```

**上位机**：打开“▦ 批量实验”页 → 勾选地图（可用筛选框和“外部迷宫库 / 生成迷宫 / 核心 3 张”按钮）→ 勾选算法 → 设置种子、重复次数 → 点“运行并导出”。结果写入 `results/batch-<时间>/`，文件格式与命令行相同。适合做小规模或自选的实验。

## 9. 结果如何进入报告

`results/standard/main/summary.md` 与 `figures/` 是 `Docs/Result.md` 第 2 章表格和图的来源；报告中引用数据时注明来自哪个结果目录和 `metadata.json` 中的提交号。

## 变更记录

| 日期 | 变更 | 原因 |
| --- | --- | --- |
| 2026-11-19 | 初版 | — |
| 2026-11-20 | ① 地图组 `competition` 改名为 `external`，报告中称“外部迷宫库”；② 递归回溯生成地图由 `gen_16x16_*` 改名为 `gen_backtracker_16x16_*`（墙壁不变）；③ 新增终止状态 `loop_detected`，沿墙法判定循环时不再记为 `no_path`。已重新运行全部实验 | ① 该组含测试 / 练习图，不全是真实比赛迷宫；② 四种生成器命名统一；③ 区分“陷入循环”与“声明无路” |
| 2026-11-20 | C2 新方案 `prior_astar` 及 3 个消融变体加入实验 1（算法 9 → 13 个，代码中固定列出为 `MAIN_ALGORITHMS`）；开发集（种子 101～110）只用于调参，记录在 `results/standard/dev/`，不作为实验运行；消融变体不进主图，另画 `ablation.png`。已重新运行全部实验 | C1 / C2；新方案与全部算法在同一次运行中比较，计时口径一致 |
