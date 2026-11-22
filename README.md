# 未知迷宫中电脑鼠探索算法的比较与分析

Computational Thinking for AI 小组项目（Track A：自主机器人导航与算法分析）。

电脑鼠一开始不知道迷宫地图，只能边走边看墙、更新地图、选择下一步，直到到达中央目标。本项目用 **Python 仿真**比较多种探索与路径规划算法，并实现、验证本组提出的新策略。不需要实体机器人。

> 研究问题：在相同迷宫、初始信息、观测能力和预算下，不同探索算法在到达效率、重复移动与计算开销上有什么差异？为什么？规则更接近真实比赛后，结论是否仍然成立？

## 项目状态

| 部分 | 状态 | 入口 |
| --- | --- | --- |
| 基础规则（16×16、每步代价 1、理想观测） | ✅ 完成并冻结（标签 `basic-rules-v1`） | 报告第 1、2、4 章 · [`results/basic/`](results/README.md) |
| 扩展规则（转弯代价、运动时间、噪声观测、两阶段比赛） | ✅ 完成（实验计划冻结后运行 X1～X4，另有标注的事后验证） | 报告第 3 章 · [`results/ext/`](results/ext/README.md) |
| **最终报告** | 🟡 中文初稿完整，进入收尾（见下方清单） | [`Docs/Result.md`](Docs/Result.md) |

## 从哪里开始

| 我想…… | 看这里 |
| --- | --- |
| 了解结论 | [报告](Docs/Result.md)：摘要、2.6 节（基础规则下的选择）、3.9 节（扩展规则下的选择） |
| 查实验数据 | [`results/README.md`](results/README.md)（目录与字段）、[`results/ext/README.md`](results/ext/README.md)（扩展结论摘要） |
| 运行、复现或演示 | 下方“快速开始”；完整命令与答辩演示步骤见 [`Docs/demo-guide.md`](Docs/demo-guide.md) |
| 读代码 | [`src/README.md`](src/README.md)（公共接口与目录分层）、[`src/ext/README.md`](src/ext/README.md)（扩展算法与规则） |
| 查设计与实验计划 | [`Docs/README.md`](Docs/README.md)（全部文档索引） |
| 核对课程要求 | [`Docs/course/Project_Brief.pdf`](Docs/course/Project_Brief.pdf)（最终以此为准）与下方“课程要求对应” |

## 主要结论

**基础规则**（报告第 2、4 章）

- 推荐 **重复 A***：514/514 张地图全部到达，步数 / 最短路均值 2.17；与 Flood-Fill 步数相近，计算时间中位数约为其 1/15～1/21。
- 迷宫结构决定算法优劣：沿墙法在有环路的迷宫上大多失败（144/514 成功）；只用一种生成器得到的结论可能完全不成立。
- 本组新方案“先验增强重复 A*”只降低了最坏情况，整体不优于重复 A*；原因是开发集只含生成图（分布偏移），按来源分层的事后分析证实了这一点。

**扩展规则**（报告第 3 章）

- 规则更接近真实比赛后，**乐观重规划仍然最好**；按转弯代价规划、D* Lite 增量修复、置信度融合都没有显著收益，加权 A*（w = 2）显著减少搜索量而代价不变。
- 两阶段比赛中，“证明找到最短路再冲刺”在外部迷宫库上显著优于“到达即停”。本组提出的误差有界提前停止满足冲刺 ≤ (1 + ε) 倍最优；ε 的最佳取值取决于计分中探索的折算系数。
- 噪声下，置信度融合的收益被“无视全部读数”的兜底规划抵消；改为按置信度加代价后（`belief_astar_soft`，冻结后新增），撞墙减少 20%～68%，步数不变。

## 快速开始

需要 Python 3.10+（开发使用 3.14.7）。所有命令在项目根目录执行。

```bash
python -m venv .venv
# Windows：.venv\Scripts\Activate.ps1    macOS / Linux：source .venv/bin/activate
python -m pip install -r requirements.txt

python -m unittest discover -s tests                  # 全部测试（含基础规则回归测试）
python tools/MazesTest/maze_app.py                    # 上位机：实时运行、同屏对比、规则切换、批量实验、地图编辑
python src/run_experiments.py --plan basic            # 复现基础规则正式实验（约 8 分钟）→ results/basic/
python src/run_experiments.py --plan ext_turn         # 复现扩展实验 X1（另有 ext_noise、ext_two_phase）→ results/ext/
python src/ext/analysis.py                            # 扩展实验的配对检验与曲线 → results/ext/analysis/
```

复现报告中全部结果的命令清单见[报告第 6 章](Docs/Result.md#6-复现方式)。

## 最终报告收尾清单

剩下的工作都围绕最终报告。完成一项就勾掉，并在 [`Docs/log.txt`](Docs/log.txt) 记一行。

- [ ] **通读校对**中文初稿：数字与 `results/` 中的文件一致，术语、算法名、表号与发现编号统一。
- [ ] **参考文献核查**：[报告](Docs/Result.md#参考文献待核查)末尾标为“待核查”的条目、比赛规程版本、ε 放宽是否已有文献。
- [ ] **参数来源核查**：运动时间模型（`src/ext/rules/motion_time.py`）、传感器准确率、两阶段计分中的 1/30（`src/ext/rules/two_phase.py`）。
- [ ] **在干净提交上重跑**全部正式实验并核对（基础结果的元数据记录的是 `4e768cb+dirty`）；用 `--out` 输出到独立目录再比较。
- [ ] **贡献记录**：按下方“分工与贡献”写入报告。
- [ ] **英文定稿**：中文定稿后译为英文，按课程要求导出。
- [ ] **答辩演练**：按 [`Docs/demo-guide.md`](Docs/demo-guide.md) 演示一遍。

## 目录结构

代码、结果、文档与测试都按 **公共接口（core）/ 基础规则（basic，冻结）/ 扩展（ext）** 分层。

```text
src/                       代码（接口契约见 src/README.md）
  run_experiments.py         实验命令行入口
  core/                      公共接口层：环境、算法接口与驱动、规则、规划工具、实验框架
  basic/                     基础规则层（冻结）：9 个已有算法 + 新方案及消融、实验计划、调参与事后分析
  ext/                       扩展层：rules/ 4 类规则层、algorithms/ 11 个扩展算法、实验计划、分析与事后验证
results/                   实验结果（说明见 results/README.md）
  basic/                     基础规则：main/、randomness/、dev/、demo/
  ext/                       扩展：turn/、noise/、two_phase/、analysis/、difficulty/、posthoc/
  local/                     自选实验与上位机导出（不提交）
Docs/                      文档（索引见 Docs/README.md）
  Result.md                  最终报告
  demo-guide.md              运行、复现与答辩演示
  log.txt                    开发日志
  course/  basic/  ext/      课程材料 / 基础规则文档 / 扩展设计与实验计划
tests/                     测试：test_core/、test_basic/（含回归测试）、test_ext/、test_tools/
tools/MazesTest/           上位机（PySide6），说明见 tools/MazesTest/README.md
mazes/                     地图：classic/ 下 514 张（外部迷宫库 external_* 只读，生成图 gen_*）、splits/ 扩展阶段地图划分
```

## 分工与贡献

| 部分 | 内容 | 负责人 | 交付 |
| --- | --- | --- | --- |
| A1～A3 | 接口约定（坐标、地图 JSON、观测、策略接口、状态与指标）；环境；外部迷宫库 394 张与 4 种生成器 | yuchen-1412 | [`src/README.md`](src/README.md)、`src/core/environment.py`、[`mazes/`](mazes/README.md) |
| B1～B3 | 算法登记与源码阅读；DFS、Flood-Fill、沿墙法、随机游走、贪心 DFS、重复 A* | mmy | [`Docs/basic/algorithm-methods.md`](Docs/basic/algorithm-methods.md)、`src/basic/algorithms/` |
| C1～C3 | 新方案“先验增强重复 A*”的设计、实现、调参、消融与事后分析；已知地图参照 BFS、A* | mmy | [`Docs/basic/algorithm-design.md`](Docs/basic/algorithm-design.md)、`src/basic/`、`results/basic/dev/` |
| D1～D3 | 基础实验计划、实验框架与正式实验、演示 | mmy | [`Docs/basic/experiment-plan.md`](Docs/basic/experiment-plan.md)、`src/core/experiments.py`、`results/basic/` |
| E0、E1 | 规则框架（基础规则 + 叠加层、`--rule`、上位机规则面板）；转弯代价、运动时间、规则最优参照 | Luca | `src/core/rules.py`、`src/ext/rules/`、`tools/MazesTest/app/rule_bar.py` |
| E3 | 朝向 A* 及加权变体、D* Lite、最近前沿探索 | zhouying682 | `src/ext/algorithms/` |
| E2、撞墙处理 | 噪声观测层、置信度重规划及消融与改进；撞墙处理层 | Luca、zhouying682 | `src/ext/rules/noisy_sensor.py`、`collision.py`、`src/ext/algorithms/belief_astar.py` |
| D4、D5 | 迷宫难度刻画与对抗迷宫；两阶段比赛与误差有界提前停止 | Luca | `src/ext/difficulty.py`、`src/ext/rules/two_phase.py`、`src/ext/algorithms/bounded_explore.py` |
| 扩展实验与报告 | 扩展实验计划、X1～X4、分析与事后验证；报告第 3 章 | Luca | [`Docs/ext/experiment-plan.md`](Docs/ext/experiment-plan.md)、`src/ext/plan.py`、`analysis.py`、`posthoc.py`、`results/ext/` |
| 收尾 | 见上方清单 | 全员 | [`Docs/Result.md`](Docs/Result.md) |

详细的开发记录（谁在何时做了什么）见 [`Docs/log.txt`](Docs/log.txt)。

## 课程要求对应

课程要求 3–4 人一组。采用多算法比较与自主设计是本组的路线，课程并不要求实现指定的算法或数量。

| 课程交付项 | 本项目位置 |
| --- | --- |
| 问题定义、计算模型 | 报告第 1 章；`src/README.md`；`src/core/environment.py` |
| 算法设计与选择理由 | 报告 2.1、2.6、3.9、第 4 章；`Docs/basic/algorithm-methods.md`、`algorithm-design.md` |
| 复杂度分析 | 报告 2.2、4.2；各算法文件头 |
| 启发式 / 近似算法 | 报告第 3 章：加权 A*（w = 2）、ε 有界提前停止、按置信度加代价的兜底规划；第 4 章：先验增强重复 A* |
| Python 概念验证 | `src/`、`tools/MazesTest/` |
| 实验评价 | 实验计划 `Docs/basic/experiment-plan.md`、`Docs/ext/experiment-plan.md`；结果 `results/` |
| 局限与改进 | 报告 2.7、3.10、第 5 章 |
| 最终报告 | `Docs/Result.md`（定稿后译为英文） |

允许使用现有库和开源实现，但需要解释与论证算法选择；不把第三方源码直接当作本组原创。

## 修改约定

收尾阶段以检查和写作为主，改动代码或结果时遵守以下约定：

1. **结果冻结**：基础规则（`src/basic/`、`results/basic/`）对应标签 `basic-rules-v1`，扩展实验按[冻结的计划](Docs/ext/experiment-plan.md)运行。只修 bug、不改行为；改变基础结果的修改会被 `tests/test_basic/test_regression.py` 拦下。
2. **新增分析必须标注**：看过测试结果之后做的分析或新增的算法（如 `src/basic/posthoc_stratified.py`、`src/ext/posthoc.py`、`belief_astar_soft`）一律标为“事后”，不改写正式结论。
3. **改公共接口 `src/core/`**：必须向后兼容（新参数的默认值等于原行为），并通过全部测试。接口契约见 [`src/README.md`](src/README.md)。
4. **记录**：完成一项工作后在 `Docs/log.txt` 追加一行。
5. **协作**：所有人直接提交到 `main`，步骤见 [`CONTRIBUTING.md`](CONTRIBUTING.md)；改同一个文件（尤其是报告）前先告诉组员。

## 参考源码与资料

| 链接 | 用途与注意事项 |
| --- | --- |
| [Python Flood-Fill](https://github.com/ParameswaranSajeenthiran/FloodFill-Maze-Solver-Algorithm) | 阅读 / 对照；阅读记录见 `Docs/basic/algorithm-methods.md` 第 5 节 |
| [AIMA-Python](https://github.com/aimacode/aima-python) | DFS、BFS 等通用搜索参考；普通 DFS 返回路径不等于未知迷宫的实际探索动作 |
| [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) | A*、Dijkstra 等路径规划参考；需区分在线重规划与完整地图条件 |
| [micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool) | 外部迷宫库的数据来源（MIT），转换说明见 `mazes/README.md` |
| [MicroMouse Maze Library](https://github.com/kerikun11/micromouse-maze-library) | 三段式探索、未知墙视为墙的回程、加减速代价表（扩展阶段参考） |
| [MMS 模拟器](https://github.com/mackorone/mms) | 可选的外部可视化；本项目使用自带上位机 |

仓库中没有直接复制以上项目的代码。使用时记录仓库链接、commit/tag、许可证、引用的函数和本组修改；参考工程的成绩或描述不等于本组实验结论。讨论阶段的方案概要见 [`Docs/course/Micromouse_Project_Proposal.pdf`](Docs/course/Micromouse_Project_Proposal.pdf)（不代表教师已批准）。
