# AGENTS.md：给 AI 助手和组员的工作规则

本文件是仓库里所有 AI 助手（Claude Code、Codex、Copilot 等）和组员共同遵守的规则。开始任何工作前先读完本文件，再读你的任务说明。

## 项目一句话

用 Python 仿真比较电脑鼠在**未知迷宫**中的探索算法（课程小组项目）。基础规则阶段已完成并冻结；现在做**扩展阶段**：在基础规则上叠加新规则（转弯代价、运动时间……），并写“懂规则”的新算法。

- 总览与进度：`README.md`
- 扩展路线图（做什么、按什么顺序、怎样算完成）：`Docs/ext/dev-plan.md`
- 接口规范（环境、观测、算法接口、规则接口）：`src/README.md`
- 扩展层怎么接入、懂规则算法的写法示例：`src/ext/README.md`
- 任务说明：`Docs/ext/tasks/`（每个任务一份，写明范围与验收标准；验收通过后由负责人删除）

## 环境与命令

Python 3.10+（开发用 3.14），虚拟环境在 `.venv`。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests                       # 全部测试，提交前必须全部通过
python -m unittest tests.test_basic.test_regression        # 基础规则回归测试（改了 src/core 必跑）
python -m unittest tests.test_ext.test_<名称>              # 单个测试文件
python tools/MazesTest/maze_app.py --rule turn_cost:weight=2   # 上位机（人工查看效果，可选）
```

Windows 上无界面运行测试需先设 `QT_QPA_PLATFORM=offscreen`；输出乱码时加 `python -X utf8`。

## 目录分层（硬规则）

| 目录 | 能不能改 | 说明 |
| --- | --- | --- |
| `src/basic/`、`results/basic/`、`Docs/basic/` | **不能改**（只修 bug，且不得改变结果） | 基础规则阶段，冻结于标签 `basic-rules-v1` |
| `src/core/` | 只在任务说明允许时改，必须向后兼容 | 公共接口层；**不得导入 `ext`**（有测试检查） |
| `src/ext/algorithms/` | 新算法放这里，一个文件一个算法（或一组变体） | 自动发现，不用登记 |
| `src/ext/rules/` | 新规则层放这里 | 模块里的 `LAYERS` 被自动发现 |
| `tests/test_ext/` | 扩展的测试放这里，文件名 `test_*.py` | |
| `results/local/` | 自选实验的输出，**不提交** | |

## 写算法必须遵守

1. **探索算法只能用观测**：只能用 `choose_direction(observation)` 收到的信息。禁止使用 `maze_walls`、`open_neighbours`、`has_wall`、`maze_blocked`、`Maze.walls` 或读地图文件——这些只给已知地图规划器（`mode = KNOWN_MAP`）用。
2. **复用公共工具，不重写**：已知墙用 `KnownWalls`，按规则代价搜路用 `heading_search`，启发式用 `cost_lower_bound`，都从 `core.algorithm_api` 导入；代价模型取 `rule.cost_model`（在 `configure(rule)` 里拿到）。写法示例见 `src/ext/README.md`。
3. **基础规则下也要能跑**：不能假设一定有代价层。
4. **无随机性就要可复现**：同一地图、同一种子，两次运行路线必须相同。
5. **类属性**：唯一的 `name`；为某些规则设计的算法写 `designed_for = ("turn_cost", ...)`；文档字符串第一行是一句话说明（上位机会显示）。
6. **文件头**写清：算法思路、信息假设、决策规则、复杂度、随机性（参考 `src/basic/algorithms/repeated_astar.py`）。

## 测试与验收

- 任务说明里列出的验收测试由负责人事先写好。**不得为了通过而修改、删除或跳过验收测试**；觉得测试有问题，在任务说明的“问题记录”里写清楚，停下来交给负责人。
- 新增的扩展算法会自动进入 `tests/test_ext/test_planning.py` 的接入检查（每套规则下到达目标、规则代价口径一致）。
- 提交前运行**全部测试**，必须 `OK`（允许 skipped）。

## 实验纪律

- 不调参、不跑正式实验，除非任务说明明确要求。带参数的方法只在开发集上调参，参数候选与选取标准先写进 `Docs/ext/` 的实验计划。
- 不要为了让结果好看改规则或改地图；发现问题记录下来。

## Git 协作（全组直接在 main 上提交，详见 `CONTRIBUTING.md`）

```bash
git pull --no-rebase origin main          # 开始前
# ……工作、测试……
git add <只加你自己改的文件>               # 不要 git add -A
git diff --cached                          # 检查暂存内容
git commit -m "E3-1：实现懂规则的重复 A*"
git pull --no-rebase origin main
git push origin main
```

- 不强制推送、不改写历史、不提交 `.venv`、`__pycache__`、`results/local/`、密码或令牌。
- 只改任务说明允许的文件；需要改其他文件时先停下来问。
- 完成后在 `Docs/log.txt` 末尾追加一行：`名字 日期 内容简述`（AI 助手写代它工作的组员的名字）。

## 完成时的汇报格式

在任务说明的“完成记录”一节填写（或在提交说明里写）：

1. 改了哪些文件；
2. 测试结果（`Ran N tests ... OK` 那一行）；
3. 与任务说明不一致或没把握的地方；
4. 观察到的现象（如某张地图上表现异常），只记录，不擅自修改。
