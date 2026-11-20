# 未知迷宫中电脑鼠探索算法的比较与分析

Computational Thinking for AI 小组项目（Track A：自主机器人导航与算法分析）。

电脑鼠一开始不知道迷宫地图，只能边走边看墙、更新地图、选择下一步，直到到达中央目标。本项目用 **Python 仿真**比较多种探索与路径规划算法，并实现、验证本组提出的新策略。不需要实体机器人。

> 研究问题：在相同迷宫、初始信息、观测能力和预算下，不同探索算法在到达效率、重复移动与计算开销上有什么差异？为什么？规则更接近真实比赛后，结论是否仍然成立？

## 当前进度

| 阶段 | 状态 | 入口 |
| --- | --- | --- |
| **基础规则**（16×16、每步代价 1、理想观测） | ✅ 已完成并冻结，标签 `basic-rules-v1` | 代码 [`src/basic/`](src/basic/README.md) · 结果 [`results/basic/`](results/README.md) · 文档 [`Docs/basic/`](Docs/README.md) |
| **扩展规则**（转弯代价、两阶段、噪声；启发式与近似算法） | 🟡 规划完成，待开发（从阶段 0 开始） | 路线图 [`Docs/ext/dev-plan.md`](Docs/ext/dev-plan.md) · 代码 [`src/ext/`](src/ext/README.md) |
| **最终报告** | 🟡 中文初稿，扩展结果、英文定稿、贡献记录待完成 | [`Docs/Result.md`](Docs/Result.md) |

**基础阶段的主要结论**（详见报告第 2、4 章）：

- 基础规则下推荐 **重复 A***：514/514 张地图全部到达，步数 / 最短路均值 2.17；与 Flood-Fill 步数相近，计算量只有其 1/15～1/21。
- 迷宫结构决定算法优劣：沿墙法在有环路的迷宫上大多失败（144/514）；只用一种迷宫生成器得到的结论可能完全不成立。
- 本组新方案“先验增强重复 A*”只降低了最坏情况，整体不优于重复 A*。原因是开发集只含生成图，出现了分布偏移；按地图来源分层的事后分析证实了这一点。

## 快速开始

需要 Python 3.10+（开发使用 3.14.7）。

```bash
python -m venv .venv
# Windows：.venv\Scripts\Activate.ps1    macOS / Linux：source .venv/bin/activate
python -m pip install -r requirements.txt

python -m unittest discover -s tests            # 全部测试（含基础规则回归测试）
python tools/MazesTest/maze_app.py              # 上位机：实时运行、同屏对比、已知地图规划、批量实验、地图编辑
python src/run_experiments.py --plan basic      # 复现基础规则的正式实验（约 8 分钟）→ results/basic/
```

更多命令与答辩演示步骤见 [`Docs/basic/demo-guide.md`](Docs/basic/demo-guide.md)。

## 目录结构

整个仓库按 **公共接口（core）/ 基础规则（basic，冻结）/ 扩展（ext，开发中）** 分层，`src/`、`results/`、`Docs/`、`tests/` 都按这一层次划分。

```text
src/                       代码（接口契约见 src/README.md）
  run_experiments.py         实验命令行入口
  core/                      公共接口层：环境、算法接口与驱动、实验框架（basic 与 ext 共用，修改须向后兼容）
  basic/                     基础规则层（冻结）：algorithms/ 9 个已有算法 + 新方案及其消融变体、plan.py 实验计划、开发集调参脚本
  ext/                       扩展层：rules/ 规则、algorithms/ 新算法、plan.py 扩展实验计划（待建）
results/                   实验结果
  basic/                     基础规则正式结果：main/、randomness/、dev/、demo/
  ext/                       扩展阶段正式结果
  local/                     自选实验与上位机导出（不提交）
Docs/                      文档（索引见 Docs/README.md）
  Result.md  log.txt         最终报告、开发日志
  course/  basic/  ext/      课程材料 / 基础规则文档 / 扩展计划
tests/                     测试：test_core/、test_basic/（含回归测试）、test_ext/、test_tools/
tools/MazesTest/           上位机（PySide6），说明见 tools/MazesTest/README.md
mazes/                     地图：classic/ 下全部地图（外部迷宫库 external_* 只读，生成图 gen_*），命名规范见 mazes/README.md
```

## 开发约定（人与 AI 共用）

1. **基础层冻结**：`src/basic/`、`results/basic/`、`Docs/basic/` 对应标签 `basic-rules-v1`，只修 bug，不改行为。改变结果的修改会被 `tests/test_basic/test_regression.py` 拦下。
2. **新代码放扩展层**：新算法 → `src/ext/algorithms/<名称>.py`；新规则 → `src/ext/rules/`；新实验计划 → `src/ext/plan.py`；测试 → `tests/test_ext/`；结果 → `results/ext/<名称>/`；文档 → `Docs/ext/`。
3. **只通过公共接口接入**：从 `core.algorithm_api`、`core.environment`、`core.experiments` 导入；复用基础算法时从 `basic.algorithms.<模块>` 导入，不复制代码。接口契约见 [`src/README.md`](src/README.md)。
4. **修改公共接口层 `src/core/`**：必须向后兼容（新参数的默认值等于基础规则），并通过全部测试。
5. **算法自动发现**：每个类设置唯一 `name`（重名会被拒绝），上位机和实验框架无需修改即可使用；消融变体用类属性 `ablation_of` 声明。
6. **实验先写计划再运行**：参数只在开发集上调，开发集按地图来源分层；看过测试结果后不再改参数，事后分析必须标注。
7. **记录**：完成一项工作后在 `Docs/log.txt` 追加一行，更新下方任务表的状态与交付链接。

新增一个扩展算法的最短路径：在 `src/ext/algorithms/` 新建文件 → 按 `src/README.md` 实现 `reset` / `choose_direction`（或 `plan`）→ 在 `tests/test_ext/` 加测试 → 运行全部测试 → 重启上位机即可看到（带 `[EXT]` 标记）。

## 任务表

**认领方式**：提交一个 Issue 说明认领哪项任务（也可以让 AI 代为认领），把下表“负责人 / 状态”改成自己的 GitHub 用户名和“进行中”，提交到 main；完成后补充交付链接、更新状态并关闭 Issue。

### 基础规则阶段（已完成）

| 编号 | 内容 | 交付 | 负责人 / 状态 |
| --- | --- | --- | --- |
| A1 | 坐标、地图 JSON、Observation、Strategy 接口、运行状态与指标 | [`src/README.md`](src/README.md) | yuchen-1412 / 已完成 |
| A2 | 环境：地图验证、观测、移动、统计、无真值泄漏 | `src/core/environment.py`；`tests/test_core/` | yuchen-1412 / 已完成 |
| A3 | 地图：外部迷宫库 394 张（micromouse_maze_tool，MIT）、4 种生成器与批量生成 | `mazes/`；[`mazes/README.md`](mazes/README.md) | yuchen-1412 / 已完成 |
| B1 | 算法登记：信息假设、规则、复杂度、源码阅读记录 | [`Docs/basic/algorithm-methods.md`](Docs/basic/algorithm-methods.md) | mmy / 已完成 |
| B2 | 基线：DFS＋实际回溯、Flood-Fill | `src/basic/algorithms/dfs.py`、`flood_fill.py` | mmy / 已完成 |
| B3 | 更多算法：沿墙法、随机游走、贪心 DFS、重复 A* | `src/basic/algorithms/` | mmy / 已完成 |
| C1 | 新方案设计：先验增强重复 A*（柱子规则 + 自适应未知边惩罚），可证明无效而排除的候选 | [`Docs/basic/algorithm-design.md`](Docs/basic/algorithm-design.md) | mmy / 已完成 |
| C2 | 新方案实现、开发集调参、消融、事后分析 | `src/basic/algorithms/prior_astar.py`、`src/basic/dev_tuning.py`；`results/basic/dev/` | mmy / 已完成 |
| C3 | 已知地图参照：BFS、A*（基础规则下 Dijkstra 与 BFS 等价，不单独实现） | `src/basic/algorithms/bfs.py`、`astar.py` | mmy / 已完成 |
| D1 | 实验计划：问题、地图、划分、预算、指标 | [`Docs/basic/experiment-plan.md`](Docs/basic/experiment-plan.md) | mmy / 已完成 |
| D2 | 实验框架与正式实验（6682 + 30 次运行） | `src/core/experiments.py`、`src/basic/plan.py`；`results/basic/` | mmy / 已完成 |
| D3 | 演示与运行说明 | [`Docs/basic/demo-guide.md`](Docs/basic/demo-guide.md)；`results/basic/demo/` | mmy / 已完成 |

### 扩展阶段（待认领，详见 [`Docs/ext/dev-plan.md`](Docs/ext/dev-plan.md) 第 4 节）

| 编号 | 阶段 | 内容 | 依赖 | 负责人 / 状态 |
| --- | --- | --- | --- | --- |
| E0 | 0 | 基础设施：`Ruleset` 规则对象；`Runner` / 实验框架的 `rule` 参数（默认基础规则）；上位机规则切换栏与横幅 | 无，**优先** | 待认领 / 未开始 |
| E1 | 1 | 运动时间模型与转弯代价规则（参数来源要记录） | E0 | 待认领 / 未开始 |
| E3 | 1 | 启发式搜索：（格子, 朝向）A*、加权 A*；可选 D* Lite、前沿探索 | E0；转弯加权依赖 E1 | 待认领 / 未开始 |
| D5 | 2 | 两阶段规则（探索 + 冲刺）与 ε 提前停止（近似算法） | E0 | 待认领 / 未开始 |
| E2 | 3 | 传感器噪声与置信度融合（**先开 Issue 讨论撞墙规则**） | E0；需组内同意 | 待认领 / 未开始 |
| D4 | 可选 | 迷宫难度刻画与对抗式生成最坏迷宫 | 无 | 待认领 / 未开始 |
| 全员 | 收尾 | 报告第 3 章扩展结果、英文定稿、参考文献核查、贡献记录、在干净提交上重跑全部实验 | 各模块结果 | 全员 / 未开始 |

## 课程要求对应

课程要求 3–4 人一组。采用多算法比较与自主设计是本组的路线，课程并不要求实现指定的算法或数量。

| 课程交付项 | 本项目位置 |
| --- | --- |
| 问题定义、计算模型 | 报告第 1 章；`src/README.md`；`src/core/environment.py` |
| 算法设计与选择理由 | 报告 2.1、2.6、第 4 章；`Docs/basic/algorithm-methods.md`、`algorithm-design.md` |
| 复杂度分析 | 报告 2.2、4.2；算法登记表 |
| 启发式 / 近似算法 | 基础：新方案与消融（第 4 章）；扩展：加权 A*、ε 提前停止（阶段 1、2） |
| Python 概念验证 | `src/`、`tools/MazesTest/` |
| 实验评价 | `Docs/basic/experiment-plan.md`；`results/basic/`；扩展：`results/ext/` |
| 局限与改进 | 报告 2.7、第 5 章 |
| 最终报告 | `Docs/Result.md`（定稿后译为英文） |

允许使用现有库和开源实现，但需要解释与论证算法选择；不把第三方源码直接当作本组原创。

## 协作

- 所有人直接提交到 `main`，不使用功能分支或 Pull Request；步骤见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- 先认领任务、说明要改哪些文件，再开始修改，避免同时覆盖同一文件。
- 课程原始要求：[`Docs/course/Project_Brief.pdf`](Docs/course/Project_Brief.pdf)（最终以此为准）；讨论阶段的方案概要：[`Docs/course/Micromouse_Project_Proposal.pdf`](Docs/course/Micromouse_Project_Proposal.pdf)（不代表教师已批准）。

## 参考源码与资料

| 链接 | 用途与注意事项 |
| --- | --- |
| [Python Flood-Fill](https://github.com/ParameswaranSajeenthiran/FloodFill-Maze-Solver-Algorithm) | 阅读 / 对照；阅读记录见 `Docs/basic/algorithm-methods.md` 第 5 节 |
| [AIMA-Python](https://github.com/aimacode/aima-python) | DFS、BFS 等通用搜索参考；普通 DFS 返回路径不等于未知迷宫的实际探索动作 |
| [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) | A*、Dijkstra 等路径规划参考；需区分在线重规划与完整地图条件 |
| [micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool) | 外部迷宫库的数据来源（MIT），转换说明见 `mazes/README.md` |
| [MicroMouse Maze Library](https://github.com/kerikun11/micromouse-maze-library) | 三段式探索、未知墙视为墙的回程、加减速代价表（扩展阶段参考） |
| [MMS 模拟器](https://github.com/mackorone/mms) | 可选的外部可视化；本项目使用自带上位机 |

仓库中没有直接复制以上项目的代码。使用时记录仓库链接、commit/tag、许可证、引用的函数和本组修改；参考工程的成绩或描述不等于本组实验结论。
