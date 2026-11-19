"""将 micromouse_maze_tool 的 16×16 二进制地图转换为项目 JSON，支持单张转换与批量导入。

上游仓库：https://github.com/micromouseonline/micromouse_maze_tool （MIT 许可证，原文见 mazes/EXTERNAL_LICENSE.txt）

用法（项目根目录）：
    # 单张：转换后打印 JSON（A3 最初整理 3 张核心迷宫时的用法）
    python mazes/convert_external.py <某个 .maz 文件> <上游提交号>
    # 批量：导入整个 mazefiles/binary 目录到 mazes/classic/
    python mazes/convert_external.py --batch <mazefiles/binary 目录> <上游提交号>

批量导入时，每张地图依次经过：
    1. convert：检查长度、外边界和相邻格墙壁一致性，转换为项目 JSON；
    2. environment.Maze：按项目格式再验证一次；
    3. 可达性：起点 (0, 0) 到中央 2×2 目标不可达的跳过（例如只使用了一小块区域的训练迷宫）；
    4. 去重：墙壁与 mazes/classic/ 中另一张已有地图完全相同的跳过；同名且墙壁相同的视为已存在，不重写文件。
通过的地图以紧凑 JSON 写入 mazes/classic/external_<文件名>.json（external_ 前缀使其在上位机中只读），
并生成 mazes/classic/README.md 记录来源版本、数量和每张被跳过地图的原因。
"""

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "classic"


def convert(path, revision):
    data = path.read_bytes()
    if len(data) != 256 or any(value & ~15 for value in data):
        raise ValueError("地图必须包含 256 个四位墙壁字节")
    edges = []
    # 上游按 x 列优先排列：索引 = x * 16 + y；N/E/S/W 位分别为 1/2/4/8。
    for x in range(16):
        for y in range(16):
            value = data[x * 16 + y]
            if (x == 0 and not value & 8 or x == 15 and not value & 2
                    or y == 0 and not value & 4 or y == 15 and not value & 1):
                raise ValueError("地图外边界缺墙")
            for dx, dy, bit, opposite in ((1, 0, 2, 8), (0, 1, 1, 4)):
                nx, ny = x + dx, y + dy
                if nx >= 16 or ny >= 16:
                    continue
                wall = bool(value & bit)
                if wall != bool(data[nx * 16 + ny] & opposite):
                    raise ValueError(f"墙壁不一致: {(x, y)} / {(nx, ny)}")
                if wall:
                    edges.append([[x, y], [nx, ny]])
    return {"maze_id": "external_" + path.stem, "width": 16, "height": 16,
            "start": [0, 0], "start_heading": "N",
            "goals": [[7, 7], [7, 8], [8, 7], [8, 8]], "blocked_edges": edges,
            "metadata": {"source": "micromouseonline/micromouse_maze_tool",
                         "source_file": "mazefiles/binary/" + path.name,
                         "revision": revision, "seed": None,
                         "notes": "转换墙壁格式；起点、朝向和中央目标为项目实验设定"}}


# ---------------------------------------------------------------- 批量导入

def wall_key(data: dict) -> frozenset:
    """用于去重的墙壁集合（与方向、顺序无关）。"""
    return frozenset(frozenset(map(tuple, edge)) for edge in data["blocked_edges"])


def goal_reachable(data: dict) -> bool:
    """在真实墙壁下，起点能否到达任一目标格。"""
    walls = wall_key(data)
    width, height = data["width"], data["height"]
    start, goals = tuple(data["start"]), {tuple(g) for g in data["goals"]}
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            return True
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen
                    and frozenset(((x, y), (nx, ny))) not in walls):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return False


def import_batch(source_dir: Path, revision: str, out: Path = OUT) -> tuple[list, list]:
    """批量导入 source_dir 中的全部 .maz 文件到 out，并写出 out/README.md 清单。

    Returns:
        (导入的上游文件名列表, [(被跳过的上游文件名, 原因)])。
    """
    sys.path.insert(0, str(HERE.parent / "src"))
    from environment import Maze  # 只有批量导入需要，单张转换不依赖 src/

    out.mkdir(exist_ok=True)
    existing = {}
    for path in sorted(out.glob("*.json")):
        existing[wall_key(json.loads(path.read_text(encoding="utf-8")))] = path.name

    imported, skipped = [], []
    for source in sorted(source_dir.glob("*.maz")):
        try:
            data = convert(source, revision)
        except ValueError as exc:
            skipped.append((source.name, f"转换失败：{exc}"))
            continue
        stem = re.sub(r"[^A-Za-z0-9_-]", "_", source.stem)
        data["maze_id"] = f"external_{stem}"
        try:
            Maze(data)
        except ValueError as exc:
            skipped.append((source.name, f"格式不合法：{exc}"))
            continue
        if not goal_reachable(data):
            skipped.append((source.name, "中央目标从起点不可达"))
            continue
        key = wall_key(data)
        target = out / f"{data['maze_id']}.json"
        if existing.get(key) == target.name:  # 已导入过（含最早由 A3 整理的 3 张），保持原文件不变
            imported.append(source.name)
            continue
        if key in existing:
            skipped.append((source.name, f"与 {existing[key]} 墙壁完全相同"))
            continue
        target.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
                          encoding="utf-8")
        existing[key] = target.name
        imported.append(source.name)

    lines = [
        "# 导入的比赛迷宫（classic）", "",
        "来源：[micromouseonline/micromouse_maze_tool](https://github.com/micromouseonline/micromouse_maze_tool)"
        f" `mazefiles/binary/`，提交 `{revision}`，MIT 许可证（原文见 `../EXTERNAL_LICENSE.txt`）。"
        "由 `mazes/convert_external.py --batch` 自动导入，未手工修改墙壁"
        "（其中 1stworld、japan2017ef、uk2011f 三张最早由 A3 用同一脚本逐张整理，为缩进格式）。", "",
        "起点 (0, 0) 朝北、目标为中央 2×2 是本项目统一的实验设定。上游说明数据可能有错误或重复；"
        "本目录已排除转换失败、目标不可达和墙壁完全相同的地图，但不保证每张都与真实比赛场地一致。"
        "文件名以 `external_` 开头，在上位机中只读。", "",
        f"- 上游文件：{len(imported) + len(skipped)} 个",
        f"- 导入：{len(imported)} 张",
        f"- 跳过：{len(skipped)} 张", "",
        "## 跳过的文件", "", "| 上游文件 | 原因 |", "| --- | --- |",
    ] + [f"| `{name}` | {reason} |" for name, reason in skipped]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return imported, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="单张：.maz 文件；--batch：mazefiles/binary 目录")
    parser.add_argument("revision", help="上游仓库提交版本")
    parser.add_argument("--batch", action="store_true", help="批量导入整个目录到 mazes/classic/")
    args = parser.parse_args()
    if args.batch:
        imported, skipped = import_batch(args.source, args.revision)
        print(f"imported {len(imported)}, skipped {len(skipped)}")
    else:
        print(json.dumps(convert(args.source, args.revision), ensure_ascii=False, indent=2))
