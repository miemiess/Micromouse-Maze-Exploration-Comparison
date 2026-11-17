"""将 micromouse_maze_tool 的 16×16 二进制地图转换为项目 JSON。"""

import argparse
import json
from pathlib import Path


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("revision", help="上游仓库提交版本")
    args = parser.parse_args()
    print(json.dumps(convert(args.source, args.revision), ensure_ascii=False, indent=2))
