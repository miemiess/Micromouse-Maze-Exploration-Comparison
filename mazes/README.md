# 迷宫地图

项目的**全部迷宫地图统一放在 `mazes/classic/`**，不分子文件夹，一视同仁地管理：实验和上位机（`tools/MazesTest`）都默认读取这个文件夹，上位机的地图下拉框、导入、保存和批量生成也都使用它。本目录（`mazes/`）只放说明、许可证和转换脚本。

**外部迷宫只读**：文件名以 `external_` 开头的是整理好的外部迷宫库地图，不要手工修改。在上位机中修改它们后保存，会自动另存为新地图（例如 `external_uk2011f` → `uk2011f_edit`），`metadata.derived_from` 记录原地图。自己的地图不要使用 `external_` 前缀。

地图 JSON 使用 `src/README.md` 规定的格式：左下角为 (0, 0)，向北 y 增加；外边界默认为墙，`blocked_edges` 记录两个相邻格之间的内部墙。起点、初始朝向和目标保存在各地图文件中。

## 文件

| 位置 | 内容 |
| --- | --- |
| `classic/external_*.json` | 394 张 16×16 外部迷宫库地图（以比赛迷宫为主，含少量测试 / 练习图），来源见下节 |
| `classic/gen_*.json` 等 | 上位机生成或编辑后保存的地图，metadata 记录生成算法、种子和环路比例 |
| `classic/README.md` | 批量导入的来源版本、数量和每张被跳过地图的原因 |
| `EXTERNAL_LICENSE.txt` | 上游仓库的 MIT 许可证原文 |
| `convert_external.py` | 把上游 `.maz` 二进制迷宫转换为项目 JSON：单张转换并打印，或加 `--batch` 批量转换、验证、去重并写入 `classic/` |

## 命名规范

| 类别 | 文件名 / `maze_id` | 例子 | 实验中的地图组 |
| --- | --- | --- | --- |
| 外部迷宫库 | `external_<上游文件名>` | `external_uk2011f` | `external` |
| 生成地图 | `gen_<生成算法>_<宽>x<高>_s<种子>[_l<环路百分比>]` | `gen_backtracker_16x16_s1`、`gen_wilson_16x16_s3_l10` | `<生成算法>_loop<环路百分比>`，如 `wilson_loop10` |
| 编辑后另存 | `<原名去掉 external_>_edit[N]` | `uk2011f_edit` | 不进入标准实验 |

生成算法为 `backtracker`、`wilson`、`prim`、`kruskal`。外部迷宫库以历届比赛迷宫为主，但也包含上游提供的少量测试 / 练习图（如 `external_empty`、`external_8x8-practice`、`external_training-maze-test1`），因此统称“外部迷宫库”，不称“真实比赛迷宫”。

## 外部迷宫库的来源

外部迷宫库全部来自 [micromouseonline/micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool) 的 `mazefiles/binary/`，来源版本为 `12118e413f6be8341ea7f64c100e7625178cd6dc`。上游仓库使用 MIT 许可，原文见 `EXTERNAL_LICENSE.txt`。地图由原始二进制墙壁数据转换为本项目 JSON，起点 (0,0)、朝北和中央四格目标为本项目统一实验设定；没有手工修改墙壁。

- **核心 3 张**（最早由 A3 整理，测试和快速调试使用）：

  | 文件 | 上游文件 | 尺寸 | 起点 / 朝向 | 目标 |
  | --- | --- | --- | --- | --- |
  | `classic/external_1stworld.json` | `mazefiles/binary/1stworld.maz` | 16×16 | (0,0) / N | 中央四格 |
  | `classic/external_japan2017ef.json` | `mazefiles/binary/japan2017ef.maz` | 16×16 | (0,0) / N | 中央四格 |
  | `classic/external_uk2011f.json` | `mazefiles/binary/uk2011f.maz` | 16×16 | (0,0) / N | 中央四格 |

- **批量导入 391 张**：上游共 408 个文件，跳过 10 张中央目标不可达、4 张与其他地图墙壁完全相同，加上核心 3 张共 394 张。跳过原因见 `classic/README.md`。

转换时检查外边界及相邻格墙壁一致性。上游提醒数据可能有错误或重复；本目录已排除转换失败、目标不可达和重复的地图，但不保证每张都与真实比赛场地一致。重新导入（结果可复现，已存在的同名文件不会被重写）：

```bash
python mazes/convert_external.py --batch <micromouse_maze_tool 的 mazefiles/binary 目录> 12118e413f6be8341ea7f64c100e7625178cd6dc
```

## 使用说明

- 真值地图只由环境读取，策略通过观测逐步了解墙壁。无路地图用于健壮性验证时，应与可达地图分开报告。
- 正式实验的测试集从外部迷宫库与多种生成器（上位机提供递归回溯、Wilson、Prim、Kruskal）生成的地图中选取，并分开开发集与测试集（见 README 任务 D1）。只用一种生成器得到的结论可能有偏差（见 `Docs/Result.md` 发现 6）。
