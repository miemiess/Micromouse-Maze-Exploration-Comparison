# 运行与演示说明（D3）

本文说明如何安装、运行、复现实验，以及答辩时如何用上位机演示。所有命令都在项目根目录执行。

## 1. 安装

需要 Python 3.10 及以上（开发使用 3.14.7）。

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS / Linux：source .venv/bin/activate
pip install -r requirements.txt   # PySide6（上位机）与 matplotlib（图表、GIF）
```

算法本身（`src/` 中的环境与各算法）只用标准库；批量实验与画图需要 matplotlib，上位机需要 PySide6，请先按 `requirements.txt` 安装。

## 2. 常用命令

| 目的 | 命令 |
| --- | --- |
| 运行全部测试 | `python -m unittest discover -s tests` |
| 打开上位机 | `python tools/MazesTest/maze_app.py` |
| 生成实验计划要求的地图 | `python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 1 10` |
| 运行标准实验（D1 计划） | `python src/run_experiments.py --plan basic` |
| 自选实验 | `python src/run_experiments.py --maps "mazes/classic/external_*.json" --algorithms dfs flood_fill --repeats 3` |
| 从 CSV 重画图表 | `python src/run_experiments.py --plot results/basic/main` |
| 导出演示图片 / GIF | `python tools/MazesTest/maze_app.py --export mazes/classic/external_uk2011f.json --strategy flood_fill --gif -o results/basic/demo` |

标准实验在一台普通笔记本上约需数分钟（514 张地图 × 13 个算法 × 3 次重复，另加 C2 开发集）。

## 3. 代表性演示

`results/basic/demo/` 中预先导出了几组图片，答辩时可直接展示，也可以用上一节的命令重新生成：

| 文件 | 展示的现象 |
| --- | --- |
| `external_uk2011f_flood_fill.gif` / `.png` | Flood-Fill：乐观假设未知边可通行，撞到新墙后改道（紫色虚线为规划路线，红线为刚发现的墙） |
| `external_uk2011f_dfs.png` | DFS：系统遍历，回溯分支多，步数远多于最短路 |
| `external_1stworld_wall_follower_left.gif` / `.png` | 沿墙法：中央目标是“孤岛”，绕外圈一周后判定陷入循环（失败案例） |
| `external_1stworld_repeated_astar.png` | 重复 A*：路线与 Flood-Fill 接近，但只在被挡住时重新规划 |
| `external_1stworld_bfs.png` | 已知地图 BFS：最短路参照 |

## 4. 答辩现场演示步骤（约 5 分钟）

1. **打开上位机**，地图选 `external_uk2011f`。
2. **实时运行页**：选 `flood_fill`，勾选“迷雾模式”，速度调到 15 步/秒，点“运行”。讲解：灰色区域是电脑鼠还不知道的部分，红线是刚发现的墙，紫色虚线是它当前的计划；事件日志中的“路线重新规划”就是乐观假设被推翻的时刻。
3. **同屏对比页**：勾选 `dfs`、`flood_fill`、`repeated_astar`、`wall_follower_left`，点“跑完”。讲解表格：成功率、步数、计算时间的差别（重复 A* 与 Flood-Fill 步数接近、计算量小一个数量级）。
4. **已知地图规划页**：运行 `bfs` 和 `astar`，说明两者最短路长度相同、扩展节点数不同，并作为探索算法的参照。
5. **地图编辑页**：选 Wilson 生成器随机生成一张地图，切回对比页重新运行，说明“迷宫结构会改变算法优劣”（`Docs/Result.md` 发现 6）。
6. **批量实验页**：点“核心 3 张”、勾选几个算法、点“运行并导出”，打开结果文件夹，展示 `runs.csv`、`summary.md` 和图表，说明正式结果就是这样批量产生的。

## 5. 计时不包含动画

所有运行（上位机、命令行、测试）都通过 `src/core/algorithm_api.py` 的 `Runner` 执行，它只对算法自身的 `reset`、`plan`、`choose_direction` 计时；读图、环境检查、绘图、动画、`debug_view` 和写盘都在计时之外。测试 `tests/test_core/test_experiments.py` 中的 `TimingScopeTests` 用一个“绘制很慢”的策略验证了这一点：4 次绘制共耗时 0.2 秒以上，计入的计算时间仍接近 0。批量实验不显示动画，正式计时以批量实验的结果为准。

## 6. 结果目录

| 目录 | 内容 |
| --- | --- |
| `results/basic/` | 按实验计划运行的正式结果（`main/`、`randomness/`；开发集调参记录在 `dev/`） |
| `results/basic/demo/` | 演示用图片与 GIF |
| `results/local/batch-<时间>/` | 上位机批量实验页的自选实验 |
