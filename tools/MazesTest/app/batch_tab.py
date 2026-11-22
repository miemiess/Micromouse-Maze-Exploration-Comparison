"""批量实验页：自选实验与正式实验计划共用同一个页面和同一套运行流程。

运行、统计和导出全部调用 src/core/experiments.py（与命令行共用），本页只负责：
    - 选择实验来源：
        · 自选实验：勾选地图与算法，设置种子、重复次数、动作预算、是否测内存；规则跟随顶部规则面板；
        · 正式计划：core.experiments.available_plans() 注册的计划（基础规则 --plan basic、扩展 --plan ext_*）。
          地图、算法、种子与规则全部由计划决定，表单只读显示；与命令行 `--plan <名称>` 完全相同；
    - 按顺序运行一个或多个子实验（计划可含多个子实验），分批推进、界面保持响应，可随时停止；
    - 每个子实验结束即导出 runs.csv / summary.csv / summary.md / metadata.json / figures，并显示汇总表。
停止时：自选实验导出已完成的部分；正式计划**不导出**未完成的子实验，已完成的子实验保留，
从而保证 results/ 下的正式结果总是完整的。
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from simulation import KNOWN_MAP, AlgorithmInfo  # 先导入：把 src/ 加入路径
from maze_document import MapLibrary

from core.experiments import (LOCAL_RESULTS, RESULTS, ExperimentRun, available_plans,  # noqa: E402
                              write_outputs)
from core.rules import BASIC, Ruleset  # noqa: E402
from .rule_bar import chip_style, update_algorithms

CORE_MAPS = ("external_1stworld", "external_japan2017ef", "external_uk2011f")
SUMMARY_COLUMNS = [("算法", "algorithm"), ("成功", "success"), ("运行", "runs"),
                   ("步数/最短路（均值）", "mean_ratio"), ("中位数", "median_ratio"),
                   ("平均转向", "mean_turns"), ("平均重复访问", "mean_repeat_visits"),
                   ("平均动作", "mean_actions"), ("平均碰撞", "mean_collisions"),
                   ("计算 ms（中位数）", "median_compute_ms"), ("扩展节点", "mean_expanded_nodes")]
# 扩展规则（有代价层 / 比赛流程层）时汇总表追加的列。
RULE_SUMMARY_COLUMNS = [("规则代价/最优（均值）", "mean_rule_cost_ratio"),
                        ("中位数", "median_rule_cost_ratio")]
FLOW_SUMMARY_COLUMNS = [("冲刺/最优（均值）", "mean_sprint_ratio"), ("平均成绩", "mean_total_score")]
TIME_SLICE = 0.05  # 每次定时器回调最多运行的秒数，保证界面响应
CUSTOM = "custom"


def _checkable(text: str, data, checked: bool = False) -> QListWidgetItem:
    """创建带复选框的列表项。"""
    item = QListWidgetItem(text)
    item.setData(Qt.UserRole, data)
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    return item


def summary_columns(rule: Ruleset) -> list[tuple[str, str]]:
    """汇总表的列：基础列 + 代价层列 + 比赛流程列。"""
    return SUMMARY_COLUMNS + (RULE_SUMMARY_COLUMNS if rule.cost_layer else []) \
        + (FLOW_SUMMARY_COLUMNS if rule.layer("flow") else [])


def existing_rows(out: Path) -> int | None:
    """结果目录中已完整导出的记录数（metadata 记录的 runs）；没有结果时为 None。"""
    try:
        meta = json.loads((out / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return meta.get("runs") if (out / "runs.csv").is_file() else None


class BatchTab(QWidget):
    """批量实验：自选（多地图 × 多算法）或正式计划，运行并导出结果。"""

    def __init__(self, library: MapLibrary, algorithms: dict[str, AlgorithmInfo], parent=None,
                 results_root: Path = RESULTS):
        """创建实验来源、地图列表、算法列表、设置、进度和汇总表。

        Args:
            library: 地图库（自选实验的地图列表来源）。
            algorithms: 可选算法（探索与已知地图两类都可选）。
            parent: 父控件。
            results_root: 正式计划的结果根目录（默认 results/；测试时指向临时目录）。
        """
        super().__init__(parent)
        self.rule = BASIC
        self.algorithm_infos = algorithms
        self.library = library
        self.results_root = Path(results_root)
        self.plans = available_plans()
        self.queue: list[tuple[ExperimentRun, Path]] = []   # 待运行的（子实验, 输出目录）
        self.queue_index = 0
        self.run: ExperimentRun | None = None               # 正在运行（或最近运行）的子实验
        self.tasks: list = []
        self.position = 0
        self.done_before = 0                                # 本次已完成子实验的组合数（总进度用）
        self.exported: list[Path] = []
        self.plan_runs: list[ExperimentRun] = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # -- 实验来源 --
        source_box = QGroupBox("实验来源")
        self.source = QComboBox()
        self.source.addItem("自选实验：按下方勾选的地图与算法，规则跟随顶部规则面板", CUSTOM)
        for name, (build, folder) in self.plans.items():
            title = (build.__doc__ or name).strip().splitlines()[0]
            self.source.addItem(f"正式计划 --plan {name}：{title}", name)
            self.source.setItemData(self.source.count() - 1, f"结果写入 results/{folder}/", Qt.ToolTipRole)
        self.source.currentIndexChanged.connect(self._on_source_changed)
        self.plan_info = QLabel()
        self.plan_info.setWordWrap(True)
        self.plan_info.setTextFormat(Qt.RichText)
        source_layout = QVBoxLayout(source_box)
        source_layout.addWidget(self.source)
        source_layout.addWidget(self.plan_info)

        # -- 地图 --
        map_box = QGroupBox("地图")
        self.filter = QLineEdit(placeholderText="按名称筛选，例如 wilson、_l30、japan")
        self.filter.textChanged.connect(self._apply_filter)
        self.maps = QListWidget()
        self.maps.setSelectionMode(QAbstractItemView.NoSelection)
        self.maps.itemChanged.connect(lambda _item: self._update_count())
        self.map_count = QLabel()
        buttons = QHBoxLayout()
        self.map_buttons = []
        for text, action in (("全选（可见）", lambda: self._check_visible(True)),
                             ("全不选", lambda: self._check(lambda name: False)),
                             ("外部迷宫库", lambda: self._check(lambda n: n.startswith("external_"))),
                             ("生成迷宫", lambda: self._check(lambda n: n.startswith("gen_"))),
                             ("核心 3 张", lambda: self._check(lambda n: n in CORE_MAPS)),
                             ("刷新", self.reload_maps)):
            button = QPushButton(text)
            button.clicked.connect(action)
            buttons.addWidget(button)
            self.map_buttons.append(button)
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
        update_algorithms(self.algorithms, algorithms, self.rule)
        self.algorithms.setMaximumHeight(200)
        QVBoxLayout(algo_box).addWidget(self.algorithms)

        # -- 设置 --
        self.settings_box = QGroupBox("设置")
        form = QFormLayout(self.settings_box)
        self.seed_first = QSpinBox(minimum=0, maximum=10**6, value=0)
        self.seed_count = QSpinBox(minimum=1, maximum=100, value=1, suffix=" 个")
        self.seed_count.setToolTip("每个种子单独运行一次；只影响随机算法与噪声观测")
        self.repeats = QSpinBox(minimum=1, maximum=10, value=1, suffix=" 次")
        self.repeats.setToolTip("同一组合重复运行，计算时间取中位数；正式计时建议 3 次")
        self.budget = QSpinBox(minimum=0, maximum=10**6, value=0, singleStep=100)
        self.budget.setSpecialValueText("默认 (20 × 格子数)")
        self.memory = QCheckBox("另外运行一轮测量峰值内存（tracemalloc，较慢）")
        self.output = QLineEdit(placeholderText="留空：results/local/batch-<时间>")
        self.browse = QPushButton("选择…")
        self.browse.clicked.connect(self._choose_output)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output, 1)
        out_row.addWidget(self.browse)
        seed_row = QHBoxLayout()
        seed_row.addWidget(QLabel("起始"))
        seed_row.addWidget(self.seed_first)
        seed_row.addWidget(QLabel("数量"))
        seed_row.addWidget(self.seed_count)
        form.addRow("随机种子", seed_row)
        form.addRow("重复次数", self.repeats)
        form.addRow("动作预算", self.budget)
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
        self.progress.setFormat("%v / %m（%p%）")
        self.status = QLabel("选择地图和算法后点击运行。")
        self.status.setWordWrap(True)
        row = QHBoxLayout()
        for button in (self.run_button, self.stop_button, self.open_button):
            row.addWidget(button)
        run_layout = QVBoxLayout(run_box)
        run_layout.addLayout(row)
        run_layout.addWidget(self.progress)
        run_layout.addWidget(self.status)

        self.table_title = QLabel("汇总（全部所选地图）：")
        self.table = QTableWidget(0, len(SUMMARY_COLUMNS))
        self.table.setHorizontalHeaderLabels([c[0] for c in SUMMARY_COLUMNS])
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        # 本页实验使用的规则：自选实验随顶部规则面板切换，正式计划使用计划自带的规则。
        self.rule_label = QLabel()
        self.rule_label.setWordWrap(True)
        right = QVBoxLayout()
        right.addWidget(source_box)
        right.addWidget(self.rule_label)
        right.addWidget(algo_box)
        right.addWidget(self.settings_box)
        right.addWidget(run_box)
        right.addWidget(self.table_title)
        right.addWidget(self.table, 1)
        layout = QHBoxLayout(self)
        layout.addWidget(map_box, 2)
        layout.addLayout(right, 3)
        self.output_dir: Path | None = None
        self.reload_maps()
        self._on_source_changed()

    # -- 来源与规则 ---------------------------------------------------------
    @property
    def plan_name(self) -> str | None:
        """当前选择的正式计划名；自选实验时为 None。"""
        key = self.source.currentData()
        return None if key == CUSTOM else key

    @property
    def follows_rule_panel(self) -> bool:
        """本页实验是否使用顶部规则面板的规则（正式计划使用计划自带的规则）。"""
        return self.plan_name is None

    @property
    def running(self) -> bool:
        return self.timer.isActive()

    def set_rule(self, rule: Ruleset) -> None:
        """顶部规则切换：自选实验清空上一轮结果（已导出的文件保留）、更新可用算法与表格列；正式计划不受影响。"""
        self.rule = rule
        if not self.follows_rule_panel:
            return
        update_algorithms(self.algorithms, self.algorithm_infos, rule)
        self._reset_results()
        self._show_rule()

    def _reset_results(self) -> None:
        self.run = None
        self.queue, self.tasks, self.position = [], [], 0
        self.output_dir = None
        self.exported = []
        if self.follows_rule_panel:
            self.output.clear()
        self.table.setRowCount(0)
        self.progress.setRange(0, 100)
        self.progress.reset()
        self.open_button.setEnabled(False)
        self.status.setText("选择地图和算法后点击运行。" if self.follows_rule_panel else "点击“运行计划”开始。")

    def _show_rule(self) -> None:
        """规则标签与汇总表的列。"""
        if self.follows_rule_panel:
            rule = self.rule
            self.rule_label.setText(f"本页实验规则：{rule.title}"
                                    + ("" if rule.is_basic else "（结果单独保存，不与基础规则混排）"))
            self.rule_label.setStyleSheet(chip_style(rule.color, filled=not rule.is_basic))
            self._set_columns(rule)
        else:
            self.rule_label.setText(f"正式计划 {self.plan_name} 使用计划自带的规则（见上方子实验列表），"
                                    "不随顶部规则面板变化")
            self.rule_label.setStyleSheet(chip_style("#495057", filled=False))

    def _set_columns(self, rule: Ruleset) -> None:
        self.columns = summary_columns(rule)
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([c[0] for c in self.columns])

    def _plan_outputs(self, runs: list[ExperimentRun]) -> list[Path]:
        """正式计划各子实验的输出目录（与命令行 --plan 的默认输出相同）。"""
        base = self.results_root / self.plans[self.plan_name][1]
        return [base / run.experiment if len(runs) > 1 else base for run in runs]

    def _on_source_changed(self, *_args) -> None:
        """切换实验来源：正式计划载入其设置并锁定表单；自选实验恢复可编辑。"""
        if self.running:
            return
        self.plan_runs = []
        if self.plan_name is not None:
            try:
                self.plan_runs = self.plans[self.plan_name][0]()
            except (Exception, SystemExit) as exc:   # 例如计划地图缺失（basic 计划会提示生成命令）
                self.plan_info.setText(f"<b style='color:#c92a2a'>无法载入计划：</b>{exc}")
                self.source.setCurrentIndex(0)
                return
            self._load_plan_into_form(self.plan_runs)
            self.run_button.setText("▶ 运行计划")
        else:
            self.plan_info.setText("")
            self.run_button.setText("▶ 运行并导出")
            update_algorithms(self.algorithms, self.algorithm_infos, self.rule)
        self._set_editable(self.follows_rule_panel)
        self._reset_results()
        self._show_rule()
        if not self.follows_rule_panel:
            self._set_columns(self.plan_runs[0].rule)
            self._refresh_plan_info()

    def _load_plan_into_form(self, runs: list[ExperimentRun]) -> None:
        """把计划的地图、算法、种子等显示在表单上（只读）。"""
        maps = {str(p) for run in runs for p in run.maze_paths}
        algorithms = {a for run in runs for a in run.algorithms}
        self.maps.blockSignals(True)
        for i in range(self.maps.count()):
            item = self.maps.item(i)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in maps else Qt.Unchecked)
        self.maps.blockSignals(False)
        for i in range(self.algorithms.count()):
            item = self.algorithms.item(i)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in algorithms else Qt.Unchecked)
        first = runs[0]
        self.seed_first.setValue(min(first.seeds))
        self.seed_count.setValue(len(first.seeds))
        self.repeats.setValue(first.repeats)
        self.budget.setValue(first.max_steps or 0)
        self.memory.setChecked(first.measure_memory)
        self.output.setText(str(self.results_root / self.plans[self.plan_name][1]))
        self._update_count()

    def _refresh_plan_info(self) -> None:
        """子实验列表：规则、规模与已有结果。"""
        lines = ["<table cellspacing='4'><tr><th align='left'>子实验</th><th align='left'>规则</th>"
                 "<th align='right'>组合数</th><th align='left'>已有结果</th></tr>"]
        for run, out in zip(self.plan_runs, self._plan_outputs(self.plan_runs)):
            rows = existing_rows(out)
            state = "—" if rows is None else (f"✓ {rows} 条" if rows == run.expected_rows else f"⚠ {rows} 条（不完整）")
            lines.append(f"<tr><td>{run.experiment}</td><td style='color:{run.rule.color}'>{run.rule.title}</td>"
                         f"<td align='right'>{run.expected_rows:,}</td><td>{state}</td></tr>")
        total = sum(run.expected_rows * run.repeats for run in self.plan_runs)
        lines.append(f"</table>共 {len(self.plan_runs)} 个子实验，{total:,} 次运行（含计时重复）。"
                     "表单为计划设置（只读）；运行与命令行 <code>--plan</code> 相同。")
        self.plan_info.setText("".join(lines))

    def _set_editable(self, editable: bool) -> None:
        """正式计划时锁定地图、算法与设置（显示计划内容，不可修改）。"""
        for widget in (self.maps, self.algorithms, self.filter, self.settings_box, *self.map_buttons):
            widget.setEnabled(editable)

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
                if self.algorithms.item(i).flags() & Qt.ItemIsEnabled
                and self.algorithms.item(i).checkState() == Qt.Checked]

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
    def start(self, *, confirm: bool = True) -> bool:
        """按当前来源创建实验队列并开始分批运行；无法开始时返回 False。

        正式计划覆盖已有结果前会确认（confirm=False 时不询问，供测试与脚本调用）。
        """
        if self.plan_name is None:
            maps, algorithms = self.selected_maps(), self.selected_algorithms()
            if not maps or not algorithms:
                QMessageBox.information(self, "批量实验", "请至少勾选一张地图和一个算法。")
                return False
            first = self.seed_first.value()
            run = ExperimentRun(maps, algorithms, seeds=list(range(first, first + self.seed_count.value())),
                                repeats=self.repeats.value(), max_steps=self.budget.value() or None,
                                measure_memory=self.memory.isChecked(), experiment="batch", rule=self.rule,
                                include_collision_stats=True)
            text = self.output.text().strip()
            out = Path(text) if text else LOCAL_RESULTS / f"batch-{datetime.now():%Y%m%d-%H%M%S}"
            self.queue = [(run, out)]
        else:
            runs = self.plans[self.plan_name][0]()            # 重新构建：每次运行使用全新的 ExperimentRun
            outputs = self._plan_outputs(runs)
            existing = [o.name for o in outputs if existing_rows(o) is not None]
            if existing and confirm:
                answer = QMessageBox.question(
                    self, "运行正式计划",
                    f"计划 {self.plan_name} 的 {len(existing)} 个子实验已有结果（{', '.join(existing)}），"
                    f"重新运行会在每个子实验完成后覆盖它。\n未完成就停止的子实验不会写入。继续吗？")
                if answer != QMessageBox.Yes:
                    return False
            self.queue = list(zip(runs, outputs))
        self.queue_index, self.done_before, self.exported = 0, 0, []
        total = sum(len(run.tasks()) for run, _ in self.queue)
        self.progress.setRange(0, total)
        self.progress.setValue(0)
        self._set_running(True)
        self._begin(0)
        self.timer.start(0)
        return True

    def _begin(self, index: int) -> None:
        """开始队列中的第 index 个子实验。"""
        self.queue_index = index
        self.run, self.output_dir = self.queue[index]
        self.tasks, self.position = self.run.tasks(), 0
        self._set_columns(self.run.rule)
        self._update_status()

    def _update_status(self) -> None:
        run = self.run
        prefix = f"子实验 {self.queue_index + 1}/{len(self.queue)}「{run.experiment}」· " if len(self.queue) > 1 else ""
        self.status.setText(f"运行中：{prefix}{run.rule.title} · {len(run.maze_paths)} 张地图 × "
                            f"{len(run.algorithms)} 个算法 × {len(run.seeds)} 个种子 · "
                            f"{self.position}/{len(self.tasks)}")

    def stop(self) -> None:
        """停止运行。自选实验导出已完成的部分；正式计划不导出未完成的子实验（已完成的子实验保留）。"""
        if self.run is None or not self.timer.isActive():
            return
        self.timer.stop()
        self._set_running(False)
        self.progress.setValue(self.done_before + self.position)
        if self.plan_name is None:
            self.run.experiment = "batch (stopped)"
            self._export_current(stopped=True)
            return
        kept = "、".join(p.name for p in self.exported) or "无"
        self.status.setText(f"已停止。已完成并导出的子实验：{kept}；未完成的子实验没有写入正式结果目录。")
        self._refresh_plan_info()

    def run_to_end(self) -> None:
        """不经定时器、直接运行剩余全部组合并导出（供测试与脚本调用）。"""
        self.timer.stop()
        while self.run is not None and self._advance(deadline=None):
            pass

    def _tick(self) -> None:
        """定时器回调：在时间片内尽量多运行几个组合，然后更新进度。"""
        if not self._advance(deadline=perf_counter() + TIME_SLICE):
            self.timer.stop()

    def _advance(self, deadline: float | None) -> bool:
        """推进当前子实验；子实验完成时导出并进入下一个。返回是否还有剩余工作。"""
        while self.position < len(self.tasks) and (deadline is None or perf_counter() < deadline):
            self.run.run_task(*self.tasks[self.position])
            self.position += 1
        self.progress.setValue(self.done_before + self.position)
        self._update_status()
        if self.position < len(self.tasks):
            return True
        if not self._export_current():
            self._set_running(False)
            return False
        self.done_before += len(self.tasks)
        if self.queue_index + 1 < len(self.queue):
            self._begin(self.queue_index + 1)
            return True
        self._set_running(False)
        names = "、".join(p.name for p in self.exported)
        where = self.exported[-1] if len(self.exported) == 1 else self.exported[-1].parent
        self.status.setText(f"完成，{self.run.rule.title if len(self.queue) == 1 else names}，"
                            f"{self.done_before} 次运行的结果已导出到：{where}")
        if self.plan_name:
            self._refresh_plan_info()
        return False

    def _export_current(self, stopped: bool = False) -> bool:
        """导出当前子实验并显示其汇总；没有记录或导出失败时返回 False。"""
        if not self.run.rows:
            self.status.setText("已停止，没有完成的运行。")
            return False
        try:
            out = write_outputs(self.run, self.output_dir)
        except OSError as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return False
        self.exported.append(out)
        self._show_summary(out)
        self.open_button.setEnabled(True)
        if stopped:
            self.status.setText(f"已停止，{self.run.rule.title}，{len(self.run.rows)} 次运行的结果已导出到：{out}")
        return True

    def _show_summary(self, out: Path) -> None:
        """读取 summary.csv 中“全部地图”一组，显示在表格中。"""
        with (out / "summary.csv").open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["map_group"] == "ALL"]
        self.table_title.setText(f"汇总（全部地图）：{out.name if len(self.queue) > 1 else '本次实验'}")
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, (_, key) in enumerate(self.columns):
                self.table.setItem(i, j, QTableWidgetItem(row.get(key, "")))
        self.table.resizeColumnsToContents()

    def _set_running(self, running: bool) -> None:
        """运行中禁用会改变实验设置的控件。"""
        self.run_button.setEnabled(not running)
        self.source.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self._set_editable(not running and self.follows_rule_panel)

    def _open_output(self) -> None:
        """在系统文件管理器中打开结果目录（计划为计划目录）。"""
        target = self.exported[-1].parent if self.plan_name and len(self.queue) > 1 and self.exported \
            else self.output_dir
        if target:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))
