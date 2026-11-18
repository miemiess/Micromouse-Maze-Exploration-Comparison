"""导出：把迷宫和运行状态渲染为 PNG / GIF，画法与界面完全一致（都由 MazeView 绘制）。

不需要显示窗口，界面按钮和命令行批量导出（tools/MazesTest/maze_app.py --export）都调用这里的函数。
图片标题使用英文和状态代码，方便直接放进英文报告。
"""

import math
from pathlib import Path

from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter

from simulation import Maze, Runner, Snapshot

from .maze_view import MazeView, ViewOptions

TITLE_HEIGHT = 34
MAX_GIF_FRAMES = 150   # 自动抽帧时 GIF 最多的帧数，避免文件过大


def snapshot_title(maze: Maze, name: str, snapshot: Snapshot) -> str:
    """生成图片标题：地图、算法、步数和状态。"""
    return f"{maze.maze_id} | {name} | step {snapshot.stats['steps']} | {snapshot.status}"


def render_image(maze: Maze, snapshot: Snapshot | None = None, *,
                 options: ViewOptions | None = None, size: int = 900,
                 title: str | None = None) -> QImage:
    """把地图（可选叠加运行状态）渲染为白底图片。

    Args:
        maze: 要绘制的地图。
        snapshot: 运行快照；None 时只画地图和起点处的电脑鼠。
        options: 显示选项，默认与界面默认值相同。
        size: 图片宽度（像素）。
        title: 顶部标题；None 时不留标题栏。

    Returns:
        渲染好的 QImage。
    """
    view = MazeView()
    view.canvas_color = QColor("#ffffff")
    view.set_maze(maze)
    view.set_snapshot(snapshot)
    view.set_options(options or ViewOptions())
    body = round((size - 36) * maze.height / maze.width) + 28  # 与 MazeView 的边距对应
    view.resize(size, body)

    top = TITLE_HEIGHT if title else 0
    image = QImage(size, body + top, QImage.Format_ARGB32)
    image.fill(QColor("#ffffff"))
    painter = QPainter(image)
    if title:
        font = QFont(view.font())
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QColor("#222222"))
        painter.drawText(QRectF(0, 0, size, top), Qt.AlignCenter, title)
    view.render(painter, QPoint(0, top))
    painter.end()
    return image


def tile_images(images: list[QImage], columns: int) -> QImage:
    """把多张图按网格拼成一张（用于多算法对比图）。"""
    width = max(image.width() for image in images)
    height = max(image.height() for image in images)
    rows = math.ceil(len(images) / columns)
    sheet = QImage(width * columns, height * rows, QImage.Format_ARGB32)
    sheet.fill(QColor("#ffffff"))
    painter = QPainter(sheet)
    for i, image in enumerate(images):
        row, col = divmod(i, columns)
        painter.drawImage(col * width, row * height, image)
    painter.end()
    return sheet


def save_png(image: QImage, path: str | Path) -> Path:
    """保存图片；所在文件夹不存在时自动创建。

    Raises:
        OSError: 写入失败。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(path)):
        raise OSError(f"cannot write {path}")
    return path


def export_gif(maze: Maze, make_strategy, path: str | Path, *, seed: int | None = None,
               max_steps: int | None = None, options: ViewOptions | None = None,
               size: int = 520, fps: int = 10, every: int | None = None) -> Path:
    """从起点完整运行一次算法，并把过程保存为 GIF 动画。

    先空跑一遍统计决策次数，再重新运行并按间隔截取画面，避免一次性保存所有帧占用大量内存。
    策略在相同种子下是确定性的，所以两次运行结果相同。

    Args:
        maze: 地图。
        make_strategy: 无参函数，每次调用返回一个新的策略对象（如 StrategyInfo.create）。
        path: 输出 .gif 路径。
        seed、max_steps: 与运行页设置相同。
        options: 显示选项。
        size: 每帧宽度（像素）。
        fps: 每秒帧数；最后一帧额外停留 2 秒。
        every: 每隔几次决策取一帧；None 时自动选择，使总帧数不超过 MAX_GIF_FRAMES。

    Returns:
        写入的文件路径。

    Raises:
        RuntimeError: 未安装 Pillow（随 matplotlib 一起安装）。
    """
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("导出 GIF 需要 Pillow：pip install -r requirements.txt") from exc

    total = Runner(maze, make_strategy(), seed=seed, max_steps=max_steps).run().decision
    every = every or max(1, math.ceil(total / MAX_GIF_FRAMES))
    runner = Runner(maze, make_strategy(), seed=seed, max_steps=max_steps)

    frames = []

    def capture(snapshot: Snapshot) -> None:
        """渲染一帧并转换为 GIF 使用的调色板图像。"""
        image = render_image(maze, snapshot, options=options, size=size,
                             title=snapshot_title(maze, runner.name, snapshot))
        image = image.convertToFormat(QImage.Format_RGBA8888)
        frame = Image.frombuffer("RGBA", (image.width(), image.height()),
                                 bytes(image.constBits()), "raw", "RGBA",
                                 image.bytesPerLine(), 1)
        frames.append(frame.convert("RGB").quantize(colors=128))

    capture(runner.snapshot())
    while not runner.finished:
        snapshot = runner.step()
        if snapshot.decision % every == 0 or runner.finished:
            capture(snapshot)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    durations = [int(1000 / fps)] * (len(frames) - 1) + [2000]
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0)
    return path
