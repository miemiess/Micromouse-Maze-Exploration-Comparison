"""电脑鼠迷宫探索桌面应用（PySide6）的启动入口，也支持不打开窗口的批量导出。

打开应用：
    python tools/MazesTest/maze_app.py                                   # 打开 地图库中的第一张地图
    python tools/MazesTest/maze_app.py mazes/classic/external_uk2011f.json

批量导出（不显示窗口，默认输出到 results/figures/）：
    python tools/MazesTest/maze_app.py --export "mazes/classic/*.json"                       # 每张地图一张 PNG
    python tools/MazesTest/maze_app.py --export "mazes/classic/*.json" --strategy flood_fill  # 运行到结束后的画面
    python tools/MazesTest/maze_app.py --export mazes/classic/external_uk2011f.json --strategy dfs --gif

批量生成地图到地图库 mazes/classic/（同名文件跳过；实验计划的生成地图集即由此产生）：
    python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal --loops 0 10 30 --seeds 1 10
"""

import argparse
import glob
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from simulation import ROOT, Maze, Runner, discover_algorithms


def build_parser() -> argparse.ArgumentParser:
    """定义命令行参数。"""
    parser = argparse.ArgumentParser(
        description="电脑鼠迷宫探索桌面应用",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("maze", nargs="?", help="启动时打开的迷宫 JSON")
    parser.add_argument("--export", nargs="+", metavar="MAZE",
                        help="批量导出这些迷宫的图片后退出（可用通配符）")
    parser.add_argument("-o", "--output", default=str(ROOT / "results" / "figures"),
                        help="导出目录，默认 results/figures")
    parser.add_argument("--strategy", help="导出时先用该算法运行到结束，画出最终状态")
    parser.add_argument("--seed", type=int, default=None, help="传给策略的随机种子")
    parser.add_argument("--gif", action="store_true", help="同时导出完整过程 GIF（需要 --strategy）")
    parser.add_argument("--size", type=int, default=900, help="PNG 宽度（像素）")
    parser.add_argument("--generate", nargs="+", metavar="ALGORITHM",
                        help="批量生成地图：生成算法（backtracker / wilson / prim / kruskal）")
    parser.add_argument("--loops", nargs="+", type=int, default=[0], help="环路比例（百分比），可多个")
    parser.add_argument("--seeds", nargs=2, type=int, default=[1, 10], metavar=("FIRST", "LAST"),
                        help="种子范围（含两端），默认 1 10")
    parser.add_argument("--maze-size", nargs=2, type=int, default=[16, 16], metavar=("W", "H"),
                        help="生成地图的宽和高，默认 16 16")
    return parser


def batch_generate(args) -> int:
    """按 生成算法 × 环路比例 × 种子 批量生成地图，存入地图库；打印写入与跳过的数量。"""
    from app.main_window import MAZE_DIR
    from maze_document import GENERATORS, MapLibrary, generate

    unknown = [g for g in args.generate if g not in GENERATORS]
    if unknown:
        sys.exit(f"unknown generator {unknown}; available: {', '.join(GENERATORS)}")
    library = MapLibrary(MAZE_DIR)
    width, height = args.maze_size
    written = skipped = 0
    for algorithm in args.generate:
        for loop in args.loops:
            for seed in range(args.seeds[0], args.seeds[1] + 1):
                doc = generate(width, height, seed=seed, loop_fraction=loop / 100, algorithm=algorithm)
                if library.save_generated(doc):
                    written += 1
                else:
                    skipped += 1
    print(f"generated {written}, skipped {skipped} existing -> {MAZE_DIR}")
    return 0


def expand_paths(patterns: list[str]) -> list[Path]:
    """展开通配符（Windows 终端不会自动展开 *.json）。

    Raises:
        SystemExit: 某个模式没有匹配到文件。
    """
    paths = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern)) if any(c in pattern for c in "*?[") else [pattern]
        if not matches:
            sys.exit(f"no file matches: {pattern}")
        paths.extend(Path(m) for m in matches)
    return paths


def batch_export(args) -> int:
    """按命令行参数批量导出图片，打印每个输出文件的路径，返回退出码。"""
    from app.export import export_gif, render_image, save_png, snapshot_title

    if args.gif and not args.strategy:
        sys.exit("--gif requires --strategy")
    info = None
    if args.strategy:
        strategies, _ = discover_algorithms()
        if args.strategy not in strategies:
            sys.exit(f"unknown strategy {args.strategy!r}; available: {', '.join(strategies)}")
        info = strategies[args.strategy]

    out = Path(args.output)
    for path in expand_paths(args.export):
        maze = Maze.from_json(path)
        if info is None:
            print(save_png(render_image(maze, size=args.size, title=maze.maze_id),
                           out / f"{maze.maze_id}.png"))
            continue
        snap = Runner(maze, info.create(), seed=args.seed).run()
        print(save_png(render_image(maze, snap, size=args.size,
                                    title=snapshot_title(maze, info.name, snap)),
                       out / f"{maze.maze_id}_{info.name}.png"))
        if args.gif:
            print(export_gif(maze, info.create, out / f"{maze.maze_id}_{info.name}.gif",
                             seed=args.seed))
    return 0


def main(argv: list[str] | None = None) -> int:
    """命令行入口：有 --export 时批量导出，否则打开主窗口并进入事件循环。"""
    args = build_parser().parse_args(argv)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    if args.export:
        return batch_export(args)
    if args.generate:
        return batch_generate(args)

    from app.main_window import MainWindow
    app.setApplicationName("Micromouse Maze Explorer")
    window = MainWindow(Path(args.maze) if args.maze else None)
    window.resize(1320, 860)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
