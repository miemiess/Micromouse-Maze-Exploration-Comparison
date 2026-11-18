# 可视化工具

桌面应用（PySide6），用于实时运行算法、多算法同屏对比、编辑地图，以及导出报告用的 PNG 和 GIF。应用通过 `simulation.Runner` 驱动 `src/environment.py` 的 `MazeEnvironment` 和 `src/` 中的真实算法，界面上的步数、转向、重复访问等统计就是环境实际记录的结果，与实验规则一致。

## 准备

```
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 启动

```
python tools/MazesTest/maze_app.py                                  # 打开 MAP 中的第一张地图
python tools/MazesTest/maze_app.py tools/MazesTest/MAP/external_uk2011f.json
```

**地图库 `tools/MazesTest/MAP/`**：项目全部迷宫地图的存放处，上位机和实验共用，来源说明见 [MAP/README.md](MAP/README.md)。工具栏左侧的下拉框列出其中所有地图。
- **导入地图**（Ctrl+O）：选择任意位置的 JSON 文件，先完整验证再复制进 MAP，保存为 `<地图 ID>.json`。
  - 拒绝导入的情况：不是 JSON，或缺字段、类型错误、坐标越界、墙两端不相邻、重复墙、没有目标。会弹窗说明原因。
  - 合法但有提醒的情况（如目标不可达）：询问后可以导入。
  - MAP 中已有同名地图时，会询问是否覆盖。
- **导出地图**（Ctrl+Shift+S）：把当前地图另存一份到任意位置，不改变当前打开的文件。
- **保存到 MAP**（Ctrl+S）：MAP 中的地图原地保存。通过命令行参数打开的 MAP 外文件，保存时在 MAP 中另存为 `<地图 ID>.json`，原文件不变。

**实时运行**：选择算法后点"单步"或"运行"，可以调整速度、种子和移动预算。
- 黑色墙是电脑鼠已观测到的墙，灰色是还没观测到的墙。勾选"迷雾模式"后只显示已观测的部分，未到过的格子会变暗，相当于电脑鼠自己的视角。
- 红色粗线是这一步刚发现的墙，紫色虚线是策略当前打算走的路线。Flood-Fill 被新发现的墙挡住时会改道，事件日志里记为"路线重新规划"。
- 格子数字：Flood-Fill 显示到目标的距离，DFS 显示首次访问的顺序。DFS 当前的分支（回溯栈）用紫色底色标出。
- "导出"区域：可以把当前画面存为 PNG，或按当前设置从头录制完整过程的 GIF。

**同屏对比**：勾选 2~4 个算法，在同一地图、同一种子下同步推进。下方表格对比统计，成功且步数最少的一行标绿。可以把所有画面拼成一张对比图导出。

**地图编辑**：
- 墙工具：点击格子边缘加墙或拆墙。起点 / 目标工具：点击格子设置。
- 可以新建空白地图，也可以按尺寸、种子、环路比例随机生成。生成器为递归回溯，种子会写入 `metadata`，方便复现。
- "检查"区域显示地图是否有效、目标是否可达。目标不可达的地图仍可保存，用于无路测试。
- "保存到 MAP"、"导出…"的规则同上。保存的文件就是项目 JSON 格式，可以直接用于实验。注意：直接修改并保存 MAP 中已有的地图，会覆盖实验地图；修改外部比赛迷宫前，建议先在"地图属性"里改一个新的地图 ID。编辑后切到运行页或对比页，会自动用新地图重新开始。

**新算法**：在 `src/` 中新增实现 Strategy 接口的类（`name`、`reset`、`choose_direction`），重启应用后会自动出现在算法列表中，不需要改动工具。

## 命令行批量导出

不打开窗口，默认输出到 `results/figures/`：

```
python tools/MazesTest/maze_app.py --export "tools/MazesTest/MAP/*.json"                       # 每张地图一张 PNG
python tools/MazesTest/maze_app.py --export "tools/MazesTest/MAP/*.json" --strategy flood_fill  # 运行到结束后的画面
python tools/MazesTest/maze_app.py --export tools/MazesTest/MAP/external_uk2011f.json --strategy dfs --gif
```

可选参数：`-o 目录`、`--seed`、`--size 宽度像素`。导出的图片和界面画法完全一致；图片标题使用英文，可以直接放进报告。

## 显示策略内部状态（可选）

策略可以额外实现 `debug_view()`，返回下面的字典（键都可以省略），应用会把它叠加显示：

```python
def debug_view(self) -> dict:
    return {
        "known_walls": [[[x1, y1], [x2, y2]], ...],  # 策略认为存在的墙
        "cell_text":   [[x, y, "12"], ...],          # 格子文字，如距离值
        "cell_color":  [[x, y, "#ffcc00"], ...],     # 格子底色
        "plan":        [[x, y], ...],                # 从下一格开始、打算走的路线
    }
```

- 该方法在每次 `choose_direction` 之后调用，不计入策略计算时间；不实现也能正常运行，只是不显示这些内容。
- 它目前是可视化工具的可选扩展，还不是 `src/README.md` 中的公共接口；需要成为正式约定时，先在 Issue 中讨论。
- 写法可以参考 `src/dfs.py` 和 `src/flood_fill.py`。

## 文件结构

| 文件 | 职责 |
| --- | --- |
| `simulation.py` | 运行核心（不依赖界面库）：发现 `src/` 中的策略；`Runner` 逐步运行并生成快照，包括已观测墙、新发现的墙、是否重新规划和实时统计 |
| `maze_document.py` | 地图编辑模型与地图库（不依赖界面库）：改墙、设起点和目标、检查、随机生成、读写 JSON；`MapLibrary` 负责导入验证和存入 MAP |
| `MAP/` | 项目全部迷宫地图（含外部比赛迷宫、来源说明 README 和上游许可证） |
| `convert_external.py` | 把上游 `.maz` 二进制迷宫转换为项目 JSON |
| `app/maze_view.py` | 迷宫画布：用 QPainter 绘制地图和运行状态，编辑模式下响应点击 |
| `app/tabs.py` | 三个功能页，以及共用的运行控制器、控制面板、显示选项 |
| `app/main_window.py` | 主窗口：地图下拉框、导入 / 导出 / 保存、菜单、未保存修改提示，并在功能页之间同步地图 |
| `app/export.py` | 把画布渲染为 PNG / GIF，以及对比图拼接 |
| `maze_app.py` | 启动入口和命令行批量导出 |

## 说明

- `simulation.maze_walls()` 是上位机中唯一读取 `Maze` 私有墙壁字段的地方，只在环境之外用于显示和统计，不会交给策略。以后 `Maze` 提供公开属性时，只需修改这一处。
- 导出 GIF 时会先完整运行一次统计步数，自动抽帧，使总帧数不超过 150。
