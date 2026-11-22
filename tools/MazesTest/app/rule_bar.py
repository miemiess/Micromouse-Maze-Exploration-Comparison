"""规则面板：显示“基础规则 + 叠加层”的当前配置，并在这里增减叠加层、调整参数。

面板横跨主窗口顶部（工具栏下方），始终可见：
    - 第一行“规则栈”：固定的“基础规则”标签，后面依次是叠加的层（每层一个彩色标签），
      右侧是代价公式与“恢复基础规则”按钮；
    - 第二行“叠加层”：每个维度一个下拉框（不叠加 / 某一层），选中的层显示参数输入框。
基础规则时面板为中性灰；叠加了层时整块面板换成该层的颜色（左侧粗色条 + 浅色底），
主窗口的标签页边框、状态栏标签和画布边框也使用同一颜色（见 rule_color / tinted）。

面板只发出 ruleRequested(Ruleset)；是否真的切换（例如有未完成的运行时需要确认）由主窗口决定，
不切换时主窗口调用 set_rule(旧规则) 把面板恢复原样。
"""

from dataclasses import fields

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QPushButton,
                               QStyledItemDelegate, QStyleOptionViewItem, QVBoxLayout, QWidget)

from core.rules import BASIC, BASIC_COLOR, DIMENSIONS, Ruleset, available_layers

BASIC_DESCRIPTION = "每走一格代价 1，转向只计数不计代价；理想观测；到达目标即结束"


def tinted(color: str, alpha: int = 28) -> str:
    """颜色的浅色版本（用于面板底色），返回 CSS rgba 字符串。"""
    c = QColor(color)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha / 255:.3f})"


def chip_style(color: str, *, filled: bool) -> str:
    """规则标签的样式：基础规则为灰色描边，叠加层为实心彩色。"""
    if filled:
        return (f"background:{color}; color:white; border-radius:10px; padding:3px 10px;"
                "font-weight:bold;")
    return (f"background:white; color:{color}; border:2px solid {color}; border-radius:10px;"
            "padding:2px 9px; font-weight:bold;")


class RulePanel(QFrame):
    """规则栈显示 + 叠加层配置。

    Signals:
        ruleRequested(Ruleset): 用户改变了叠加层或参数，请求切换到这套规则。
    """

    ruleRequested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RulePanel")
        self.layer_classes = available_layers()
        self.rule: Ruleset = BASIC

        # 第一行：规则栈
        self.stack_row = QHBoxLayout()
        self.stack_row.setSpacing(6)
        self.heading = QLabel("当前规则")
        self.heading.setStyleSheet("font-weight:bold; font-size:13px;")
        self.base_chip = QLabel("基础规则")
        self.base_chip.setToolTip(BASIC_DESCRIPTION)
        self.layer_chips = QHBoxLayout()
        self.layer_chips.setSpacing(6)
        self.formula = QLabel()
        self.formula.setTextFormat(Qt.RichText)
        self.reset_button = QPushButton("↺ 恢复基础规则")
        self.reset_button.setToolTip("移除全部叠加层，回到基础规则")
        self.reset_button.clicked.connect(lambda: self.ruleRequested.emit(BASIC))
        self.stack_row.addWidget(self.heading)
        self.stack_row.addWidget(self.base_chip)
        self.stack_row.addLayout(self.layer_chips)
        self.stack_row.addSpacing(12)
        self.stack_row.addWidget(self.formula, 1)
        self.stack_row.addWidget(self.reset_button)

        # 第二行：每个维度一个下拉框 + 参数
        self.config_row = QHBoxLayout()
        self.config_row.setSpacing(6)
        self.config_row.addWidget(QLabel("叠加："))
        self.selectors: dict[str, QComboBox] = {}
        self.param_boxes: dict[str, QWidget] = {}
        self.spins: dict[tuple[str, str], QDoubleSpinBox] = {}
        for dimension, dim_title in DIMENSIONS.items():
            classes = [c for c in self.layer_classes.values() if c.dimension == dimension]
            if not classes:
                continue   # 该维度还没有可用的层（如观测模型、比赛流程尚未开发）
            combo = QComboBox()
            combo.addItem("不叠加", None)
            for cls in classes:
                combo.addItem(f"＋ {cls.title}", cls.key)
                combo.setItemData(combo.count() - 1, cls.summary, Qt.ToolTipRole)
            combo.currentIndexChanged.connect(self._emit)
            self.selectors[dimension] = combo
            self.config_row.addWidget(QLabel(f"{dim_title}"))
            self.config_row.addWidget(combo)
            for cls in classes:
                box = QWidget()
                row = QHBoxLayout(box)
                row.setContentsMargins(0, 0, 0, 0)
                for f in fields(cls):
                    name, unit = cls.param_labels.get(f.name, (f.name, ""))
                    spin = QDoubleSpinBox()
                    spin.setDecimals(2)
                    spin.setRange(0.0, 100.0)
                    spin.setSingleStep(0.1 if f.default < 5 else 1.0)
                    spin.setValue(f.default)
                    spin.setSuffix(unit)
                    spin.setKeyboardTracking(False)
                    spin.setToolTip(f"{cls.title}：{name}")
                    spin.valueChanged.connect(self._emit)
                    row.addWidget(QLabel(name))
                    row.addWidget(spin)
                    self.spins[(cls.key, f.name)] = spin
                box.hide()
                self.param_boxes[cls.key] = box
                self.config_row.addWidget(box)
            self.config_row.addSpacing(16)
        self.config_row.addStretch(1)
        if not self.selectors:
            self.config_row.addWidget(QLabel("（src/ext/rules/ 中还没有可叠加的规则层）"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)
        layout.addLayout(self.stack_row)
        layout.addLayout(self.config_row)
        self.set_rule(BASIC)

    # -- 外部接口 ---------------------------------------------------------
    def set_rule(self, rule: Ruleset) -> None:
        """按 rule 同步全部控件与配色（不发出信号）。"""
        self.rule = rule
        blockers = [QSignalBlocker(w) for w in [*self.selectors.values(), *self.spins.values()]]
        for dimension, combo in self.selectors.items():
            layer = rule.layer(dimension)
            combo.setCurrentIndex(max(0, combo.findData(layer.key if layer else None)))
        for key, box in self.param_boxes.items():
            active = next((l for l in rule.layers if l.key == key), None)
            box.setVisible(active is not None)
            if active is not None:
                for f in fields(active):
                    self.spins[(key, f.name)].setValue(getattr(active, f.name))
        del blockers
        self._refresh_stack()

    # -- 内部 -------------------------------------------------------------
    def current_selection(self) -> Ruleset:
        """由下拉框和参数框组成的规则。"""
        layers = []
        for combo in self.selectors.values():
            key = combo.currentData()
            if key is None:
                continue
            cls = self.layer_classes[key]
            layers.append(cls(**{f.name: self.spins[(key, f.name)].value() for f in fields(cls)}))
        return Ruleset(tuple(layers))

    def _emit(self, *_args) -> None:
        """下拉框或参数改变：显示对应的参数框，并请求切换规则。"""
        for key, box in self.param_boxes.items():
            box.setVisible(any(c.currentData() == key for c in self.selectors.values()))
        rule = self.current_selection()
        if rule != self.rule:
            self.ruleRequested.emit(rule)

    def _refresh_stack(self) -> None:
        """重画规则栈标签、公式和整块面板的配色。"""
        while self.layer_chips.count():
            item = self.layer_chips.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        rule = self.rule
        self.base_chip.setStyleSheet(chip_style(BASIC_COLOR, filled=rule.is_basic))
        for layer in rule.layers:
            plus = QLabel("＋")
            plus.setStyleSheet(f"color:{layer.color}; font-weight:bold; font-size:15px;")
            chip = QLabel(layer.label())
            chip.setObjectName(f"chip_{layer.key}")
            chip.setStyleSheet(chip_style(layer.color, filled=True))
            chip.setToolTip(f"{layer.summary}\n参数：{layer.param_text(full=True)}")
            self.layer_chips.addWidget(plus)
            self.layer_chips.addWidget(chip)
        cost = rule.cost_layer
        if rule.is_basic:
            self.formula.setText(f"<span style='color:#495057'>{BASIC_DESCRIPTION}</span>")
        else:
            text = cost.formula if cost else "；".join(l.summary for l in rule.layers)
            self.formula.setText(
                f"<b style='color:{rule.color}'>{text}</b>"
                "<span style='color:#495057'>　·　结果不可与基础规则直接比较</span>")
        self.reset_button.setEnabled(not rule.is_basic)
        color = rule.color
        self.setStyleSheet(
            f"#RulePanel {{ background:{tinted(color, 18 if rule.is_basic else 34)};"
            f" border-left:8px solid {color}; border-bottom:1px solid {tinted(color, 120)}; }}")


class AlgorithmGroupDelegate(QStyledItemDelegate):
    """在每组首项上方绘制标题，使键盘导航只经过算法。"""

    title_role = Qt.UserRole + 1

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        title = index.data(self.title_role)
        if title:
            size.setHeight(size.height() + option.fontMetrics.height() + 8)
            size.setWidth(max(size.width(), option.fontMetrics.horizontalAdvance(title) + 20))
        return size

    def paint(self, painter, option, index):
        title = index.data(self.title_role)
        if title:
            option = QStyleOptionViewItem(option)
            height = option.fontMetrics.height() + 8
            heading = option.rect.adjusted(6, 0, 0, 0)
            heading.setHeight(height)
            painter.save()
            painter.fillRect(option.rect.adjusted(0, 0, 0, height - option.rect.height()),
                             option.palette.window())
            painter.setPen(option.palette.windowText().color())
            font = option.font
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(heading, Qt.AlignLeft | Qt.AlignVCenter, title)
            painter.restore()
            option.rect = option.rect.adjusted(0, height, 0, 0)
        super().paint(painter, option, index)


def populate_algorithm_combo(combo, infos, rule: Ruleset) -> None:
    """按当前规则和算法来源分组；标题不可选，切换规则时保留可用的原选项。"""
    previous = combo.currentData()
    groups = {"为当前规则设计": [], "基础算法": [], "扩展算法": []}
    for info in infos.values():
        if info.designed_for_rule(rule):
            group = "为当前规则设计"
        else:
            group = "扩展算法" if info.layer == "ext" else "基础算法"
        groups[group].append(info)

    with QSignalBlocker(combo):
        if not isinstance(combo.itemDelegate(), AlgorithmGroupDelegate):
            combo.setItemDelegate(AlgorithmGroupDelegate(combo))
        combo.clear()
        first_enabled = -1
        selected = -1
        for title, members in groups.items():
            if not members:
                continue
            for offset, info in enumerate(members):
                combo.addItem(info.name, info.name)
                index = combo.count() - 1
                item = combo.model().item(index)
                if offset == 0:
                    item.setData(title, AlgorithmGroupDelegate.title_role)
                if not rule.supports(info):
                    item.setEnabled(False)
                    item.setToolTip(f"该算法不支持{rule.title}")
                    continue
                if first_enabled == -1:
                    first_enabled = index
                if info.name == previous:
                    selected = index
        combo.setCurrentIndex(selected if selected >= 0 else first_enabled)


def update_algorithms(widget, infos, rule: Ruleset) -> None:
    """更新对比和批量实验的勾选列表，保留选择及勾选状态。"""
    with QSignalBlocker(widget):
        for index in range(widget.count()):
            item = widget.item(index)
            info = infos[item.data(Qt.UserRole) or item.text()]
            enabled = rule.supports(info)
            item.setToolTip(f"该算法不支持{rule.title}" if not enabled
                            else f"为{rule.title}设计" if info.designed_for_rule(rule) else "")
            flags = item.flags()
            item.setFlags(flags | Qt.ItemIsEnabled if enabled else flags & ~Qt.ItemIsEnabled)
