"""上位机与 src/ 算法统一接口之间的连接层。

算法的发现、运行和统计全部来自公共接口层 src/core/algorithm_api.py（上位机、批量实验和测试共用同一套规则），
本模块只负责把 src/ 加入导入路径并转出这些名称，另外提供画图用的几何函数 wall_segment。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # tools/MazesTest/simulation.py → 项目根目录
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from core.algorithm_api import (  # noqa: E402,F401  转出给上位机使用
    DELTAS, EXPLORE, KNOWN_MAP, AlgorithmInfo, Cell, Direction, Edge, Maze, Runner,
    Snapshot, discover_algorithms, load_algorithm, maze_walls, run_episode)


def wall_segment(a: Cell, b: Cell) -> tuple[tuple[int, int], tuple[int, int]]:
    """计算两个相邻格之间那面墙的线段端点（迷宫坐标，格子 (x, y) 占 [x, x+1] × [y, y+1]）。

    Returns:
        线段两端 ((x1, y1), (x2, y2))。
    """
    (x1, y1), (x2, y2) = sorted((tuple(a), tuple(b)))
    if x1 != x2:  # 东西相邻：墙是 x = x2 处的竖线
        return (x2, y1), (x2, y1 + 1)
    return (x1, y2), (x1 + 1, y2)  # 南北相邻：墙是 y = y2 处的横线
