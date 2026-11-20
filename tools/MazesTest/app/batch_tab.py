"""批量实验页（D2）：勾选多张地图和多个算法，批量运行并导出结果。不做动画演示。

运行、统计和导出全部调用 src/core/experiments.py（与命令行共用），本页只负责：
    - 选择地图（筛选、全选、按类别选）与算法；
    - 设置种子、重复次数、移动预算、是否测内存；
    - 分批推进运行（界面保持响应，可随时停止），显示进度；
    - 结束后导出 runs.csv / summary.csv / summary.md / metadata.json / figures，并显示汇总表。
"""

from datetime import datetime
from pathlib import Path
from time import perf_counter

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from maze_document import MapLibrary
from core.experiments import LOCAL_RESULTS, ExperimentRun, write_outputs
from simulation import KNOWN_MAP, ROOT, AlgorithmInfo

CORE_MAPS = ("external_1stworld", "external_japan2017ef", "external_uk2011f")
SUMMARY_COLUMNS = [("算法", "algorithm"), ("成功", "success"), ("运行", "runs"),
                   ("步数/最短路（均值）", "mean_ratio"), ("中位数", "median_ratio"),
                   ("平均转向", "mean_turns"), ("平均重复访问", "mean_repeat_visits"),
                   ("计算 ms（中位数）", "median_compute_ms"), ("扩展节点", "mean_expanded_nodes")]
TIME_SLICE = 0.05  # 每次定时器回调最多运行的秒数，保证界面响应


def _checkable(text: str, data, checked: bool = False) -> QListWidgetItem:
    """创建带复选框的列表项。"""
    item = QListWidgetItem(text)
    item.setData(Qt.UserRole, data)
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    return item


class BatchTab(QWidget):
    """批量实验：多地图 × 多算法，运行并导出结果。"""

    def __init__(self, library: MapLibrary, algorithms: dict[str, AlgorithmInfo], parent=None):
        """创建地图列表、算法列表、设置、进度和汇总表。

        Args:
            library: 地图库（地图列表来源）。
            algorithms: 可选算法（探索与已知地图两类都可选）。
            parent: 父控件。
        """
        super().__init__(parent)
        self.library = library
        self.run: ExperimentRun | None = None
        self.tasks: list = []
        self.position = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # -- 地图 --
        map_box = QGroupBox("地图")
        self.filter = QLineEdit(placeholderText="按名称筛选，例如 wilson、_l30、japan")
        self.filter.textChanged.connect(self._apply_filter)
        self.maps = QListWidget()
        self.maps.setSelectionMode(QAbstractItemView.NoSelection)
        self.maps.itemChanged.connect(lambda _item: self._update_count())
        self.map_count = QLabel()
        buttons = QHBoxLayout()
        for text, action in (("全选（可见）", lambda: self._check_visible(True)),
                             ("全不选", lambda: self._check(lambda name: False)),
                             ("外部迷宫库", lambda: self._check(lambda n: n.startswith("external_"))),
                             ("生成迷宫", lambda: self._check(lambda n: n.startswith("gen_"))),
                             ("核心 3 张", lambda: self._check(lambda n: n in CORE_MAPS)),
                             ("刷新", self.reload_maps)):
            button = QPushButton(text)
            button.clicked.connect(action)
            buttons.addWidget(button)
        map_layout = QVBoxLayout(map_box)
        map_layout.addWidget(self.filter)
        map_layout.addLayout(buttons)
        map_layout.addWidget(self.maps, 1)
        map_layout.addWidget(self.map_count)

        # -- 算法 --
        algo_box = QGroupBox("算法")
        self.algorithms = QListWidget()
        self.algorithms.setSelectionMode(QAbstractItemView.NoSelection)
        for name, info in algorithms.items():
            tag = "已知地图（参照）" if info.mode == KNOWN_MAP else "探索"
            self.algorithms.addItem(_checkable(f"{name}　[{tag}]", name, checked=True))
        self.algorithms.setMaximumHeight(200)
        QVBoxLayout(algo_box).addWidget(self.algorithms)

        # -- 设置 --
        settings_box = QGroupBox("设置")
        form = QFormLayout(settings_box)
        self.seed_first = QSpinBox(minimum=0, maximum=10**6, value=0)
        self.seed_count = QSpinBox(minimum=1, maximum=100, value=1, suffix=" 个")
        self.seed_count.setToolTip("每个种子单独运行一次；只影响随机算法（如随机游走）")
        self.repeats = QSpinBox(minimum=1, maximum=10, value=1, suffix=" 次")
        self.repeats.setToolTip("同一组合重复运行，计算时间取中位数；正式计时建议 3 次")
        self.budget = QSpinBox(minimum=0, maximum=10**6, value=0, singleStep=100)
        self.budget.setSpecialValueText("默认 (20 × 格子数)")
        self.memory = QCheckBox("另外运行一轮测量峰值内存（tracemalloc，较慢）")
        self.output = QLineEdit(placeholderText="留空：results/local/batch-<时间>")
        browse = QPushButton("选择…")
        browse.clicked.connect(self._choose_output)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output, 1)
        out_row.addWidget(browse)
        seed_row = QHBoxLayout()
        seed_row.addWidget(QLabel("起始"))
        seed_row.addWidget(self.seed_first)
        seed_row.addWidget(QLabel("数量"))
        seed_row.addWidget(self.seed_count)
        form.addRow("随机种子", seed_row)
        form.addRow("重复次数", self.repeats)
        form.addRow("移动预算", self.budget)
        form.addRow(self.memory)
        form.addRow("输出目录", out_row)

        # -- 运行 --
        run_box = QGroupBox("运行")
        self.run_button = QPushButton("▶ 运行并导出")
        self.run_button.clicked.connect(self.start)
        self.stop_button = QPushButton("■ 停止")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)
        self.open_button = QPushButton("打开结果文件夹")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self._open_output)
        self.progress = QProgressBar()
        self.status = QLabel("选择地图和算法后点击运行。")
        self.status.setWordWrap(True)
        row = QHBoxLayout()
        for button in (self.run_button, self.stop_button, self.open_button):
            row.addWidget(button)
        run_layout = QVBoxLayout(run_box)
        run_layout.addLayout(row)
        run_layout.addWidget(self.progress)
        run_layout.addWidget(self.status)

        self.table = QTableWidget(0, len(SUMMARY_COLUMNS))
        self.table.setHorizontalHeaderLabels([c[0] for c in SUMMARY_COLUMNS])
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        right = QVBoxLayout()
        right.addWidget(algo_box)
        right.addWidget(settings_box)
        right.addWidget(run_box)
        right.addWidget(QLabel("汇总（全部所选地图）："))
        right.addWidget(self.table, 1)
        layout = QHBoxLayout(self)
        layout.addWidget(map_box, 2)
        layout.addLayout(right, 3)
        self.output_dir: Path | None = None
        self.reload_maps()

    # -- 地图选择 ---------------------------------------------------------
    def reload_maps(self) -> None:
        """从地图库重新读取地图列表，保留已勾选的状态。"""
        checked = set(self.selected_maps())
        self.maps.blockSignals(True)
        self.maps.clear()
        for path in self.library.maps():
            self.maps.addItem(_checkable(path.stem, str(path), checked=str(path) in map(str, checked)))
        self.maps.blockSignals(False)
        self._apply_filter(self.filter.text())
        self._update_count()

    def selected_maps(self) -> list[Path]:
        """被勾选的地图文件。"""
        return [Path(self.maps.item(i).data(Qt.UserRole)) for i in range(self.maps.count())
                if self.maps.item(i).checkState() == Qt.Checked]

    def selected_algorithms(self) -> list[str]:
        """被勾选的算法名。"""
        return [self.algorithms.item(i).data(Qt.UserRole) for i in range(self.algorithms.count())
                if self.algorithms.item(i).checkState() == Qt.Checked]

    def _check(self, rule) -> None:
        """按规则 rule(地图名) 设置每张地图的勾选状态。"""
        self.maps.blockSignals(True)
        for i in range(self.maps.count()):
            item = self.maps.item(i)
            item.setCheckState(Qt.Checked if rule(item.text()) else Qt.Unchecked)
        self.maps.blockSignals(False)
        self._update_count()

    def _check_visible(self, checked: bool) -> None:
        """勾选（或取消）当前筛选后可见的全部地图。"""
        self.maps.blockSignals(True)
        for i in range(self.maps.count()):
            item = self.maps.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.maps.blockSignals(False)
        self._update_count()

    def _apply_filter(self, text: str) -> None:
        """只显示名称包含 text 的地图（不改变勾选状态）。"""
        text = text.strip().lower()
        for i in range(self.maps.count()):
            item = self.maps.item(i)
            item.setHidden(bool(text) and text not in item.text().lower())

    def _update_count(self) -> None:
        """更新“已选 n / 共 N 张”的提示。"""
        self.map_count.setText(f"已选 {len(self.selected_maps())} / 共 {self.maps.count()} 张")

    def _choose_output(self) -> None:
        """选择输出目录。"""
        path = QFileDialog.getExistingDirectory(self, "选择输出目录", str(LOCAL_RESULTS))
        if path:
            self.output.setText(path)

    # -- 运行 -------------------------------------------------------------
    def start(self) -> bool:
        """按当前选择创建实验并开始分批运行；选择不完整时提示并返回 False。"""
        maps, algorithms = self.selected_maps(), self.selected_algorithms()
        if not maps or not algorithms:
            QMessageBox.information(self, "批量实验", "请至少勾选一张地图和一个算法。")
            return False
        first = self.seed_first.value()
        self.run = ExperimentRun(maps, algorithms,
                                 seeds=list(range(first, first + self.seed_count.value())),
                                 repeats=self.repeats.value(), max_steps=self.budget.value() or None,
                                 measure_memory=self.memory.isChecked(), experiment="batch")
        text = self.output.text().strip()
        self.output_dir = Path(text) if text else \
            LOCAL_RESULTS / f"batch-{datetime.now():%Y%m%d-%H%M%S}"
        self.tasks, self.position = self.run.tasks(), 0
        self.progress.setRange(0, len(self.tasks))
        self.progress.setValue(0)
        self._set_running(True)
        self.status.setText(f"运行中：{len(maps)} 张地图 × {len(algorithms)} 个算法 × "
                            f"{self.seed_count.value()} 个种子 = {len(self.tasks)} 次")
        self.timer.start(0)
        return True

    def stop(self) -> None:
        """停止运行；已完成的部分照常导出，并在元数据中注明。"""
        if self.run is not None and self.timer.isActive():
            self.timer.stop()
            self.run.experiment = "batch (stopped)"
            self._finish(stopped=True)

    def run_to_end(self) -> None:
        """不经定时器、直接运行剩余全部组合并导出（供测试与脚本调用）。"""
        while self.position < len(self.tasks):
            self.run.run_task(*self.tasks[self.position])
            self.position += 1
        self.timer.stop()
        self._finish()

    def _tick(self) -> None:
        """定时器回调：在时间片内尽量多运行几个组合，然后更新进度。"""
        deadline = perf_counter() + TIME_SLICE
        while self.position < len(self.tasks) and perf_counter() < deadline:
            self.run.run_task(*self.tasks[self.position])
            self.position += 1
        self.progress.setValue(self.position)
        if self.position >= len(self.tasks):
            self.timer.stop()
            self._finish()

    def _finish(self, stopped: bool = False) -> None:
        """导出结果、显示汇总表并恢复按钮。"""
        self.progress.setValue(self.position)
        self._set_running(False)
        if not self.run.rows:
            self.status.setText("已停止，没有完成的运行。")
            return
        try:
            out = write_outputs(self.run, self.output_dir)
        except OSError as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return
        self._show_summary(out)
        self.open_button.setEnabled(True)
        done = len(self.run.rows)
        self.status.setText(("已停止，" if stopped else "完成，") +
                            f"{done} 次运行的结果已导出到：{out}")

    def _show_summary(self, out: Path) -> None:
        """读取 summary.csv 中“全部地图”一组，显示在表格中。"""
        import csv
        with (out / "summary.csv").open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["map_group"] == "ALL"]
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, (_, key) in enumerate(SUMMARY_COLUMNS):
                self.table.setItem(i, j, QTableWidgetItem(row.get(key, "")))
        self.table.resizeColumnsToContents()

    def _set_running(self, running: bool) -> None:
        """运行中禁用会改变实验设置的控件。"""
        for widget in (self.run_button, self.maps, self.algorithms, self.filter):
            widget.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def _open_output(self) -> None:
        """在系统文件管理器中打开结果目录。"""
        if self.output_dir:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output_dir)))
