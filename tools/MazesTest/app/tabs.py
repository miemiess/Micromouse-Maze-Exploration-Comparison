"""应用的三个功能页及其共用控件。

    RunTab      实时运行：单个算法逐步/连续运行，显示认知地图、规划路线、事件日志和统计；
    CompareTab  同屏对比：同一张地图上 2~4 个算法同步推进，表格对比统计；
    EditorTab   地图编辑：点击加墙/拆墙、设置起点和目标、新建、随机生成、保存 JSON。

共用部件：RunController（定时推进一组 Runner）、ControlBox（种子、预算、播放按钮、速度）、
DisplayBox（显示选项）。算法运行全部通过 simulation.Runner，与实验规则一致。
"""

from pathlib import Path

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPlainTextEdit, QPushButton, QRadioButton, QScrollArea,
    QSlider, QSpinBox, QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from simulation import ROOT, AlgorithmInfo, Direction, Maze, Runner  # 先导入：把 src/ 加入路径
from maze_document import GENERATORS, MazeDocument, generate

from core.rules import BASIC, Ruleset  # noqa: E402
from .rule_bar import populate_algorithm_combo, tinted, update_algorithms
from .export import export_gif, render_image, save_png, snapshot_title, tile_images
from .maze_view import MazeView, ViewOptions

FIGURE_DIR = ROOT / "results" / "local" / "figures"  # 上位机导出的图片，不提交

# 每秒决策次数的档位。
SPEEDS = [1, 2, 4, 8, 15, 30, 60, 120, 300, 1000]

STATUS_TEXT = {"running": "运行中", "success": "到达目标", "no_path": "无路可走",
               "loop_detected": "陷入循环",
               "budget_exceeded": "超出步数预算", "timeout": "计算超时",
               "collision_limit": "达到撞墙上限", "invalid_action": "非法动作", "error": "策略异常"}

DIRECTION_TEXT = {Direction.NORTH: "北 N", Direction.EAST: "东 E",
                  Direction.SOUTH: "南 S", Direction.WEST: "西 W"}

# 统计项：(显示名, Snapshot.stats 中的键)。
STAT_ROWS = [("状态", "status"), ("决策次数", "decisions"), ("移动步数", "steps"), ("撞墙次数", "collisions"), ("已用动作", "actions"),
             ("90° 转向", "turns_90"), ("重复访问", "repeat_visits"),
             ("覆盖率", "coverage"), ("已观测墙", "observed_walls"),
             ("计算时间", "compute_seconds")]

# 已知地图规划器额外显示的统计项（来自规划器的 stats()）。
KNOWN_MAP_STAT_ROWS = [("扩展节点", "expanded_nodes")]

# 扩展规则（有代价层）时显示的规则指标：(显示名, 键)。rule_cost 来自 Runner；其余由页面计算。
RULE_STAT_ROWS = [("规则代价", "rule_cost"), ("规则最优代价", "optimal_rule_cost"),
                  ("代价 / 最优", "rule_cost_ratio")]


def format_cost(rule: Ruleset, value) -> str:
    """按规则代价的单位格式化（如 "4.53 s"）；缺失时为 "-"。"""
    if value is None:
        return "-"
    unit = rule.cost_layer.unit if rule.cost_layer else ""
    return f"{value:g}{(' ' + unit) if unit else ''}"


def rule_metrics(rule: Ruleset, snap, optimal) -> dict:
    """快照的规则指标：规则代价、最优代价，以及成功到达时的代价 / 最优。"""
    cost = snap.stats.get("rule_cost") if snap else None
    ratio = cost / optimal if cost is not None and optimal and snap.status == "success" else None
    return {"rule_cost": format_cost(rule, cost), "optimal_rule_cost": format_cost(rule, optimal),
            "rule_cost_ratio": f"{ratio:.3f}" if ratio is not None else "-"}


def algorithm_description(info, rule: Ruleset) -> str:
    """算法说明行：扩展算法带 [EXT]，为当前规则设计的算法带“为 … 设计”。"""
    tags = (["[EXT]"] if info.layer == "ext" else []) \
        + ([f"为{'、'.join(l.title for l in rule.layers if l.key in info.designed_for)}设计"]
           if info.designed_for_rule(rule) else [])
    return " ".join([*tags, f"{info.module} · {info.doc}"])


def rule_box_style(rule: Ruleset) -> str:
    """规则指标框的样式：规则颜色的边框与浅色底。"""
    return (f"QGroupBox {{ border:2px solid {rule.color}; border-radius:4px; margin-top:12px;"
            f" background:{tinted(rule.color, 22)}; }}"
            f"QGroupBox::title {{ color:{rule.color}; font-weight:bold; subcontrol-origin:margin;"
            " left:8px; padding:0 4px; }")


def format_stat(key: str, value) -> str:
    """把统计值格式化为界面文字；缺失的指标显示为 "-"。"""
    if value is None:
        return "-"
    if key == "status":
        return STATUS_TEXT.get(value, value)
    if key == "coverage":
        return f"{value:.0%}"
    if key == "compute_seconds":
        return f"{value * 1000:.1f} ms"
    return str(value)


def show_document(view: MazeView, doc: MazeDocument) -> None:
    """把正在编辑的 MazeDocument 设置为画布要显示的地图。"""
    view.set_board(doc.width, doc.height, doc.start, doc.start_heading, doc.goals, doc.walls)


# ====================================================================== 共用部件

class RunController(QObject):
    """用定时器推进一组 Runner，并把每次推进产生的快照通知界面。

    Signals:
        advanced(list[list[Snapshot]]): 每个 Runner 本次新产生的快照列表。
        playingChanged(bool): 播放 / 暂停状态变化。
    """

    advanced = Signal(object)
    playingChanged = Signal(bool)

    def __init__(self, parent=None):
        """创建停止状态的控制器，默认速度 8 步/秒。"""
        super().__init__(parent)
        self.runners: list[Runner] = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._batch = 1
        self.set_speed(3)

    @property
    def playing(self) -> bool:
        """是否正在连续运行。"""
        return self.timer.isActive()

    @property
    def all_finished(self) -> bool:
        """所有 Runner 是否都已结束。"""
        return all(r.finished for r in self.runners)

    def set_runners(self, runners: list[Runner]) -> None:
        """替换要推进的 Runner（会先暂停），并通知界面显示初始快照。"""
        self.pause()
        self.runners = runners
        self.advanced.emit([[r.snapshot()] for r in runners])

    def set_speed(self, level: int) -> None:
        """设置速度档位（SPEEDS 的下标）。速度超过约 60 步/秒时每次定时推进多步。"""
        per_second = SPEEDS[max(0, min(level, len(SPEEDS) - 1))]
        interval = max(16, int(1000 / per_second))
        self._batch = max(1, round(per_second * interval / 1000))
        self.timer.setInterval(interval)

    def play(self) -> None:
        """开始连续运行；全部结束时不做任何事。"""
        if self.runners and not self.all_finished and not self.playing:
            self.timer.start()
            self.playingChanged.emit(True)

    def pause(self) -> None:
        """暂停连续运行。"""
        if self.playing:
            self.timer.stop()
            self.playingChanged.emit(False)

    def toggle(self) -> None:
        """在播放和暂停之间切换。"""
        self.pause() if self.playing else self.play()

    def step_once(self) -> None:
        """暂停并让每个未结束的 Runner 前进一步。"""
        self.pause()
        self._advance(1)

    def run_to_end(self) -> None:
        """暂停并把所有 Runner 直接运行到结束。"""
        self.pause()
        self._advance(None)

    def reset(self) -> None:
        """暂停并把所有 Runner 重置到起点。"""
        self.pause()
        self.advanced.emit([[r.reset()] for r in self.runners])

    def _advance(self, count: int | None) -> None:
        """让每个 Runner 最多前进 count 步（None 表示到结束），然后发出 advanced。"""
        batches = []
        for runner in self.runners:
            snaps = []
            while not runner.finished and (count is None or len(snaps) < count):
                snaps.append(runner.step())
            batches.append(snaps)
        self.advanced.emit(batches)
        if self.all_finished:
            self.pause()

    def _tick(self) -> None:
        """定时器回调。"""
        self._advance(self._batch)


class ControlBox(QGroupBox):
    """运行控制：随机种子、动作预算、重置/单步/运行/跑完按钮、速度滑块。

    Signals:
        settingsChanged: 种子或预算改变，需要重新创建 Runner。
    """

    settingsChanged = Signal()

    def __init__(self, controller: RunController, parent=None):
        """创建控件并连接到 controller。"""
        super().__init__("运行控制", parent)
        self.controller = controller

        self.seed = QSpinBox(minimum=-1, maximum=10**6, value=-1)
        self.seed.setSpecialValueText("无")
        self.seed.setToolTip("传给策略的随机种子；确定性算法会忽略它")
        self.budget = QSpinBox(minimum=0, maximum=10**6, value=0, singleStep=100)
        self.budget.setSpecialValueText("默认 (20 × 格子数)")
        self.seed.valueChanged.connect(lambda _value: self.settingsChanged.emit())
        self.budget.valueChanged.connect(lambda _value: self.settingsChanged.emit())

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("⟲ 重置")
        self.step_button = QPushButton("⏭ 单步")
        self.play_button = QPushButton("▶ 运行")
        self.end_button = QPushButton("⏩ 跑完")
        for button, slot in ((self.reset_button, controller.reset),
                             (self.step_button, controller.step_once),
                             (self.play_button, controller.toggle),
                             (self.end_button, controller.run_to_end)):
            button.clicked.connect(slot)
            buttons.addWidget(button)
        controller.playingChanged.connect(
            lambda playing: self.play_button.setText("⏸ 暂停" if playing else "▶ 运行"))

        self.speed = QSlider(Qt.Horizontal, minimum=0, maximum=len(SPEEDS) - 1, value=3)
        self.speed_label = QLabel()
        self.speed.valueChanged.connect(self._speed_changed)
        self._speed_changed(self.speed.value())
        speed_row = QHBoxLayout()
        speed_row.addWidget(self.speed, 1)
        speed_row.addWidget(self.speed_label)

        form = QFormLayout(self)
        form.addRow("随机种子", self.seed)
        form.addRow("动作预算", self.budget)
        form.addRow(buttons)
        form.addRow("速度", speed_row)

    def seed_value(self) -> int | None:
        """当前种子；"无" 时为 None。"""
        return None if self.seed.value() < 0 else self.seed.value()

    def budget_value(self) -> int | None:
        """当前动作预算；"默认" 时为 None。"""
        return self.budget.value() or None

    def _speed_changed(self, level: int) -> None:
        """更新速度档位和文字。"""
        self.controller.set_speed(level)
        self.speed_label.setText(f"{SPEEDS[level]} 步/秒")


class DisplayBox(QGroupBox):
    """显示选项复选框。

    Signals:
        changed(ViewOptions): 任一选项改变。
    """

    changed = Signal(object)

    _ITEMS = [("fog", "迷雾模式（只显示电脑鼠已观测到的墙）"),
              ("plan", "规划路线（紫色虚线）"),
              ("cell_text", "格子文字（距离 / 访问顺序）"),
              ("cell_color", "策略着色（如 DFS 当前分支）"),
              ("path", "已走路径"),
              ("known_walls", "策略认知墙（橙色点线）"),
              ("turns", "转弯点（扩展规则：规则色圆环，掉头为双环）"),
              ("rule_optimal", "规则最优路线（扩展规则：规则色点划线）")]

    def __init__(self, parent=None):
        """按 ViewOptions 的默认值创建复选框。"""
        super().__init__("显示", parent)
        defaults = ViewOptions()
        layout = QVBoxLayout(self)
        self.boxes = {}
        for key, text in self._ITEMS:
            box = QCheckBox(text, checked=getattr(defaults, key))
            box.toggled.connect(lambda _checked: self.changed.emit(self.options()))
            layout.addWidget(box)
            self.boxes[key] = box
        legend = QLabel("图例：<span style='color:#1f1f1f'>■</span> 已观测墙 "
                        "<span style='color:#b0b0b0'>■</span> 未观测墙 "
                        "<span style='color:#e63946'>■</span> 刚发现的墙 "
                        "<span style='color:#d62828'>▲</span> 电脑鼠")
        legend.setWordWrap(True)
        layout.addWidget(legend)

    def options(self) -> ViewOptions:
        """当前选项。"""
        return ViewOptions(**{key: box.isChecked() for key, box in self.boxes.items()})


def ask_save_path(parent, title: str, default_name: str, file_filter: str) -> Path | None:
    """弹出保存对话框，默认放在 results/local/figures/；取消时返回 None。"""
    path, _ = QFileDialog.getSaveFileName(parent, title, str(FIGURE_DIR / default_name),
                                          file_filter)
    return Path(path) if path else None


def run_with_wait_cursor(parent, action, done_message: str) -> None:
    """执行可能较慢的导出操作：显示等待光标，失败时弹出错误，成功时在状态栏提示。"""
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        path = action()
    except (OSError, RuntimeError, ValueError) as exc:
        QApplication.restoreOverrideCursor()
        QMessageBox.warning(parent, "导出失败", str(exc))
        return
    QApplication.restoreOverrideCursor()
    window = parent.window()
    if hasattr(window, "statusBar"):
        window.statusBar().showMessage(f"{done_message}：{path}", 8000)


def side_panel(*widgets, width: int = 370) -> QScrollArea:
    """把若干控件竖排放进固定宽度、只能纵向滚动的侧边栏。"""
    inner = QWidget()
    layout = QVBoxLayout(inner)
    layout.setContentsMargins(4, 4, 8, 4)
    for widget in widgets:
        layout.addWidget(widget)
    layout.addStretch(1)
    area = QScrollArea()
    area.setWidget(inner)
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setFixedWidth(width)
    area.setFrameShape(QScrollArea.NoFrame)
    return area


# ====================================================================== 实时运行

class RunTab(QWidget):
    """实时运行单个算法，展示算法真实的决策过程。

    同一个页面类用于两类算法：未知地图探索（"实时运行"页）和已知地图规划（"已知地图规划"页）。
    两类算法按 README 约定分开比较，因此各占一页，不会出现在同一个列表中。
    """

    def __init__(self, strategies: dict[str, AlgorithmInfo], parent=None, *,
                 known_map: bool = False):
        """创建画布、算法选择、运行控制、显示选项、统计和事件日志。

        Args:
            strategies: 本页可选的算法（只包含一类）。
            parent: 父控件。
            known_map: 是否为已知地图规划页（标题、说明和统计项不同）。
        """
        super().__init__(parent)
        self.rule = BASIC
        self.strategies = strategies
        self.known_map = known_map
        self.maze: Maze | None = None
        self.runner: Runner | None = None
        self._pending_walls = frozenset()  # 上一次移动新发现、策略还未处理的墙
        self.controller = RunController(self)
        self.controller.advanced.connect(self._on_advanced)

        self.view = MazeView()
        self.message = QLabel(alignment=Qt.AlignCenter)
        self.message.setStyleSheet("color:#c0392b")
        self.message.hide()

        algo_box = QGroupBox("已知地图算法" if known_map else "探索算法（未知地图）")
        self.algorithm = QComboBox()
        populate_algorithm_combo(self.algorithm, strategies, self.rule)
        self.algorithm.currentTextChanged.connect(self.rebuild)
        self.description = QLabel(wordWrap=True)
        self.description.setStyleSheet("color:#555")
        algo_layout = QVBoxLayout(algo_box)
        if known_map:
            note = QLabel("一开始就拿到完整地图，用作参照；与探索算法分开比较，不进入同屏对比。")
            note.setWordWrap(True)
            note.setStyleSheet("color:#d68910")
            algo_layout.addWidget(note)
        algo_layout.addWidget(self.algorithm)
        algo_layout.addWidget(self.description)

        self.controls = ControlBox(self.controller)
        self.controls.settingsChanged.connect(self.rebuild)
        self.display = DisplayBox()
        self.display.changed.connect(self.view.set_options)

        stats_box = QGroupBox("统计")
        stats_form = QFormLayout(stats_box)
        self.stat_labels = {}
        for title, key in STAT_ROWS + (KNOWN_MAP_STAT_ROWS if known_map else []):
            self.stat_labels[key] = QLabel("-")
            stats_form.addRow(title, self.stat_labels[key])

        # 规则指标：只在扩展规则（有代价层）时显示，边框为规则颜色。
        self.rule_box = QGroupBox()
        rule_form = QFormLayout(self.rule_box)
        self.rule_formula = QLabel(wordWrap=True)
        rule_form.addRow(self.rule_formula)
        self.rule_labels = {}
        for title, key in RULE_STAT_ROWS:
            self.rule_labels[key] = QLabel("-")
            rule_form.addRow(title, self.rule_labels[key])
        self.rule_box.hide()
        self._optimal: tuple[float, list] | None = None

        log_box = QGroupBox("事件")
        self.log = QPlainTextEdit(readOnly=True)
        self.log.setMaximumBlockCount(1000)
        self.log.setMinimumHeight(140)
        QVBoxLayout(log_box).addWidget(self.log)

        export_box = QGroupBox("导出")
        export_row = QHBoxLayout(export_box)
        png_button = QPushButton("当前画面 PNG…")
        png_button.clicked.connect(self.export_png)
        gif_button = QPushButton("完整过程 GIF…")
        gif_button.setToolTip("按当前算法、种子、预算和显示选项从头运行一次并录制")
        gif_button.clicked.connect(self.export_gif)
        export_row.addWidget(png_button)
        export_row.addWidget(gif_button)

        left = QVBoxLayout()
        left.addWidget(self.message)
        left.addWidget(self.view, 1)
        layout = QHBoxLayout(self)
        layout.addLayout(left, 1)
        layout.addWidget(side_panel(algo_box, self.controls, self.display, self.rule_box,
                                    stats_box, export_box, log_box))

    def set_rule(self, rule: Ruleset) -> None:
        """切换规则：更新可用算法与规则指标框，并从起点重新运行。"""
        self.rule = rule
        populate_algorithm_combo(self.algorithm, self.strategies, rule)
        cost = rule.cost_layer
        self.rule_box.setVisible(cost is not None)
        if cost is not None:
            self.rule_box.setTitle(f"规则指标 · {rule.title}")
            self.rule_box.setStyleSheet(rule_box_style(rule))
            self.rule_formula.setText(f"<b style='color:{rule.color}'>{cost.formula}</b>")
        self.rebuild()

    def set_maze(self, maze: Maze | None, message: str = "") -> None:
        """切换地图并重新开始；maze 为 None 时显示 message 并禁用运行。"""
        self.maze = maze
        self.message.setText(message)
        self.message.setVisible(maze is None)
        self.setEnabled(True)
        self.rebuild()

    def rebuild(self) -> None:
        """按当前地图、算法、种子和预算新建 Runner。"""
        name = self.algorithm.currentData()
        info = self.strategies.get(name)
        self.description.setText(algorithm_description(info, self.rule) if info else "没有这一类算法")
        self.log.clear()
        if self.maze is None or info is None:
            self.runner = None
            self.controller.set_runners([])
            self.view.set_snapshot(None)
            return
        self.view.set_maze(self.maze)
        self._optimal = self.rule.optimal_plan(self.maze) if self.rule.cost_layer else None
        self.view.set_rule(self.rule, self._optimal[1] if self._optimal else None)
        try:
            self.runner = Runner(self.maze, info.create(), seed=self.controls.seed_value(),
                                 rule=self.rule, max_steps=self.controls.budget_value())
        except Exception as exc:  # 策略构造函数出错
            self.runner = None
            self.controller.set_runners([])
            self.log.appendPlainText(f"无法创建策略 {name}: {exc}")
            return
        self.log.appendPlainText(
            f"地图 {self.maze.maze_id}，算法 {name}，预算 {self.runner.env.max_steps} 步，规则：{self.rule.title}")
        self.controller.set_runners([self.runner])

    def export_png(self) -> None:
        """把当前画面（含当前显示选项）导出为高分辨率 PNG。"""
        if self.runner is None:
            return
        snap = self.runner.snapshot()
        path = ask_save_path(self, "导出 PNG",
                             f"{self.maze.maze_id}_{self.runner.name}_step{snap.stats['steps']}.png",
                             "PNG 图片 (*.png)")
        if path:
            run_with_wait_cursor(self, lambda: save_png(render_image(
                self.maze, snap, options=self.display.options(),
                title=snapshot_title(self.maze, self.runner.name, snap, self.rule), rule=self.rule), path), "已导出")

    def export_gif(self) -> None:
        """按当前设置从头运行一次，把完整过程导出为 GIF。"""
        info = self.strategies.get(self.algorithm.currentData())
        if self.maze is None or info is None:
            return
        path = ask_save_path(self, "导出 GIF", f"{self.maze.maze_id}_{info.name}.gif",
                             "GIF 动画 (*.gif)")
        if path:
            run_with_wait_cursor(self, lambda: export_gif(
                self.maze, info.create, path, seed=self.controls.seed_value(),
                rule=self.rule, max_steps=self.controls.budget_value(), options=self.display.options()),
                "已导出")

    def _on_advanced(self, batches) -> None:
        """记录本次推进中的事件，并用最后一个快照刷新画面和统计。"""
        if not batches or not batches[0]:
            return
        for snap in batches[0]:
            self._log_events(snap)
            # 墙在移动到新格时被观测到，策略在下一次决策时才据此改变路线。
            self._pending_walls = snap.new_walls if snap.moved or snap.decision == 0 else frozenset()
        last = batches[0][-1]
        self.view.set_snapshot(last)
        for key, label in self.stat_labels.items():
            label.setText(format_stat(key, last.stats.get(key)))
        if self.rule.cost_layer:
            values = rule_metrics(self.rule, last, self._optimal[0] if self._optimal else None)
            for key, label in self.rule_labels.items():
                label.setText(values[key])

    def _log_events(self, snap) -> None:
        """把"被墙挡住后重新规划"、"试图穿墙"、"运行结束"等事件写入日志。"""
        prefix = f"[{snap.stats['steps']:>4}] {snap.position}"
        if snap.replanned:
            cause = self._pending_walls
            self.log.appendPlainText(
                f"{prefix} 上一格发现 {len(cause)} 面新墙 → 路线重新规划" if cause
                else f"{prefix} 路线重新规划")
        if snap.blocked:
            self.log.appendPlainText(f"{prefix} 试图向 {snap.blocked[1].value} 撞墙")
        if snap.status != "running" and snap.decision > 0:
            stats = snap.stats
            self.log.appendPlainText(
                f"结束：{STATUS_TEXT.get(snap.status, snap.status)}；{stats['steps']} 步，"
                f"{stats['turns_90']} 次转向，{stats['repeat_visits']} 次重复访问，"
                f"覆盖 {stats['coverage']:.0%}"
                + (f"；规则代价 {format_cost(self.rule, stats.get('rule_cost'))}" if self.rule.cost_layer else ""))
            if self.runner and self.runner.error:
                self.log.appendPlainText(self.runner.error)
            if self.runner and getattr(self.runner.algorithm, "loop_detected", False):
                self.log.appendPlainText("原因：回到了走过的（位置, 朝向），之后会无限重复，判定陷入循环")


# ====================================================================== 同屏对比

class CompareTab(QWidget):
    """同一张地图上多个算法同步运行，并排显示并用表格对比统计。"""

    MAX_ALGORITHMS = 4
    COLUMNS = [("算法", None), ("状态", "status"), ("移动步数", "steps"), ("撞墙次数", "collisions"), ("已用动作", "actions"),
               ("90° 转向", "turns_90"), ("重复访问", "repeat_visits"),
               ("覆盖率", "coverage"), ("计算时间", "compute_seconds")]

    def __init__(self, strategies: dict[str, AlgorithmInfo], parent=None):
        """创建算法勾选列表、运行控制、显示选项、画布网格和统计表。"""
        super().__init__(parent)
        self.rule = BASIC
        self.strategies = strategies
        self.maze: Maze | None = None
        self.runners: list[Runner] = []
        self.views: list[tuple[QLabel, MazeView]] = []
        self.controller = RunController(self)
        self.controller.advanced.connect(self._on_advanced)

        algo_box = QGroupBox(f"参与对比的算法（最多 {self.MAX_ALGORITHMS} 个）")
        self.algorithms = QListWidget()
        self.algorithms.setSelectionMode(QAbstractItemView.NoSelection)
        for i, name in enumerate(strategies):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if i < self.MAX_ALGORITHMS else Qt.Unchecked)
            self.algorithms.addItem(item)
        update_algorithms(self.algorithms, strategies, self.rule)
        self.algorithms.setMaximumHeight(130)
        self.algorithms.itemChanged.connect(self._on_algorithm_toggled)
        QVBoxLayout(algo_box).addWidget(self.algorithms)

        self.controls = ControlBox(self.controller)
        self.controls.settingsChanged.connect(self.rebuild)
        self.display = DisplayBox()
        self.display.changed.connect(self._apply_options)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.message = QLabel(alignment=Qt.AlignCenter)
        self.message.setStyleSheet("color:#c0392b")
        self.columns = list(self.COLUMNS)
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels([c[0] for c in self.columns])
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMaximumHeight(36 + 30 * self.MAX_ALGORITHMS)

        splitter = QSplitter(Qt.Vertical)
        top = QWidget()
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.message)
        top_layout.addWidget(self.grid_host, 1)
        splitter.addWidget(top)
        splitter.addWidget(self.table)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 1)

        export_button = QPushButton("导出对比图 PNG…")
        export_button.clicked.connect(self.export_png)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter, 1)
        layout.addWidget(side_panel(algo_box, self.controls, self.display, export_button))

    def export_png(self) -> None:
        """把所有算法的当前画面拼成一张对比图导出。"""
        if not self.runners:
            return
        names = "_vs_".join(r.name for r in self.runners)
        path = ask_save_path(self, "导出对比图", f"{self.maze.maze_id}_{names}.png",
                             "PNG 图片 (*.png)")
        if not path:
            return

        def build():
            images = [render_image(self.maze, r.snapshot(), options=self.display.options(),
                                   size=700, title=snapshot_title(self.maze, r.name, r.snapshot(), self.rule),
                                   rule=self.rule)
                      for r in self.runners]
            return save_png(tile_images(images, 1 if len(images) == 1 else 2), path)
        run_with_wait_cursor(self, build, "已导出")

    def set_rule(self, rule: Ruleset) -> None:
        """切换规则：更新可用算法与表格列（扩展规则下加“规则代价”，并按它评最优），重新运行。"""
        self.rule = rule
        update_algorithms(self.algorithms, self.strategies, rule)
        self.columns = self.COLUMNS + ([("规则代价", "rule_cost")] if rule.cost_layer else [])
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([c[0] for c in self.columns])
        self.rebuild()

    def selected(self) -> list[str]:
        """被勾选的算法名。"""
        return [self.algorithms.item(i).text() for i in range(self.algorithms.count())
                if self.algorithms.item(i).flags() & Qt.ItemIsEnabled
                and self.algorithms.item(i).checkState() == Qt.Checked]

    def _on_algorithm_toggled(self, item: QListWidgetItem) -> None:
        """勾选变化时重建；超过上限时撤销本次勾选。"""
        if len(self.selected()) > self.MAX_ALGORITHMS:
            self.algorithms.blockSignals(True)
            item.setCheckState(Qt.Unchecked)
            self.algorithms.blockSignals(False)
            return
        self.rebuild()

    def set_maze(self, maze: Maze | None, message: str = "") -> None:
        """切换地图并重新开始；maze 为 None 时显示 message。"""
        self.maze = maze
        self.message.setText(message)
        self.message.setVisible(maze is None)
        self.rebuild()

    def rebuild(self) -> None:
        """按勾选的算法新建 Runner 和对应画布：1 个占满，2 个左右并排，3~4 个排成 2×2。"""
        for label, view in self.views:
            label.deleteLater()
            view.deleteLater()
        self.views, self.runners = [], []
        names = self.selected() if self.maze else []
        for name in names:
            try:
                self.runners.append(Runner(self.maze, self.strategies[name].create(),
                                           seed=self.controls.seed_value(),
                                           rule=self.rule, max_steps=self.controls.budget_value()))
            except Exception as exc:
                self.message.setText(f"无法创建策略 {name}: {exc}")
                self.message.show()
        columns = 1 if len(self.runners) <= 1 else 2
        optimal = self.rule.optimal_plan(self.maze) if self.rule.cost_layer and self.maze else None
        for i, runner in enumerate(self.runners):
            label = QLabel(alignment=Qt.AlignCenter)
            label.setStyleSheet("font-weight:bold")
            view = MazeView()
            view.set_options(self.display.options())
            view.set_maze(self.maze)
            view.set_rule(self.rule, optimal[1] if optimal else None)
            row, col = divmod(i, columns)
            self.grid.addWidget(label, row * 2, col)
            self.grid.addWidget(view, row * 2 + 1, col)
            self.grid.setRowStretch(row * 2 + 1, 1)
            self.views.append((label, view))
        self.table.setRowCount(len(self.runners))
        self.controller.set_runners(self.runners)

    def _apply_options(self, options: ViewOptions) -> None:
        """把显示选项应用到所有画布。"""
        for _, view in self.views:
            view.set_options(options)

    def _on_advanced(self, batches) -> None:
        """刷新每个画布、标题和统计表；成功运行中最优的一行加粗标绿。

        基础规则按步数评最优；扩展规则（有代价层）按规则代价评最优，表格多一列“规则代价”。
        """
        snaps = [batch[-1] if batch else runner.snapshot()
                 for batch, runner in zip(batches, self.runners)]
        score_key = "rule_cost" if self.rule.cost_layer else "steps"
        for (label, view), runner, snap in zip(self.views, self.runners, snaps):
            view.set_snapshot(snap)
            extra = (f" · 代价 {format_cost(self.rule, snap.stats.get('rule_cost'))}"
                     if self.rule.cost_layer else "")
            label.setText(f"{runner.name} · {STATUS_TEXT.get(snap.status, snap.status)}"
                          f" · {snap.stats['steps']} 步{extra}")
        finished = [s.stats[score_key] for s in snaps if s.status == "success"]
        best = min(finished) if finished else None
        for row, (runner, snap) in enumerate(zip(self.runners, snaps)):
            is_best = best is not None and snap.status == "success" and snap.stats[score_key] == best
            for col, (_, key) in enumerate(self.columns):
                if key == "rule_cost":
                    text = format_cost(self.rule, snap.stats.get(key))
                else:
                    text = runner.name if key is None else format_stat(key, snap.stats.get(key))
                item = QTableWidgetItem(text)
                if is_best:
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                    item.setBackground(QColor("#d8f3dc"))
                self.table.setItem(row, col, item)


# ====================================================================== 地图编辑

class EditorTab(QWidget):
    """可视化编辑迷宫，保存为项目 JSON 格式。

    Signals:
        documentEdited: 当前地图内容被修改。
        documentReplaced(MazeDocument): 新建或随机生成了另一张地图。
        saveRequested: 点击了"保存到地图库"，由主窗口写入地图库。
        exportRequested: 点击了"导出…"，由主窗口选择位置导出。
        batchGenerated(list[MazeDocument]): 批量生成了一组地图，由主窗口存入地图库。
    """

    documentEdited = Signal()
    documentReplaced = Signal(object)
    saveRequested = Signal()
    exportRequested = Signal()
    batchGenerated = Signal(object)

    def __init__(self, parent=None):
        """创建可编辑画布和工具栏。"""
        super().__init__(parent)
        self.document: MazeDocument | None = None
        self.confirm_discard = lambda: True  # 由主窗口替换为"未保存修改"确认对话框

        self.view = MazeView(editable=True)
        self.view.edgeClicked.connect(self._on_edge_clicked)
        self.view.cellClicked.connect(self._on_cell_clicked)

        tool_box = QGroupBox("编辑工具")
        tool_layout = QVBoxLayout(tool_box)
        self.tools = QButtonGroup(self)
        for i, (key, text) in enumerate([("wall", "墙：点击格子边缘加墙 / 拆墙"),
                                         ("start", "起点：点击格子设为起点"),
                                         ("goal", "目标：点击格子加入 / 移出目标")]):
            button = QRadioButton(text, checked=(i == 0))
            button.setProperty("tool", key)
            self.tools.addButton(button)
            tool_layout.addWidget(button)
        self.tools.buttonToggled.connect(self._on_tool_changed)

        props_box = QGroupBox("地图属性")
        props = QFormLayout(props_box)
        self.maze_id = QLineEdit()
        self.maze_id.editingFinished.connect(self._on_id_edited)
        self.heading = QComboBox()
        for direction, text in DIRECTION_TEXT.items():
            self.heading.addItem(text, direction)
        self.heading.currentIndexChanged.connect(self._on_heading_changed)
        self.size_label = QLabel()
        self.source_label = QLabel(wordWrap=True)
        props.addRow("地图 ID", self.maze_id)
        props.addRow("起始朝向", self.heading)
        props.addRow("尺寸", self.size_label)
        props.addRow("来源", self.source_label)

        bulk_box = QGroupBox("批量操作")
        bulk = QHBoxLayout(bulk_box)
        clear_button = QPushButton("清空内部墙")
        clear_button.clicked.connect(lambda: self._edit(lambda d: d.clear_walls()))
        fill_button = QPushButton("全部加墙")
        fill_button.clicked.connect(lambda: self._edit(lambda d: d.fill_walls()))
        bulk.addWidget(clear_button)
        bulk.addWidget(fill_button)

        new_box = QGroupBox("新建 / 随机生成")
        new = QFormLayout(new_box)
        self.new_width = QSpinBox(minimum=2, maximum=32, value=16)
        self.new_height = QSpinBox(minimum=2, maximum=32, value=16)
        size_row = QHBoxLayout()
        size_row.addWidget(self.new_width)
        size_row.addWidget(QLabel("×"))
        size_row.addWidget(self.new_height)
        self.gen_algorithm = QComboBox()
        for key, (title, _, feature) in GENERATORS.items():
            self.gen_algorithm.addItem(f"{title}（{feature}）", key)
        self.gen_algorithm.setToolTip("不同生成算法的迷宫结构不同；实验只用一种生成器，结论可能有偏差")
        self.gen_seed = QSpinBox(minimum=0, maximum=10**6, value=1)
        self.gen_loops = QDoubleSpinBox(minimum=0, maximum=100, value=0, suffix=" %", decimals=0)
        self.gen_loops.setToolTip("生成完美迷宫后再随机拆掉的内部墙比例，用来制造环路")
        blank_button = QPushButton("新建空白地图")
        blank_button.clicked.connect(self._new_blank)
        gen_button = QPushButton("随机生成")
        gen_button.clicked.connect(self._generate)
        self.batch_count = QSpinBox(minimum=1, maximum=500, value=10, suffix=" 张")
        self.batch_count.setToolTip("从当前种子开始连续编号，例如种子 1、数量 10 → 种子 1～10")
        batch_button = QPushButton("批量生成到地图库")
        batch_button.setToolTip("按上面的参数生成多张地图，存入地图库；同名文件跳过")
        batch_button.clicked.connect(self._generate_batch)
        new.addRow("宽 × 高", size_row)
        new.addRow("生成算法", self.gen_algorithm)
        new.addRow("随机种子", self.gen_seed)
        new.addRow("环路比例", self.gen_loops)
        row = QHBoxLayout()
        row.addWidget(blank_button)
        row.addWidget(gen_button)
        new.addRow(row)
        batch_row = QHBoxLayout()
        batch_row.addWidget(self.batch_count)
        batch_row.addWidget(batch_button, 1)
        new.addRow("批量", batch_row)

        check_box = QGroupBox("检查")
        self.check_label = QLabel(wordWrap=True)
        QVBoxLayout(check_box).addWidget(self.check_label)

        file_box = QGroupBox("文件")
        file_row = QHBoxLayout(file_box)
        save_button = QPushButton("💾 保存到地图库")
        save_button.setToolTip("保存到 mazes/classic/<地图 ID>.json；外部迷宫（external_*）只读，修改后自动另存为新地图")
        save_button.clicked.connect(self.saveRequested)
        export_button = QPushButton("导出…")
        export_button.setToolTip("把当前地图另存一份到任意位置，不改变当前地图对应的文件")
        export_button.clicked.connect(self.exportRequested)
        file_row.addWidget(save_button)
        file_row.addWidget(export_button)

        layout = QHBoxLayout(self)
        layout.addWidget(self.view, 1)
        layout.addWidget(side_panel(tool_box, props_box, bulk_box, new_box, check_box,
                                    file_box))

    # -- 文档 -------------------------------------------------------------
    def set_document(self, doc: MazeDocument) -> None:
        """切换正在编辑的地图。"""
        self.document = doc
        self.refresh()

    def refresh(self) -> None:
        """根据文档刷新画布、属性和检查结果。"""
        doc = self.document
        if doc is None:
            return
        show_document(self.view, doc)
        self.maze_id.setText(doc.maze_id)
        self.heading.blockSignals(True)
        self.heading.setCurrentIndex(list(DIRECTION_TEXT).index(doc.start_heading))
        self.heading.blockSignals(False)
        self.size_label.setText(f"{doc.width} × {doc.height}，内部墙 {len(doc.walls)} 面")
        path = doc.path.name if doc.path else "未保存"
        text = f"{path} · {doc.metadata.get('source', '-')}"
        if doc.read_only:
            text += ("<br><span style='color:#d68910'>🔒 外部迷宫只读：可以编辑，"
                     "保存时自动另存为新地图</span>")
        elif doc.metadata.get("derived_from"):
            text += f"<br>改自 {doc.metadata['derived_from']}"
        self.source_label.setText(text)
        errors, warnings = doc.check()
        lines = [f"<span style='color:#c0392b'>错误：{e}</span>" for e in errors]
        lines += [f"<span style='color:#d68910'>提醒：{w}</span>" for w in warnings]
        self.check_label.setText("<br>".join(lines) or
                                 "<span style='color:#2e7d32'>地图有效，目标可达</span>")

    def _edit(self, action) -> None:
        """对文档执行一次修改，然后刷新并通知主窗口。"""
        if self.document is None:
            return
        revision = self.document.revision
        action(self.document)
        if self.document.revision != revision:
            self.refresh()
            self.documentEdited.emit()

    # -- 交互 -------------------------------------------------------------
    def _current_tool(self) -> str:
        """当前选中的工具："wall"、"start" 或 "goal"。"""
        return self.tools.checkedButton().property("tool")

    def _on_tool_changed(self, *_args) -> None:
        """墙工具悬停高亮边，其余工具悬停高亮格子。"""
        self.view.edit_target = "edge" if self._current_tool() == "wall" else "cell"

    def _on_edge_clicked(self, a, b) -> None:
        """墙工具：切换两格之间的墙。"""
        if self._current_tool() == "wall":
            self._edit(lambda d: d.toggle_wall(a, b))

    def _on_cell_clicked(self, cell, _button) -> None:
        """起点 / 目标工具：设置起点或切换目标。"""
        tool = self._current_tool()
        if tool == "start":
            self._edit(lambda d: d.set_start(cell))
        elif tool == "goal":
            self._edit(lambda d: d.toggle_goal(cell))

    def _on_heading_changed(self, index: int) -> None:
        """修改起始朝向。"""
        heading = self.heading.itemData(index)
        self._edit(lambda d: d.set_start(d.start, heading))

    def _on_id_edited(self) -> None:
        """修改地图 ID（空白时恢复原值）。"""
        text = self.maze_id.text().strip()
        doc = self.document
        if doc is None or not text or text == doc.maze_id:
            self.maze_id.setText(doc.maze_id if doc else "")
            return

        def rename(d):
            d.maze_id = text
            d._changed()
        self._edit(rename)

    def _new_blank(self) -> None:
        """新建没有内部墙的空白地图。"""
        if self.confirm_discard():
            w, h = self.new_width.value(), self.new_height.value()
            doc = MazeDocument(f"handmade_{w}x{h}", w, h)
            doc.dirty = True
            self.documentReplaced.emit(doc)

    def _generate_one(self, seed: int) -> MazeDocument:
        """按当前的尺寸、生成算法和环路比例，用指定种子生成一张地图。"""
        return generate(self.new_width.value(), self.new_height.value(), seed=seed,
                        loop_fraction=self.gen_loops.value() / 100,
                        algorithm=self.gen_algorithm.currentData())

    def _generate(self) -> None:
        """按尺寸、生成算法、种子和环路比例随机生成一张地图，并打开它。"""
        if self.confirm_discard():
            self.documentReplaced.emit(self._generate_one(self.gen_seed.value()))

    def _generate_batch(self) -> None:
        """从当前种子开始连续生成多张地图，交给主窗口存入地图库。"""
        start = self.gen_seed.value()
        self.batchGenerated.emit([self._generate_one(seed)
                                  for seed in range(start, start + self.batch_count.value())])
