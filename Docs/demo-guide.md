# 运行、复现与演示

本文说明如何运行上位机和命令行、复现报告中的结果，以及答辩时如何演示。所有命令都在项目根目录执行；安装步骤见根目录 [README](../README.md#快速开始)。

算法与环境（`src/`）只用标准库；批量实验与画图需要 matplotlib，上位机需要 PySide6（均在 `requirements.txt` 中）。

## 1. 常用命令

| 目的 | 命令 |
| --- | --- |
| 运行全部测试 | `python -m unittest discover -s tests` |
| 打开上位机 | `python tools/MazesTest/maze_app.py`（可加地图路径；`--rule turn_cost:weight=2` 以指定规则启动） |
| 基础规则正式实验 | `python src/run_experiments.py --plan basic`（约 8 分钟） |
| 扩展正式实验 | `python src/run_experiments.py --plan ext_turn`（X1，约 15 分钟）、`ext_noise`（X2，约 30 分钟）、`ext_two_phase`（X3，约 20 分钟）；加 `--dry-run` 只预览设置 |
| 扩展分析 / 难度刻画 / 事后验证 | `python src/ext/analysis.py`；`python src/ext/difficulty.py features`；`python src/ext/posthoc.py divisor`（`contact`、`soft`） |
| 自选实验 | `python src/run_experiments.py --rule motion_time --maps "mazes/classic/external_*.json" --algorithms dfs repeated_astar rule_optimal` |
| 从 CSV 重画图表 | `python src/run_experiments.py --plot results/basic/main` |
| 生成计划要求的地图 | `python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 1 10` |
| 导出演示图片 / GIF | `python tools/MazesTest/maze_app.py --export mazes/classic/external_uk2011f.json --strategy flood_fill --gif -o results/local/demo` |

复现正式结果时建议加 `--out results/local/<名称>`，与已提交的结果分开比较。报告中每个结果对应的命令见[报告第 6 章](Result.md#6-复现方式)。

## 2. 代表性演示素材

`results/basic/demo/` 中预先导出了几组图片，答辩时可直接展示：

| 文件 | 展示的现象 |
| --- | --- |
| `external_uk2011f_flood_fill.gif` / `.png` | Flood-Fill：乐观假设未知边可通行，撞到新墙后改道（紫色虚线为规划路线，红线为刚发现的墙） |
| `external_uk2011f_dfs.png` | DFS：系统遍历，回溯分支多，步数远多于最短路 |
| `external_1stworld_wall_follower_left.gif` / `.png` | 沿墙法：中央目标是“孤岛”，绕外圈一周后判定陷入循环（失败案例） |
| `external_1stworld_repeated_astar.png` | 重复 A*：路线与 Flood-Fill 接近，但只在被挡住时重新规划 |
| `external_1stworld_bfs.png` | 已知地图 BFS：最短路参照 |

扩展阶段的图表在 `results/ext/analysis/`（λ 曲线、噪声曲线、ε 曲线）；对抗迷宫 `results/ext/difficulty/adversarial_*.json` 可直接用上位机打开。

## 3. 答辩现场演示步骤（约 8 分钟）

**基础规则（约 5 分钟）**

1. **打开上位机**，地图选 `external_uk2011f`，确认顶部规则面板显示“基础规则”。
2. **实时运行页**：选 `flood_fill`，勾选“迷雾模式”，速度调到 15 步/秒，点“运行”。讲解：灰色区域是电脑鼠还不知道的部分，红线是刚发现的墙，紫色虚线是它当前的计划；事件日志中的“路线重新规划”就是乐观假设被推翻的时刻。
3. **同屏对比页**：勾选 `dfs`、`flood_fill`、`repeated_astar`、`wall_follower_left`，点“跑完”。讲解成功率、步数、计算时间的差别（重复 A* 与 Flood-Fill 步数接近、计算量小一个数量级）。
4. **地图编辑页**：用 Wilson 生成器随机生成一张地图，切回对比页重新运行，说明“迷宫结构会改变算法优劣”（报告发现 6）。

**扩展规则（约 3 分钟）**

5. **转弯代价**：规则面板“代价模型”选转弯代价、λ = 2。对比页勾选 `repeated_astar`、`turn_aware_astar`、`turn_aware_astar_w2`，表格多出“规则代价”列。讲解：懂规则的规划在未知地图上没有显著优势（发现 7）。
6. **噪声观测**：“代价模型”改回不叠加，“观测模型”选噪声观测，把前 / 侧 / 后准确率设为 0.8 / 0.7 / 0.6（X2 的低准确率档）。对比页勾选 `belief_astar` 与 `belief_astar_soft`，比较撞墙次数（发现 11）。
7. **两阶段比赛**：观测改回理想，“比赛流程”选两阶段。对比 `repeated_astar`（到达即停）与 `bounded_explore_e0`，看成绩与冲刺 / 最优（发现 12）。
8. **批量实验页**（可选）：“实验来源”选正式计划，展示子实验列表与已有结果，说明正式结果就是这样批量产生的。

## 4. 计时不包含动画

所有运行（上位机、命令行、测试）都通过 `src/core/algorithm_api.py` 的 `Runner` 执行，它只对算法自身的 `reset`、`plan`、`choose_direction` 计时；读图、环境检查、绘图、动画、`debug_view` 和写盘都在计时之外。`tests/test_core/test_experiments.py` 的 `TimingScopeTests` 用一个“绘制很慢”的策略验证了这一点。批量实验不显示动画，正式计时以批量实验的结果为准。
