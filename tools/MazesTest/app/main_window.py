"""主窗口：地图库（项目的 mazes/classic/ 目录）的选择、导入、导出与保存，三个功能页，菜单与"未保存修改"处理。

主窗口持有唯一的当前地图（MazeDocument）。编辑页直接修改它；切换到运行页或对比页时，
若地图有改动，就验证后转换为 Maze 交给这两页重新开始，保证运行的总是最新地图。

地图下拉框列出地图库 mazes/classic/ 中的全部地图（上位机与实验共用）。
"""

from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QComboBox, QFileDialog, QLabel, QMainWindow, QMessageBox,
                               QTabWidget, QToolBar)

from maze_document import MapLibrary, MazeDocument, generate
from simulation import EXPLORE, KNOWN_MAP, ROOT, discover_algorithms

from .batch_tab import BatchTab
from .tabs import CompareTab, EditorTab, RunTab

MAZE_DIR = ROOT / "mazes" / "classic"  # 项目的地图目录：全部地图统一放在这里

HELP_TEXT = """<h3>电脑鼠迷宫探索</h3>
<p><b>地图</b>：下拉框中列出地图库 mazes/classic/ 中的全部地图。
"导入"会先验证文件是否为合法迷宫，再复制进地图库；"导出"把当前地图另存到任意位置；
"保存到地图库"把编辑结果写回地图库。</p>
<p><b>外部迷宫只读</b>：external_*.json 是整理好的外部迷宫库地图，不会被覆盖。修改后保存时自动另存为
新地图（例如 external_uk2011f → uk2011f_edit），metadata 中记录 derived_from。</p>
<p><b>实时运行</b>：选择算法后点"运行"或"单步"。算法与实验使用同一个环境（src/environment.py），
统计数字就是环境真实记录的结果。</p>
<ul>
<li>黑色墙：电脑鼠已观测到的墙；灰色墙：还没观测到的墙（迷雾模式下隐藏）；</li>
<li>红色粗线：这一步刚发现的墙；紫色虚线：策略当前打算走的路线；</li>
<li>Flood-Fill 撞上新墙时路线会改变，事件日志中记录为"路线重新规划"。</li>
</ul>
<p><b>同屏对比</b>：勾选 2~4 个探索算法，在同一张地图上同步推进，表格中成功且步数最少的一行标绿。</p>
<p><b>已知地图规划</b>：BFS 等一开始就拿到完整地图的算法单独成页，作为参照，
不与探索算法放在同一个对比里（README 规定两类分开比较）。</p>
<p><b>批量实验</b>：勾选多张地图和多个算法，批量运行（不显示动画），自动导出 runs.csv、summary.csv、metadata.json 和图表到 results/；规则见 Docs/experiment-plan.md。</p>
<p><b>地图编辑</b>：点击格子边缘加墙/拆墙，切换工具设置起点和目标；可新建、随机生成（记录种子）。</p>
<p>新算法：在 src/ 中新建文件，按 src/algorithm_api.py 的接口写一个类，重启应用后自动出现在对应页面；
实现可选的 debug_view() 即可显示距离、路线等内部状态（格式见 tools/MazesTest/README.md）。</p>"""


class MainWindow(QMainWindow):
    """应用主窗口。"""

    def __init__(self, initial: Path | None = None, *, map_dir: Path = MAZE_DIR):
        """发现算法、创建四个功能页，并打开初始地图。

        Args:
            initial: 启动时打开的迷宫文件；None 时打开 地图库中的第一张，没有则随机生成一张。
            map_dir: 地图库文件夹，默认项目的 mazes/classic/（测试时可换成临时目录）。
        """
        super().__init__()
        self.library = MapLibrary(map_dir)
        self.algorithms, errors = discover_algorithms()
        explorers = {n: i for n, i in self.algorithms.items() if i.mode == EXPLORE}
        planners = {n: i for n, i in self.algorithms.items() if i.mode == KNOWN_MAP}
        self.document: MazeDocument | None = None
        self._synced = None  # 上次交给运行页的 (文档 id, 修改版本)

        self.run_tab = RunTab(explorers)
        self.compare_tab = CompareTab(explorers)
        self.known_tab = RunTab(planners, known_map=True)
        self.batch_tab = BatchTab(self.library, self.algorithms)
        self.editor_tab = EditorTab()
        self.editor_tab.confirm_discard = self.confirm_discard
        self.editor_tab.documentEdited.connect(self._update_title)
        self.editor_tab.documentReplaced.connect(self.set_document)
        self.editor_tab.saveRequested.connect(self.save_to_library)
        self.editor_tab.exportRequested.connect(self.export_dialog)
        self.editor_tab.batchGenerated.connect(self.save_generated_batch)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.run_tab, "▶ 实时运行")
        self.tabs.addTab(self.compare_tab, "⚖ 同屏对比")
        self.tabs.addTab(self.known_tab, "◎ 已知地图规划")
        self.tabs.addTab(self.batch_tab, "▦ 批量实验")
        self.tabs.addTab(self.editor_tab, "✎ 地图编辑")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        self._build_toolbar_and_menu()
        if errors:
            self.statusBar().showMessage("以下算法文件导入失败：" + "；".join(errors))
        elif not self.algorithms:
            self.statusBar().showMessage("src/ 中没有找到符合 algorithm_api 接口的算法")
        else:
            self.statusBar().showMessage(
                f"探索算法：{', '.join(explorers) or '无'}；已知地图算法：{', '.join(planners) or '无'}")

        candidates = self.library.maps()
        if initial is not None:
            self.open_path(Path(initial))
        elif candidates:
            self.open_path(candidates[0])
        else:
            self.set_document(generate(16, 16, seed=1))

    # -- 界面 -------------------------------------------------------------
    def _build_toolbar_and_menu(self) -> None:
        """创建地图工具栏（下拉框、导入、导出、保存）和菜单。"""
        toolbar = QToolBar("地图")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addWidget(QLabel(" 地图： "))
        self.map_combo = QComboBox()
        self.map_combo.setMinimumWidth(300)
        self.map_combo.activated.connect(self._on_map_chosen)
        toolbar.addWidget(self.map_combo)

        import_action = QAction("导入地图…", self, shortcut=QKeySequence.Open)
        import_action.setToolTip("验证外部迷宫文件，合法后复制进地图库 mazes/classic/")
        import_action.triggered.connect(self.import_dialog)
        export_action = QAction("导出地图…", self, shortcut=QKeySequence.SaveAs)
        export_action.setToolTip("把当前地图另存到任意位置")
        export_action.triggered.connect(self.export_dialog)
        save_action = QAction("保存到地图库", self, shortcut=QKeySequence.Save)
        save_action.triggered.connect(self.save_to_library)
        quit_action = QAction("退出", self, shortcut=QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        help_action = QAction("使用说明", self, shortcut=QKeySequence.HelpContents)
        help_action.triggered.connect(lambda: QMessageBox.information(self, "使用说明", HELP_TEXT))

        toolbar.addActions([import_action, export_action, save_action])
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addActions([import_action, export_action, save_action])
        file_menu.addSeparator()
        file_menu.addAction(quit_action)
        self.menuBar().addMenu("帮助").addAction(help_action)

    def _populate_maps(self) -> None:
        """刷新地图下拉框：地图库中的地图，以及不在 地图库中的当前地图（外部文件或未保存）。"""
        self.map_combo.blockSignals(True)
        self.map_combo.clear()
        for path in self.library.maps():
            self.map_combo.addItem(path.stem, str(path.resolve()))

        doc = self.document
        current = doc.path.resolve() if doc and doc.path else None
        index = self.map_combo.findData(str(current)) if current else -1
        if index < 0 and doc:
            label = f"{current.name}（外部文件）" if current else f"{doc.maze_id}（未保存）"
            if self.map_combo.count():
                self.map_combo.insertSeparator(self.map_combo.count())
            self.map_combo.addItem(label, str(current) if current else None)
            index = self.map_combo.count() - 1
        self.map_combo.setCurrentIndex(index)
        self.map_combo.blockSignals(False)

    def _on_tab_changed(self, _index: int) -> None:
        """切换页面：运行类页面同步当前地图；进入批量实验页时刷新地图列表（地图库可能已变化）。"""
        if self.tabs.currentWidget() is self.batch_tab:
            if not self.batch_tab.timer.isActive():
                self.batch_tab.reload_maps()
        else:
            self._sync_maze()

    def _update_title(self) -> None:
        """窗口标题显示地图 ID，有未保存修改时加 *。"""
        doc = self.document
        mark = " *" if doc and doc.dirty else ""
        self.setWindowTitle(f"电脑鼠迷宫探索 — {doc.maze_id if doc else ''}{mark}")

    # -- 当前地图 ---------------------------------------------------------
    def set_document(self, doc: MazeDocument) -> None:
        """把 doc 设为当前地图，刷新所有页面。"""
        self.document = doc
        self.editor_tab.set_document(doc)
        self._populate_maps()
        self._update_title()
        self._sync_maze(force=True)

    def open_path(self, path: Path) -> bool:
        """打开已存在的地图文件（下拉框中的地图）；失败时提示并返回 False。"""
        try:
            doc, _ = self.library.validate_file(path)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法打开地图", f"{path}\n{exc}")
            return False
        self.set_document(doc)
        return True

    def _on_map_chosen(self, index: int) -> None:
        """在下拉框中选择了另一张地图。"""
        data = self.map_combo.itemData(index)
        current = self.document.path.resolve() if self.document and self.document.path else None
        if data is None or (current and Path(data) == current):
            return
        if not self.confirm_discard() or not self.open_path(Path(data)):
            self._populate_maps()  # 取消或失败：恢复原来的选择

    def _sync_maze(self, force: bool = False) -> None:
        """地图有改动时，验证并交给运行页和对比页（它们会从头开始）。"""
        doc = self.document
        if doc is None:
            return
        key = (id(doc), doc.revision)
        if key == self._synced and not force:
            return
        self._synced = key
        errors, warnings = doc.check()
        if errors:
            maze, message = None, "当前地图无效，请在“地图编辑”中修正：" + "；".join(errors)
        else:
            maze, message = doc.to_maze(), ""
        for tab in (self.run_tab, self.compare_tab, self.known_tab):
            tab.set_maze(maze, message)
        if warnings:
            self.statusBar().showMessage("地图提醒：" + "；".join(warnings))

    # -- 地图库：导入、导出、保存 -----------------------------------------
    def import_path(self, path: Path) -> bool:
        """验证外部地图文件，合法后复制进地图库 并打开。

        不合法时说明原因并拒绝导入；有提醒（如目标不可达）时询问是否继续；
        地图库中已有同名地图时询问是否覆盖。返回是否导入成功。
        """
        try:
            doc, warnings = self.library.validate_file(path)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "导入失败", f"{Path(path).name} 不是合法的迷宫文件。\n\n{exc}")
            return False
        if warnings and QMessageBox.question(
                self, "导入提醒", "地图合法，但有以下提醒：\n" + "\n".join(warnings)
                + "\n\n仍然导入吗？") != QMessageBox.Yes:
            return False
        doc.path = None  # 作为新地图存入库中
        if not self._save_into_library(doc):
            return False
        self.set_document(doc)
        self.statusBar().showMessage(f"已导入：{doc.path}", 8000)
        return True

    def import_dialog(self) -> None:
        """选择外部文件并导入。"""
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "导入地图", str(Path.home()),
                                              "迷宫 JSON (*.json)")
        if path:
            self.import_path(Path(path))

    def export_dialog(self) -> None:
        """把当前地图另存一份到任意位置（不改变当前地图对应的文件）。"""
        doc = self.document
        if doc is None or not self._check_savable(doc):
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出地图",
                                              str(Path.home() / f"{doc.maze_id}.json"),
                                              "迷宫 JSON (*.json)")
        if not path:
            return
        try:
            self.statusBar().showMessage(f"已导出：{doc.export(Path(path))}", 8000)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "导出失败", str(exc))

    def save_to_library(self) -> bool:
        """把当前地图保存到地图库；返回是否保存成功。

        外部迷宫（只读）修改后会另存为新地图，状态栏说明新文件名；未修改时不写文件。
        """
        doc = self.document
        if doc is None or not self._check_savable(doc):
            return False
        if not doc.dirty and self.library.contains(doc.path):
            self.statusBar().showMessage("地图没有修改，无需保存", 5000)
            return True
        original_id = doc.maze_id
        if not self._save_into_library(doc):
            return False
        self.editor_tab.refresh()
        self._populate_maps()
        self._update_title()
        if doc.maze_id != original_id and doc.metadata.get("derived_from") == original_id:
            message = f"{original_id} 是只读的外部迷宫，修改已另存为新地图：{doc.path.name}"
        else:
            message = f"已保存：{doc.path}"
        self.statusBar().showMessage(message, 10000)
        return True

    def save_generated_batch(self, docs: list[MazeDocument]) -> list:
        """把批量生成的地图存入地图库，返回实际写入的文件。

        同名文件已存在时跳过，不覆盖；完成后刷新下拉框，并在状态栏报告数量。
        """
        written = []
        for doc in docs:
            try:
                path = self.library.save_generated(doc)
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "批量生成失败", f"{doc.maze_id}：{exc}")
                break
            if path is not None:
                written.append(path)
        self._populate_maps()
        skipped = len(docs) - len(written)
        message = f"已生成 {len(written)} 张地图到地图库"
        self.statusBar().showMessage(message + (f"，跳过 {skipped} 张已存在的" if skipped else ""), 10000)
        return written

    def _check_savable(self, doc: MazeDocument) -> bool:
        """地图有错误时提示并返回 False。"""
        errors, _ = doc.check()
        if errors:
            QMessageBox.warning(self, "地图无效", "请先修正以下错误：\n" + "\n".join(errors))
        return not errors

    def _save_into_library(self, doc: MazeDocument) -> bool:
        """写入地图库；同名文件已存在时询问是否覆盖。"""
        try:
            self.library.save(doc)
            return True
        except FileExistsError:
            target = self.library.path_for(doc.maze_id)
            if QMessageBox.question(self, "地图已存在",
                                    f"地图库中已有 {target.name}，是否覆盖？") != QMessageBox.Yes:
                return False
            self.library.save(doc, overwrite=True)
            return True
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False

    def confirm_discard(self) -> bool:
        """当前地图有未保存修改时询问：保存到地图库 / 放弃 / 取消。返回是否可以继续。"""
        if not (self.document and self.document.dirty):
            return True
        answer = QMessageBox.question(
            self, "未保存的修改", f"地图 {self.document.maze_id} 有未保存的修改，是否保存到地图库？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if answer == QMessageBox.Save:
            return self.save_to_library()
        return answer == QMessageBox.Discard

    def closeEvent(self, event) -> None:
        """关闭窗口前处理未保存的修改。"""
        if self.confirm_discard():
            event.accept()
        else:
            event.ignore()
