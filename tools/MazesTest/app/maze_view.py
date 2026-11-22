"""迷宫画布控件：用 QPainter 绘制迷宫和运行状态，并在编辑模式下响应鼠标点击。

画布本身不运行算法、不修改地图，只负责"显示什么"和"点到了哪里"：
    - set_board()    设置要显示的地图（真值墙、起点、目标）；
    - set_snapshot() 设置运行状态（simulation.Snapshot），为 None 时只显示地图；
    - set_options()  设置显示选项（迷雾、策略认知墙、规划路线、格子文字等）；
    - 编辑模式下点击墙边发出 edgeClicked，点击格子发出 cellClicked。
"""

from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from simulation import DELTAS, Cell, Direction, Maze, Snapshot, maze_walls, wall_segment  # 先导入：把 src/ 加入路径

from core.rules import BASIC, Ruleset, turn_points  # noqa: E402

COLORS = {
    "background": QColor("#ffffff"),
    "grid": QColor("#e3e3e3"),
    "wall": QColor("#1f1f1f"),
    "unseen_wall": QColor("#b0b0b0"),
    "start": QColor("#b7e4c7"),
    "goal": QColor("#ffd6a5"),
    "visited": QColor(142, 202, 230, 110),
    "fog": QColor(60, 60, 70, 150),
    "path": QColor(29, 78, 216, 190),
    "plan": QColor("#7b2cbf"),
    "known_wall": QColor("#f4a261"),
    "new_wall": QColor("#e63946"),
    "mouse": QColor("#d62828"),
    "text": QColor("#333333"),
    "hover": QColor(29, 78, 216, 150),
    "label": QColor("#666666"),
}

# 电脑鼠三角形的朝向角度（屏幕坐标，0 度朝右，顺时针）。
_ANGLE = {Direction.EAST: 0, Direction.SOUTH: 90, Direction.WEST: 180, Direction.NORTH: 270}


@dataclass
class ViewOptions:
    """显示选项。

    Attributes:
        fog: 迷雾模式。只显示已观测到的墙，未到过的格子变暗，相当于电脑鼠的视角。
        known_walls: 叠加策略自己认为存在的墙（来自 debug_view），用于检查策略的认知。
        plan: 显示策略打算走的路线（来自 debug_view 的 plan）。
        cell_text: 显示格子文字，如 Flood-Fill 距离或 DFS 访问顺序。
        cell_color: 显示策略自定义的格子底色，如 DFS 当前分支。
        path: 显示已走过的路径。
        turns: 扩展规则下标出转弯点（规则颜色的圆环，掉头为双环）。
        rule_optimal: 扩展规则下叠加已知地图上的规则最优路线（规则颜色虚线）。
    """
    fog: bool = False
    known_walls: bool = False
    plan: bool = True
    cell_text: bool = True
    cell_color: bool = True
    path: bool = True
    turns: bool = True
    rule_optimal: bool = True


class MazeView(QWidget):
    """可缩放的迷宫画布。"""

    cellClicked = Signal(object, object)   # (格子, 鼠标按键)
    edgeClicked = Signal(object, object)   # (格子 a, 相邻格子 b)

    def __init__(self, parent=None, *, editable: bool = False):
        """创建空画布。

        Args:
            parent: 父控件。
            editable: 是否为编辑模式（显示悬停高亮并发出点击信号）。
        """
        super().__init__(parent)
        self.editable = editable
        self.edit_target = "edge"   # 编辑模式下悬停高亮的对象："edge" 或 "cell"
        self.options = ViewOptions()
        self.canvas_color: QColor | None = None  # 迷宫外的底色；None 时跟随窗口主题
        self._board = None
        self._snapshot: Snapshot | None = None
        self._hover = None
        self._rule = BASIC
        self._optimal: list[Cell] | None = None   # 当前规则下的最优路线（已知地图参照）
        self.setMinimumSize(240, 240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(editable)

    # -- 外部接口 ---------------------------------------------------------
    def set_board(self, width: int, height: int, start: Cell, start_heading: Direction,
                  goals, walls) -> None:
        """设置要显示的地图。

        Args:
            width、height: 网格尺寸。
            start、start_heading: 起点和初始朝向。
            goals: 目标格集合。
            walls: 内部墙集合（两个相邻格组成的 frozenset）。
        """
        self._board = (width, height, tuple(start), start_heading,
                       frozenset(map(tuple, goals)), frozenset(walls))
        self.update()

    def set_maze(self, maze: Maze) -> None:
        """把环境使用的 Maze 设置为要显示的地图。"""
        self.set_board(maze.width, maze.height, maze.start, maze.start_heading,
                       maze.goals, maze_walls(maze))

    def set_snapshot(self, snapshot: Snapshot | None) -> None:
        """设置运行状态；None 表示只显示地图。"""
        self._snapshot = snapshot
        self.update()

    def set_rule(self, rule: Ruleset, optimal_path: list[Cell] | None = None) -> None:
        """设置当前规则与规则最优路线；基础规则下不画任何规则图层。"""
        self._rule = rule
        self._optimal = [tuple(c) for c in optimal_path] if optimal_path else None
        self.update()

    def set_options(self, options: ViewOptions) -> None:
        """设置显示选项。"""
        self.options = options
        self.update()

    # -- 坐标换算 ---------------------------------------------------------
    def _layout(self) -> tuple[float, float, float]:
        """计算格子边长和左上角位置，使迷宫居中并留出坐标标注的边距。"""
        width, height = self._board[0], self._board[1]
        left, bottom, pad = 28, 20, 8
        cell = max(1.0, min((self.width() - left - pad) / width,
                            (self.height() - bottom - pad) / height))
        ox = left + (self.width() - left - pad - cell * width) / 2
        oy = pad + (self.height() - bottom - pad - cell * height) / 2
        return cell, ox, oy

    def _point(self, fx: float, fy: float) -> QPointF:
        """迷宫坐标（y 向北）转换为屏幕坐标（y 向下）。"""
        cell, ox, oy = self._layout()
        return QPointF(ox + fx * cell, oy + (self._board[1] - fy) * cell)

    def _cell_rect(self, x: int, y: int) -> QRectF:
        """格子 (x, y) 在屏幕上的矩形。"""
        return QRectF(self._point(x, y + 1), self._point(x + 1, y))

    def _hit(self, pos: QPointF):
        """判断屏幕位置落在哪个格子、离哪面内部墙最近。

        Returns:
            ("edge", (a, b))、("cell", 格子) 或 None（在迷宫外）。
        """
        if self._board is None:
            return None
        width, height = self._board[0], self._board[1]
        cell, ox, oy = self._layout()
        fx = (pos.x() - ox) / cell
        fy = height - (pos.y() - oy) / cell
        x, y = int(fx // 1), int(fy // 1)
        if not (0 <= x < width and 0 <= y < height):
            return None
        if self.edit_target == "cell":
            return "cell", (x, y)
        u, v = fx - x, fy - y
        distance, direction = min((u, Direction.WEST), (1 - u, Direction.EAST),
                                  (v, Direction.SOUTH), (1 - v, Direction.NORTH))
        dx, dy = DELTAS[direction]
        neighbour = (x + dx, y + dy)
        if distance < 0.25 and 0 <= neighbour[0] < width and 0 <= neighbour[1] < height:
            return "edge", ((x, y), neighbour)
        return None

    # -- 鼠标 -------------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:
        """编辑模式下更新悬停高亮。"""
        if self.editable:
            hover = self._hit(event.position())
            if hover != self._hover:
                self._hover = hover
                self.update()

    def leaveEvent(self, event) -> None:
        """鼠标离开时清除悬停高亮。"""
        self._hover = None
        self.update()

    def mousePressEvent(self, event) -> None:
        """编辑模式下把点击转换为 edgeClicked / cellClicked 信号。"""
        if not self.editable:
            return
        hit = self._hit(event.position())
        if hit is None:
            return
        kind, target = hit
        if kind == "edge":
            self.edgeClicked.emit(*target)
        else:
            self.cellClicked.emit(target, event.button())

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        """按图层顺序绘制：底色 → 格子着色 → 迷雾 → 网格 → 路线 → 墙 → 文字 → 电脑鼠。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.canvas_color or self.palette().window())
        if self._board is None:
            painter.drawText(self.rect(), Qt.AlignCenter, "未加载地图")
            return
        width, height, start, _, goals, walls = self._board
        snap, opt = self._snapshot, self.options
        debug = (snap.debug if snap and isinstance(snap.debug, dict) else {}) or {}
        cell, _, _ = self._layout()

        painter.fillRect(QRectF(self._point(0, height), self._point(width, 0)),
                         COLORS["background"])
        self._fill_cells(painter, [start], COLORS["start"])
        self._fill_cells(painter, goals, COLORS["goal"])
        if snap:
            self._fill_cells(painter, snap.visited, COLORS["visited"])
            if opt.cell_color:
                for x, y, color in debug.get("cell_color", []):
                    c = QColor(color)
                    c.setAlpha(120)
                    self._fill_cells(painter, [(x, y)], c)
            if opt.fog:
                fog = [(x, y) for x in range(width) for y in range(height)
                       if (x, y) not in snap.visited]
                self._fill_cells(painter, fog, COLORS["fog"])

        grid = QPen(COLORS["grid"], 1)
        painter.setPen(grid)
        for x in range(1, width):
            painter.drawLine(self._point(x, 0), self._point(x, height))
        for y in range(1, height):
            painter.drawLine(self._point(0, y), self._point(width, y))

        if snap and opt.path and len(snap.path) > 1:
            self._polyline(painter, snap.path, QPen(COLORS["path"], max(1.5, cell * 0.08),
                                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if snap and opt.plan and debug.get("plan"):
            plan = [tuple(c) for c in debug["plan"]]
            if plan[0] != snap.position:
                plan.insert(0, snap.position)
            pen = QPen(COLORS["plan"], max(1.5, cell * 0.07), Qt.DashLine, Qt.RoundCap)
            self._polyline(painter, plan, pen)

        if self._rule.cost_layer is not None:
            self._draw_rule_layers(painter, snap, cell)

        self._draw_walls(painter, walls, snap, cell)
        if snap and opt.known_walls:
            pen = QPen(COLORS["known_wall"], max(1.0, cell * 0.05), Qt.DotLine)
            self._segments(painter, [tuple(map(tuple, w)) for w in debug.get("known_walls", [])], pen)

        if snap and opt.cell_text and cell >= 16:
            painter.setPen(COLORS["text"])
            font = QFont(self.font())
            font.setPixelSize(max(7, int(cell * 0.3)))
            painter.setFont(font)
            for x, y, text in debug.get("cell_text", []):
                painter.drawText(self._cell_rect(x, y), Qt.AlignCenter, str(text))

        if snap:
            self._draw_blocked(painter, snap, cell)
            self._draw_mouse(painter, snap.position, snap.heading, cell)
        elif self._board:
            self._draw_mouse(painter, start, self._board[3], cell, alpha=110)
        self._draw_hover(painter, cell)
        self._draw_labels(painter, width, height, cell)

    def _draw_rule_layers(self, painter: QPainter, snap: Snapshot | None, cell: float) -> None:
        """扩展规则的图层：迷宫外框、规则最优路线（虚线）与转弯点（圆环）。"""
        width, height = self._board[0], self._board[1]
        color = QColor(self._rule.color)
        painter.setPen(QPen(color, max(3.0, cell * 0.12)))
        painter.setBrush(Qt.NoBrush)
        pad = 0.22  # 外框画在外墙之外（单位：格），避免被黑色外墙盖住
        painter.drawRect(QRectF(self._point(-pad, height + pad), self._point(width + pad, -pad)))
        if self.options.rule_optimal and self._optimal and len(self._optimal) > 1:
            faded = QColor(color)
            faded.setAlpha(150)
            self._polyline(painter, self._optimal,
                           QPen(faded, max(1.5, cell * 0.06), Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin))
        if self.options.turns and snap and len(snap.path) > 1:
            pen = QPen(color, max(1.5, cell * 0.07))
            painter.setPen(pen)
            for point, quarters in turn_points(snap.path, self._board[3]):
                center = self._center(point)
                for ring in range(quarters):  # 转 90° 一个圆环，掉头两个
                    r = cell * (0.2 + 0.1 * ring)
                    painter.drawEllipse(center, r, r)

    def _fill_cells(self, painter: QPainter, cells, color: QColor) -> None:
        """用同一颜色填充多个格子。"""
        for x, y in cells:
            painter.fillRect(self._cell_rect(x, y), color)

    def _center(self, cell: Cell) -> QPointF:
        """格子中心的屏幕坐标。"""
        return self._point(cell[0] + 0.5, cell[1] + 0.5)

    def _polyline(self, painter: QPainter, cells, pen: QPen) -> None:
        """沿格子中心画折线。"""
        painter.setPen(pen)
        painter.drawPolyline(QPolygonF([self._center(c) for c in cells]))

    def _segments(self, painter: QPainter, walls, pen: QPen) -> None:
        """画多面墙。"""
        painter.setPen(pen)
        for a, b in (tuple(w) for w in walls):
            p, q = wall_segment(a, b)
            painter.drawLine(self._point(*p), self._point(*q))

    def _draw_walls(self, painter: QPainter, walls, snap: Snapshot | None, cell: float) -> None:
        """画外边界和内部墙。

        运行时：已观测的墙为黑色；未观测的墙在迷雾模式下隐藏，否则为浅灰；
        本步新观测到的墙用红色加粗，表现"被墙挡住"的瞬间。
        """
        width, height = self._board[0], self._board[1]
        thick = max(2.0, cell * 0.1)
        pen = QPen(COLORS["wall"], thick, Qt.SolidLine, Qt.SquareCap)
        if snap is None:
            self._segments(painter, walls, pen)
        else:
            unseen = walls - snap.observed_walls
            if not self.options.fog:
                self._segments(painter, unseen, QPen(COLORS["unseen_wall"], thick * 0.7,
                                                     Qt.SolidLine, Qt.SquareCap))
            self._segments(painter, snap.observed_walls - snap.new_walls, pen)
            self._segments(painter, snap.new_walls, QPen(COLORS["new_wall"], thick * 1.4,
                                                         Qt.SolidLine, Qt.SquareCap))
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(self._point(0, height), self._point(width, 0)))

    def _draw_blocked(self, painter: QPainter, snap: Snapshot, cell: float) -> None:
        """策略试图穿墙时，在那面墙上画红色叉号。"""
        if not snap.blocked:
            return
        (x, y), direction = snap.blocked
        dx, dy = DELTAS[direction]
        center = self._point(x + 0.5 + dx * 0.5, y + 0.5 + dy * 0.5)
        r = cell * 0.25
        painter.setPen(QPen(COLORS["new_wall"], max(2.0, cell * 0.1)))
        painter.drawLine(center + QPointF(-r, -r), center + QPointF(r, r))
        painter.drawLine(center + QPointF(-r, r), center + QPointF(r, -r))

    def _draw_mouse(self, painter: QPainter, cell_xy: Cell, heading: Direction,
                    cell: float, alpha: int = 255) -> None:
        """在格子中心画一个指向朝向的三角形。"""
        painter.save()
        painter.translate(self._center(cell_xy))
        painter.rotate(_ANGLE[heading])
        r = cell * 0.32
        color = QColor(COLORS["mouse"])
        color.setAlpha(alpha)
        painter.setPen(QPen(QColor("#ffffff"), max(1.0, cell * 0.03)))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygonF([QPointF(r, 0), QPointF(-r * 0.75, -r * 0.8),
                                       QPointF(-r * 0.75, r * 0.8)]))
        painter.restore()

    def _draw_hover(self, painter: QPainter, cell: float) -> None:
        """编辑模式下高亮鼠标所指的墙或格子。"""
        if not (self.editable and self._hover):
            return
        kind, target = self._hover
        if kind == "edge":
            p, q = wall_segment(*target)
            painter.setPen(QPen(COLORS["hover"], max(3.0, cell * 0.14), Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(self._point(*p), self._point(*q))
        else:
            painter.setPen(QPen(COLORS["hover"], 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self._cell_rect(*target))

    def _draw_labels(self, painter: QPainter, width: int, height: int, cell: float) -> None:
        """在左侧和下方标注格子坐标；格子太小时隔几个标一次。"""
        painter.setPen(COLORS["label"])
        font = QFont(self.font())
        font.setPixelSize(10)
        painter.setFont(font)
        every = 1 if cell >= 18 else (2 if cell >= 9 else 5)
        for x in range(0, width, every):
            p = self._point(x + 0.5, 0)
            painter.drawText(QRectF(p.x() - 15, p.y() + 5, 30, 14), Qt.AlignCenter, str(x))
        for y in range(0, height, every):
            p = self._point(0, y + 0.5)
            painter.drawText(QRectF(p.x() - 28, p.y() - 7, 20, 14),
                             Qt.AlignRight | Qt.AlignVCenter, str(y))
