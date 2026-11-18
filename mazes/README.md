# 迷宫地图

项目的全部迷宫地图都存放在这里，实验和上位机（`tools/MazesTest`）都默认读取本目录：上位机的地图下拉框、导入和保存都使用这里。

**外部迷宫只读**：文件名以 `external_` 开头的是整理好的比赛迷宫，不要手工修改。在上位机中修改它们后保存，会自动另存为新地图（例如 `external_uk2011f` → `uk2011f_edit`），`metadata.derived_from` 记录原地图。自己的地图不要使用 `external_` 前缀。

本目录中的 JSON 使用 `src/README.md` 规定的格式：左下角为 (0, 0)，向北 y 增加；外边界默认为墙，`blocked_edges` 记录两个相邻格之间的内部墙。起点、初始朝向和目标保存在各地图文件中。

## 外部地图

以下地图来自 [micromouseonline/micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool)，来源版本为 `12118e413f6be8341ea7f64c100e7625178cd6dc`。上游仓库使用 MIT 许可，许可原文见 `EXTERNAL_LICENSE.txt`。地图由原始二进制墙壁数据转换为本项目 JSON，起点 (0,0)、朝北和中央四格目标为本项目统一实验设定；没有手工修改墙壁。

| 文件 | 上游文件 | 尺寸 | 起点 / 朝向 | 目标 |
| --- | --- | --- | --- | --- |
| `external_1stworld.json` | `mazefiles/binary/1stworld.maz` | 16×16 | (0,0) / N | 中央四格 |
| `external_japan2017ef.json` | `mazefiles/binary/japan2017ef.maz` | 16×16 | (0,0) / N | 中央四格 |
| `external_uk2011f.json` | `mazefiles/binary/uk2011f.maz` | 16×16 | (0,0) / N | 中央四格 |

转换脚本 `convert_external.py` 检查外边界及相邻格墙壁一致性。上游提醒数据可能有错误或重复；使用前仍需验证，且这些地图暂不构成项目计划要求的 20 张独立测试地图。

真值地图只由环境读取，策略通过观测逐步了解墙壁。无路地图用于健壮性验证时，应与可达地图分开报告。

项目实验计划还需要独立收集不少于 20 张有代表性的测试地图，建议包含 16×16 地图，并记录来源、版本、改动和种子。外部地图如参考 https://github.com/micromouseonline/micromouse_maze_tool ，使用前须核对许可、坐标和墙壁编码。
