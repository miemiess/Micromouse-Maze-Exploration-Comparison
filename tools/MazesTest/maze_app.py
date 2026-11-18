"""电脑鼠迷宫探索桌面应用（PySide6）的启动入口，也支持不打开窗口的批量导出。

打开应用：
    python tools/MazesTest/maze_app.py                                   # 打开 地图库中的第一张地图
    python tools/MazesTest/maze_app.py mazes/external_uk2011f.json

批量导出（不显示窗口，默认输出到 results/figures/）：
    python tools/MazesTest/maze_app.py --export "mazes/*.json"                       # 每张地图一张 PNG
    python tools/MazesTest/maze_app.py --export "mazes/*.json" --strategy flood_fill  # 运行到结束后的画面
    python tools/MazesTest/maze_app.py --export mazes/external_uk2011f.json --strategy dfs --gif
"""

import argparse
import glob
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from simulation import ROOT, Maze, Runner, discover_strategies


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
    return parser


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
        strategies, _ = discover_strategies()
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

    from app.main_window import MainWindow
    app.setApplicationName("Micromouse Maze Explorer")
    window = MainWindow(Path(args.maze) if args.maze else None)
    window.resize(1320, 860)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
