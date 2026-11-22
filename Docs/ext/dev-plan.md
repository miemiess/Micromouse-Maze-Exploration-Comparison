# 扩展阶段开发计划（ext）

> 本文是扩展阶段的**唯一路线图与进度看板**：先看第 0 节“现在到哪了、下一步做什么”，再看后面各节的设计与约定。
> 基础规则阶段已完成并冻结（标签 `basic-rules-v1`，代码 `src/basic/`，结果 `results/basic/`）。任务认领见根目录 README 的任务表；
> 交给组员或 AI 执行的子任务说明放在 `Docs/ext/tasks/`（验收通过后删除，结果记入本文与开发日志 `Docs/log.txt`）。

## 0. 进度看板

最后更新：2026-11-22。每完成一项（或改变计划）就更新本节。

**一句话**：扩展规则的 4 个维度（代价、观测、撞墙处理、比赛流程）全部实现；扩展算法 10 个（含 D5 的有界提前停止）；D4 难度刻画与对抗迷宫已出结果；实验计划已冻结，X1～X3 正式结果与分析已完成（[`results/ext/README.md`](../../results/ext/README.md) 有结论摘要），**下一步是写报告**。

| 项 | 内容 | 状态 | 负责 | 代码 / 测试 |
| --- | --- | --- | --- | --- |
| E0 | 规则框架：基础规则 + 叠加层、`--rule`、上位机规则面板 | ✅ 完成 | Luca | `src/core/rules.py` · `tests/test_ext/test_rules.py` |
| E1 | 代价层：转弯代价、运动时间；规则最优参照 `rule_optimal` | ✅ 完成（运动参数来源待核查） | Luca | `src/ext/rules/turn_cost.py`、`motion_time.py` · `test_turn_cost.py`、`test_motion_time.py` |
| E3 | 懂规则的探索：朝向 A* 及 w = 2 变体、D* Lite、最近前沿 | ✅ 完成（正式实验待做） | zhouying682 | `src/ext/algorithms/` · `test_turn_aware_astar.py`、`test_incremental_frontier.py` |
| 撞墙处理 | 撞墙后原地转向继续、可靠接触反馈、累计上限（contact 维度的层） | ✅ 完成 | zhouying682（实现）、Luca（改为规则层） | `src/ext/rules/collision.py` · `test_collision.py` |
| E2 | 噪声观测层 + 置信度（对数几率）重规划及“只信最近读数”消融 | ✅ 完成（传感器参数为假设，正式实验待做） | Luca | `src/ext/rules/noisy_sensor.py`、`src/ext/algorithms/belief_astar.py` · `test_noisy_sensor.py` |
| 实验计划 | 扩展实验的问题、地图划分、算法、规则、指标、结论标准 | ✅ 已冻结（2026-11-22） | Luca | [`Docs/ext/experiment-plan.md`](experiment-plan.md) |
| 计划落地 | `src/ext/plan.py`（`--plan ext_turn` / `ext_noise`）、分层划分 `mazes/splits/ext_dev.json` | ✅ 完成 | Luca | `src/ext/plan.py` · `tests/test_ext/test_plan.py` |
| 分析脚本 | `src/ext/analysis.py`：配对胜负、符号检验、分组一致性、λ / 噪声 / ε 曲线 | ✅ 完成 | Luca | `src/ext/analysis.py` · `test_analysis.py` |
| 正式结果 | X1～X3 运行与分析 | ✅ 完成；写入报告第 3 章、4.6 节待做 | Luca | `results/ext/`、`results/ext/analysis/report.md` |
| D5 | 两阶段比赛（探索 + 返回 + 冲刺）与 ε 提前停止（近似算法，冲刺代价 ≤ (1 + ε) × 最优，已用测试验证） | ✅ 完成（正式实验 X3 待做；计分系数 1/30 来源待核查） | Luca | `src/ext/rules/two_phase.py`、`src/ext/algorithms/bounded_explore.py` · `test_two_phase.py` |
| D4 | 迷宫难度特征与基础结果的相关（描述性）、模拟退火对抗迷宫 | ✅ 完成（结果：`results/ext/difficulty/`） | Luca | `src/ext/difficulty.py` · `test_difficulty.py` |
| 收尾 | 运动 / 传感器参数来源核查、文献核查、英文定稿、贡献记录、干净提交上重跑全部实验 | ⬜ 未开始 | 全员 | `Docs/Result.md` |

**下一步（按顺序）**

1. ~~确认并冻结实验计划~~（已冻结，2026-11-22）。
2. ~~写分析脚本~~、~~运行 X1～X3~~（已完成，2026-11-22）。
3. **写报告**：把 `results/ext/README.md` 的结论摘要与 D4 描述性结果写入报告第 3 章、4.6 节，并更新摘要与局限。
5. 收尾各项。

**已做的决定**（不再讨论）

- 算法不按规则拆分，全部在同一个算法库；为某规则设计的算法用 `designed_for` 标记。
- 撞墙处理是普通叠加层（contact 维度），不叠加时保持基础规则“首次撞墙即 invalid_action”；噪声观测层默认撞墙后继续。
- 噪声下撞墙反馈总是可靠；外圈边界总是读对。
- 运动时间与传感器准确率的默认值是仿真假设，报告中如实标注，可用参数覆盖。

**已知问题 / 待核查**

- 运动时间模型的 v_max、accel、转向用时，噪声层的前 / 侧 / 后准确率：都没有实测或文献来源。
- 置信度重规划在噪声下撞墙较多（默认准确率下每局约 30 次）：未知边按乐观假设视为可走，属于待实验分析的现象，不在实验前调参。
- 上位机规则面板叠加 3 层时最小宽度约 1330 像素。

## 1. 目标

在基础规则（每步代价 1、理想观测、单次到达）之上**逐项放宽假设**，回答：规则更接近真实电脑鼠比赛后，基础阶段的结论（乐观重规划最好、重复 A* 计算量最小）是否仍然成立？并借此补齐课程 Brief 中“设计启发式或近似算法”的要求。

本项目有意只建模**决策层**，以便把差异归因于策略本身；扩展阶段以可选包装层的方式加入另外两层：

| 层 | 真实电脑鼠 | 基础规则 | 扩展 |
| --- | --- | --- | --- |
| 决策层 | 选择下一步往哪走 | `src/basic/algorithms/` | 新算法：`src/ext/algorithms/` |
| 感知层 | 红外传感器融合判断有无墙 | 理想观测，四向 100% 准确 | E2：传感器噪声 + 置信度融合 |
| 控制层 | 电机加减速、转弯 | 走一格 = 1 步，转 90° 计数 | E1：运动时间模型 / 转弯代价 |

**不做**（写入报告的局限分析）：定位误差（SLAM，超出课程范围）、电机 PID（偏离主题）、强化学习（需在同一张地图上反复训练，等于泄露地图信息）。

## 2. 规则层设计

规则拆成四个相互独立的维度，可以组合（每个维度最多一层）：

| 维度 | 基础规则（默认） | 扩展选项 | 任务 |
| --- | --- | --- | --- |
| 代价模型 | 每步 1，转弯只计数 | 转弯代价 λ；运动时间模型（直线梯形加减速 + 转弯耗时，格长取比赛规格，速度、加速度和转向耗时为待校准的仿真假设） | E1 |
| 观测模型 | 理想观测 | 噪声观测：按前 / 侧 / 后设定准确率，读数随机漏报或误报；算法每面墙维护对数几率 S，w = ln(p/(1−p))，P(有墙) = 1/(1+e^(−S)) | E2 ✅ |
| 撞墙处理 | 首次撞墙即 invalid_action | 撞墙后原地转向继续（不移动），接触反馈可靠；可设累计撞墙上限，达到时状态 `collision_limit` | ✅ |
| 比赛流程 | 单次到达目标 | 两阶段：到达目标后可继续探索，返回起点后沿已确认的通路冲刺；成绩 = 冲刺 + 探索 / 30；ε 提前停止 | D5 ✅ |

**实现**：规则 = 基础规则 + 若干叠加层，每个维度最多一层。层通过两个钩子影响运行：`env_options()`（创建环境的参数，如撞墙上限；按维度顺序合并）与 `wrap_env(env)`（包装环境，如给观测加噪声）。

| 位置 | 内容 |
| --- | --- |
| `src/core/rules.py` | 公共接口：`RuleLayer` / `CostLayer` 抽象（`env_options`、`wrap_env`、`param_ranges`）、`Ruleset`（`key`、`spec`、`title`、`color`、`make_env`、`supports`、`collision_limit`、`cost`、`optimal_plan`、`new_meter`）、`BASIC`、`CostMeter`（增量计价，撞墙只计转向）、`parse_rule`、`available_layers`（自动发现）。不导入任何具体规则 |
| `src/ext/rules/turn_cost.py` | `TurnCostLayer(weight=λ)`：代价 = 步数 + λ × 90° 转向 |
| `src/ext/rules/motion_time.py` | `MotionTimeLayer`：梯形 / 三角形速度曲线的直线段 + 固定转向用时；参数与来源见文件头；`equivalent_weight()` 换算 λ |
| `src/ext/rules/collision.py` | `CollisionLayer(limit=inf)`（contact 维度）：撞墙原地转向、不移动，消耗一次动作预算；撞墙后的观测为 `ContactObservation`（`collision_wall` 标出撞到的方向）；累计 limit 次终止。结果另含 `actions`、`collisions` |
| `src/ext/rules/noisy_sensor.py` | `NoisySensorLayer(p_front, p_side, p_back)`（observation 维度，E2）：每面内部墙读数按相对朝向的准确率随机出错；边界总读对、接触反馈可靠；噪声由运行种子与地图 id 决定；默认撞墙后继续 |
| `src/ext/algorithms/rule_optimal.py` | 已知地图参照：当前规则下代价最小的路线（基础规则下等于 BFS 最短路） |
| `src/ext/algorithms/belief_astar.py` | 置信度重规划（E2）：对数几率融合读数，S > 0 视为墙，按规则代价做朝向 A*；找不到路时只把确定的墙当墙再规划；消融 `belief_astar_naive` 只信最近一次读数 |
| `src/core/planning.py` | 为 E3 准备的共用规划工具：`KnownWalls`（已知墙 + 乐观地图）、`heading_search`（（格子, 朝向）上的 Dijkstra / A* / 加权 A*，返回扩展状态数）、`cost_lower_bound`（曼哈顿 + 转弯下界启发式，已验证不高估）；`Ruleset.optimal_plan` 也用它 |

代价模型统一采用“走—停—转”假设：路线拆成直线段与原地转向，总代价 = Σ 直线段代价 + Σ 转向代价。实际路线由 `CostMeter` 在运行中增量计价（每步 O(1)）；规则最优路线在（格子, 朝向）上做 Dijkstra，边为“转 1 / 2 个 90°”或“沿当前朝向直走 k 格”。测试用一个独立的逐格 Dijkstra 交叉验证了最优代价。

命令行写法（`Ruleset.spec`，写入 metadata，可被 `parse_rule` 还原）：`basic`、`turn_cost`、`turn_cost:weight=2`、`motion_time:v_max=1,accel=3`、`noisy_sensor:p_front=0.9`、`collision:limit=5`（`inf` / `unlimited` 为不限）；多层用 `+` 连接（不同维度），如 `turn_cost:weight=2+noisy_sensor+collision:limit=20`。

**接入公共接口的约定**（保证基础规则不受影响）：

- `Runner(maze, algorithm, rule=BASIC)`、`run_episode(..., rule=BASIC)`：新增可选参数，**默认值等于基础规则**，不传时行为与 `basic-rules-v1` 完全相同。
- Strategy 接口不变；需要规则参数的算法可选实现 `configure(rule)`，Runner 在 `reset` 前调用。
- 有代价层时，运行结果多一个 `rule_cost`（规则代价）；实验的 `runs.csv` 追加 `rule`、`rule_cost`、`optimal_rule_cost`、`rule_cost_ratio` 列，汇总表与图表另有规则代价部分。允许撞墙后继续时自动导出 `actions`、`collisions`。上位机和扩展计划为首次终止模式也导出这两列，自选命令行可用 `--collision-stats` 启用。
- 算法可声明 `supported_rules`；未声明时默认支持所有**不改变观测**的规则（基础算法在转弯代价规则下照常运行，作为“不懂规则”的对照）。改变观测的规则（噪声）只对声明支持的探索算法开放；已知地图规划器不使用观测，不受限制。
- 算法不按规则拆分：全部在同一个算法库，任何规则下直接套用。为某些层设计的算法声明 `designed_for`（层 key），只用于上位机标记与 `metadata.json` 的 `algorithm_info` 分组，便于“基础算法 vs 懂规则的算法”同表比较。
- 探索算法也可实现 `stats()`（每次决策后读取），`expanded_nodes` 写入 `runs.csv`，用于比较计算量（如 D* Lite 与全量重算）。
- 撞墙规则：基础规则仍是“首次撞墙 = invalid_action”；叠加撞墙处理层或噪声层后改为“撞墙 = 一次可靠的接触观测、原地转向不移动”（已定，见 `src/README.md` 的“撞墙处理”）。
- 每次修改 `src/core/` 后运行 `tests/test_basic/test_regression.py`。

## 3. 上位机：规则切换必须一眼可见

仍用同一个上位机（`tools/MazesTest`）。规则面板（`tools/MazesTest/app/rule_bar.py`）横跨主窗口顶部、始终可见，把“基础规则 + 叠加层”直接画出来（**已实现**）：

| 位置 | 基础规则 | 基础规则 + 叠加层 |
| --- | --- | --- |
| 规则面板第一行（规则栈） | 灰色实心标签“基础规则”，旁边写明基础规则的内容 | “基础规则”变为描边标签，后面依次是“＋ 层名（参数）”彩色实心标签；右侧显示代价公式与“结果不可与基础规则直接比较”，“↺ 恢复基础规则”按钮可用 |
| 规则面板第二行（叠加） | 每个维度一个下拉框，均为“不叠加” | 选中的层显示参数输入框（如 λ），改参数立即生效 |
| 面板与标签页边框、选中标签 | 中性灰 | 换成层的颜色（转弯代价橙色、运动时间蓝色、噪声观测紫色、撞墙处理玫红），边框加粗 |
| 窗口标题、状态栏 | “【基础规则】”，灰色描边标签 | “【基础规则 + 转弯代价（λ = 2）】”，彩色实心标签（悬停显示命令行写法） |
| 实时运行 / 已知地图页 | 统计面板不变 | 多一个规则颜色的“规则指标”框：代价公式、规则代价、规则最优代价、代价 / 最优 |
| 画布 | 不变 | 迷宫外圈规则颜色外框；转弯点圆环（掉头为双环）；已知地图上的规则最优路线（点划线）；两者可在“显示”中关闭 |
| 同屏对比 | 按步数标出最优 | 多一列“规则代价”，并改按规则代价标出最优；每个画布标题带代价 |
| 批量实验 | 顶部标签“本页实验规则：基础规则” | 彩色标签；汇总表多两列“规则代价/最优”；metadata 记录规则 |
| 导出图片 | 标题不变 | 标题追加规则写法与规则代价，并带同样的规则图层 |
| 算法列表 | 全部算法 | 下拉框按规则适配和算法来源分组。不支持当前规则的算法置灰并提示原因 |

切换规则时，有正在进行或未完成的运行先确认；确认后各页从起点重新运行（当前所在页与地图不变），批量实验先导出已完成的记录。命令行可直接以某规则启动：`python tools/MazesTest/maze_app.py --rule turn_cost:weight=2`。

## 4. 阶段与任务

| 阶段 | 任务 | 内容 | 产出位置 | 完成标准 |
| --- | --- | --- | --- | --- |
| **0. 基础设施** ✅ | E0 | `Ruleset`（基础规则 + 叠加层）；`Runner` / `run_episode` / 实验框架的 `rule` 参数；`--rule` 命令行；上位机规则面板 | `src/core/rules.py`、`tools/MazesTest/app/rule_bar.py` | 已完成：回归测试通过；`tests/test_ext/test_rules.py` |
| **1. 转弯代价与启发式搜索** | E1 ✅、E3 开发完成 | E1 已完成：转弯代价与运动时间模型两个代价层、规则最优参照 `rule_optimal`（`tests/test_ext/test_turn_cost.py`、`test_motion_time.py`）。E3-1 已验收（`turn_aware_astar`、`turn_aware_astar_w2`，见 `tests/test_ext/test_turn_aware_astar.py`）。E3 已实现：（格子, 朝向）状态上的 A*（不高估的“曼哈顿 + 转弯下界”启发式）；加权 A*（f = g + w·h，路径 ≤ w 倍最优）；D* Lite（单位步长的增量重算）、最近前沿探索（沿确认通路导航） | `src/ext/rules/`、`src/ext/algorithms/` | 实验计划先写好；λ / w 只在分层开发集上调；基础算法与懂规则的算法同表比较 |
| **2. 两阶段与近似算法** ✅ | D5 | 探索 + 冲刺；停止判据：乐观代价 O 与悲观代价 P 满足 P ≤ (1 + ε)·O 时停止，冲刺代价 ≤ (1 + ε)·最短路（ε = 0 时即证明最优后停止） | `src/ext/rules/two_phase.py`、`src/ext/algorithms/` | 判据可证明；“探索 + 冲刺总代价”随 ε 的曲线 |
| **3. 噪声观测** ✅ | E2、撞墙处理 | 已完成：噪声观测层、撞墙处理层、置信度重规划 `belief_astar` 与消融 `belief_astar_naive`（`tests/test_ext/test_noisy_sensor.py`、`test_collision.py`）。正式实验待做 | `src/ext/rules/noisy_sensor.py`、`collision.py`、`src/ext/algorithms/belief_astar.py` | 多种子重复，报告均值与离散程度；准确率曲线 |
| **可选研究** ✅ | D4 | 迷宫难度刻画（环路比例、死胡同比例、分岔数、“欺骗度”）；用模拟退火对抗式生成最坏迷宫 | `src/ext/`、`results/ext/` | 特征与算法表现的关系分析 |
| **收尾** | 全员 | 报告第 3 章填入扩展结果；英文定稿；参考文献核查；贡献记录；在干净提交上重跑全部实验 | `Docs/Result.md` | 课程交付项全部覆盖 |

四种已接入的探索策略、已知地图参照和可运行的转弯迷宫示例见[扩展算法说明](../../src/ext/README.md#已实现的算法)。[正式对照计划](experiment-plan.md)已固定分层地图、规则参数和指标，覆盖朝向 A* 两种权重、D* Lite 与最近前沿。转弯加权 Flood-Fill、加权评分与元启发式调参仍是候选方向。

**建议主线：“乐观假设的代价”**——乐观规划什么时候会被误导（难度刻画、对抗迷宫）？换成转弯代价、两阶段规则后，结论是否仍然成立？用一条主线串起算法与实验，避免罗列结果。

**E1 / E3 已知地图验收样例。** [4×5 转弯迷宫](../../tests/test_ext/fixtures/turn_cost_tradeoff.json) 从左下角朝东出发。穷举得到两条简单路径。锯齿路线 `ENENEN` 为 6 步、5 次直角转向，外圈路线 `NNNNEEES` 为 8 步、3 次直角转向（含起步向北）。按“步数 + λ × 转向次数”计分，在 λ = 0.5、1、2 时最优代价分别为 8.5、11、14；λ = 1 时两条路线都应通过验收。

## 5. 实验约定（沿用基础阶段的做法，并吸取其教训）

- **先写计划再运行**（当前计划：[`experiment-plan.md`](experiment-plan.md)）：每个扩展实验在 `Docs/ext/` 写实验计划（问题、地图、算法、参数候选、选取标准、指标），运行后不按结果改规则；改了要写变更记录并重跑。
- **开发集按地图来源分层**（基础阶段的教训，见报告 4.5）：划分固定在 `mazes/splits/ext_dev.json`（由 `src/ext/plan.py` 用固定种子计算，测试检查两者一致），开发集同时包含生成图与 20% 外部迷宫库地图；这部分外部图不进扩展测试集。
- **同一次运行、同一计时口径**：新方案与对照算法在同一个实验中运行；消融变体用类属性 `ablation_of` 声明，自动只进消融图。
- **结果目录**：`results/ext/<规则或实验名>/`，由 `src/ext/plan.py` 的 `PLANS` 注册，当前计划为 `ext_turn` 和 `ext_noise`，可用 `--dry-run` 预览设置与输出目录。
- **有随机性的设置**（噪声）：多种子重复，报告均值与离散程度。

## 6. 与现实的对应（用于报告的问题定义与局限分析）

扫地机器人首次进入新户型（覆盖与重复访问）、仓库机器人或无人机遇到新障碍后改道（重新规划）、搜救机器人在未知废墟中寻找目标、火星车移动代价远高于计算代价、电脑鼠比赛（两阶段规则）。仿真与现实的主要差距：理想观测、统一步长代价、四向观测、已知自身位置、不限电量。E1 已放宽统一步长代价假设，E2 已实现噪声观测以放宽理想观测假设，其余写入局限分析。

上述 D* Lite、两阶段规则、加权 A* 等均为已有方法；本组的贡献在于放进统一框架比较与分析，完成文献核查前不宣称首创。
