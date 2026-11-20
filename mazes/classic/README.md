# 外部迷宫库（classic）

来源：[micromouseonline/micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool) `mazefiles/binary/`，提交 `12118e413f6be8341ea7f64c100e7625178cd6dc`，MIT 许可证（原文见 `../EXTERNAL_LICENSE.txt`）。由 `mazes/convert_external.py --batch` 自动导入，未手工修改墙壁（其中 1stworld、japan2017ef、uk2011f 三张最早由 A3 用同一脚本逐张整理，为缩进格式）。

起点 (0, 0) 朝北、目标为中央 2×2 是本项目统一的实验设定。上游说明数据可能有错误或重复；本目录已排除转换失败、目标不可达和墙壁完全相同的地图，但不保证每张都与真实比赛场地一致。文件名以 `external_` 开头，在上位机中只读。

- 上游文件：408 个
- 导入：394 张
- 跳过：14 张

## 跳过的文件

| 上游文件 | 原因 |
| --- | --- |
| `5x5_test1.maz` | 中央目标从起点不可达 |
| `5x5_test2.maz` | 中央目标从起点不可达 |
| `5x5_test3.maz` | 中央目标从起点不可达 |
| `5x5_test4.maz` | 中央目标从起点不可达 |
| `japan2007ef.maz` | 与 external_uk2011f.json 墙壁完全相同 |
| `map-y7.maz` | 中央目标从起点不可达 |
| `map-y77.maz` | 中央目标从起点不可达 |
| `maze-train-10x5-a.maz` | 中央目标从起点不可达 |
| `maze-train-10x5-q.maz` | 中央目标从起点不可达 |
| `maze-train-10x5.maz` | 中央目标从起点不可达 |
| `minimaze.maz` | 中央目标从起点不可达 |
| `uk1989f.maz` | 与 external_japan1991q.json 墙壁完全相同 |
| `us02.maz` | 与 external_robotic-2011-solver-finals.json 墙壁完全相同 |
| `us82.maz` | 与 external_japan1992.json 墙壁完全相同 |
