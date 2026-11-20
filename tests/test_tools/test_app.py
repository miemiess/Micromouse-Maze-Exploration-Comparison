"""桌面应用的冒烟测试：在无窗口模式下启动，检查三个功能页与底层运行结果一致。

需要 PySide6；未安装时整组测试跳过。
"""

import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HAS_QT = importlib.util.find_spec("PySide6") is not None

if HAS_QT:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(ROOT / "tools" / "MazesTest"))
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from app.export import export_gif, render_image, tile_images
    from app.main_window import MainWindow
    from app.tabs import STATUS_TEXT
    from maze_app import main as app_main
    from simulation import Maze, Runner, discover_algorithms, load_algorithm

MAZE = ROOT / "mazes" / "classic" / "external_uk2011f.json"


@unittest.skipUnless(HAS_QT, "PySide6 not installed")
class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """整组测试共用一个 QApplication。"""
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        """每个测试打开一个新主窗口，地图库使用临时目录。"""
        self.tmp = tempfile.TemporaryDirectory()
        self.map_dir = Path(self.tmp.name) / "mazes"
        self.window = MainWindow(MAZE, map_dir=self.map_dir)
        self.window.show()

    def tearDown(self):
        """关闭窗口（跳过保存确认）并删除临时目录。"""
        self.window.document.dirty = False
        self.window.close()
        self.tmp.cleanup()

    def test_map_library_import_and_save(self):
        """导入的地图进入地图库并出现在下拉框；库外打开的地图修改后保存为库中的副本。"""
        from maze_document import generate
        source = generate(6, 6, seed=4, maze_id="imported").export(Path(self.tmp.name) / "x.json")
        self.assertTrue(self.window.import_path(source))
        self.assertEqual(self.window.document.path, self.map_dir / "imported.json")
        self.assertEqual(self.window.map_combo.currentText(), "imported")

        original = MAZE.read_bytes()
        self.window.open_path(MAZE)  # 测试用的地图库是临时目录，真实 mazes/classic/ 相当于库外文件
        self.assertIn("外部文件", self.window.map_combo.currentText())
        self.window.editor_tab._on_edge_clicked((0, 0), (0, 1))
        self.assertTrue(self.window.save_to_library())
        self.assertEqual(self.window.document.path.parent, self.map_dir)
        self.assertEqual(MAZE.read_bytes(), original)
        labels = [self.window.map_combo.itemText(i) for i in range(self.window.map_combo.count())]
        self.assertEqual(labels, ["imported", "uk2011f_edit"])  # 外部迷宫修改后不会以 external_ 名称另存

    def test_run_tab_matches_core_runner(self):
        """运行页跑完的统计与直接使用 Runner 的结果相同，画布可以正常绘制。"""
        tab = self.window.run_tab
        tab.algorithm.setCurrentText("flood_fill")
        tab.controller.step_once()
        self.assertEqual(tab.stat_labels["steps"].text(), "1")
        tab.controller.run_to_end()
        expected = Runner(Maze.from_json(MAZE), load_algorithm("flood_fill")).run().stats
        self.assertEqual(tab.stat_labels["steps"].text(), str(expected["steps"]))
        self.assertIn("路线重新规划", tab.log.toPlainText())
        tab.display.boxes["fog"].setChecked(True)
        self.assertFalse(tab.view.grab().isNull())

    def test_external_map_saved_as_new_file(self):
        """在上位机里修改外部迷宫后保存：原文件不变，自动另存为新地图并出现在下拉框。"""
        import shutil
        external = Path(shutil.copy(MAZE, self.map_dir / MAZE.name))
        original = external.read_bytes()
        self.window.open_path(external)
        self.assertTrue(self.window.save_to_library())  # 未修改：不写文件
        self.assertEqual(len(self.window.library.maps()), 1)

        self.window.editor_tab._on_edge_clicked((0, 0), (0, 1))
        self.assertTrue(self.window.save_to_library())
        self.assertEqual(self.window.document.path.name, "uk2011f_edit.json")
        self.assertIn("只读", self.window.statusBar().currentMessage())
        self.assertEqual(external.read_bytes(), original)
        self.assertEqual(self.window.map_combo.currentText(), "uk2011f_edit")

    def test_known_map_algorithms_are_separated(self):
        """已知地图算法只出现在"已知地图规划"页；探索页和对比页里没有它们。"""
        def names(combo):
            return {combo.itemText(i) for i in range(combo.count())}
        compare = {self.window.compare_tab.algorithms.item(i).text()
                   for i in range(self.window.compare_tab.algorithms.count())}
        self.assertEqual(names(self.window.known_tab.algorithm), {"astar", "bfs"})
        self.assertFalse({"astar", "bfs"} & (names(self.window.run_tab.algorithm) | compare))
        self.assertIn("wall_follower_left", names(self.window.run_tab.algorithm))

        tab = self.window.known_tab
        tab.controller.run_to_end()
        self.assertEqual(tab.stat_labels["status"].text(), "到达目标")
        self.assertNotEqual(tab.stat_labels["expanded_nodes"].text(), "-")

    def test_compare_tab_runs_all_selected(self):
        """对比页为每个勾选的算法建立画布；跑完后每行都已结束，并与直接运行的结果一致。"""
        tab = self.window.compare_tab
        self.assertEqual(len(tab.views), len(tab.selected()))
        tab.controller.run_to_end()
        statuses = [tab.table.item(row, 1).text() for row in range(tab.table.rowCount())]
        expected = [STATUS_TEXT[Runner(Maze.from_json(MAZE), load_algorithm(n)).run().status]
                    for n in tab.selected()]
        self.assertEqual(statuses, expected)
        self.assertNotIn("运行中", statuses)

    def test_editor_changes_reach_run_tab(self):
        """编辑页修改地图后，切到运行页时运行的是修改后的地图。"""
        editor = self.window.editor_tab
        self.window.tabs.setCurrentWidget(editor)
        editor._on_edge_clicked((0, 0), (0, 1))  # 封住起点唯一的出口
        self.assertTrue(self.window.document.dirty)
        self.window.tabs.setCurrentWidget(self.window.run_tab)
        self.window.run_tab.controller.run_to_end()
        self.assertEqual(self.window.run_tab.runner.snapshot().status, "no_path")

    def test_batch_experiment_tab(self):
        """批量实验页：按类别勾选地图、选择算法、运行并导出结果文件，汇总表显示每个算法一行。"""
        import shutil
        for name in ("external_1stworld.json", "external_uk2011f.json"):
            shutil.copy(ROOT / "mazes" / "classic" / name, self.map_dir / name)
        from maze_document import generate
        self.window.library.save_generated(generate(5, 5, seed=1))
        tab = self.window.batch_tab
        self.window.tabs.setCurrentWidget(tab)  # 切到本页时刷新地图列表
        self.assertEqual(tab.maps.count(), 3)
        tab._check(lambda name: name.startswith("external_"))
        self.assertEqual(len(tab.selected_maps()), 2)
        for i in range(tab.algorithms.count()):
            item = tab.algorithms.item(i)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in ("dfs", "bfs") else Qt.Unchecked)
        tab.output.setText(str(Path(self.tmp.name) / "batch"))
        self.assertTrue(tab.start())
        tab.run_to_end()
        out = Path(self.tmp.name) / "batch"
        self.assertTrue((out / "runs.csv").exists() and (out / "metadata.json").exists())
        self.assertEqual(tab.table.rowCount(), 2)
        self.assertIn("完成", tab.status.text())

    def test_generate_replaces_document(self):
        """随机生成会替换当前地图并出现在地图下拉框中。"""
        editor = self.window.editor_tab
        editor.new_width.setValue(6)
        editor.new_height.setValue(6)
        editor._generate()
        self.assertEqual(self.window.document.width, 6)
        self.assertIn("未保存", self.window.map_combo.currentText())

    def test_batch_generation_with_chosen_algorithm(self):
        """批量生成按所选算法和连续种子写入地图库，并出现在下拉框中；重复生成时跳过。"""
        editor = self.window.editor_tab
        editor.new_width.setValue(5)
        editor.new_height.setValue(5)
        editor.gen_algorithm.setCurrentIndex(editor.gen_algorithm.findData("wilson"))
        editor.gen_seed.setValue(3)
        editor.batch_count.setValue(4)
        editor._generate_batch()
        files = sorted(p.name for p in self.map_dir.glob("gen_*.json"))
        self.assertEqual(files, [f"gen_wilson_5x5_s{s}.json" for s in (3, 4, 5, 6)])
        labels = [self.window.map_combo.itemText(i) for i in range(self.window.map_combo.count())]
        self.assertIn("gen_wilson_5x5_s3", labels)
        editor._generate_batch()
        self.assertIn("跳过 4 张", self.window.statusBar().currentMessage())


@unittest.skipUnless(HAS_QT, "PySide6 not installed")
class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """整组测试共用一个 QApplication。"""
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        """每个测试使用独立的临时文件夹。"""
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        """删除临时文件夹。"""
        self.tmp.cleanup()

    def test_render_and_tile(self):
        """渲染图片宽度符合设置，带标题时更高；拼图尺寸为网格大小。"""
        maze = Maze.from_json(MAZE)
        plain = render_image(maze, size=400)
        titled = render_image(maze, size=400, title="t")
        self.assertEqual(plain.width(), 400)
        self.assertGreater(titled.height(), plain.height())
        sheet = tile_images([plain, plain, plain], 2)
        self.assertEqual((sheet.width(), sheet.height()), (800, plain.height() * 2))

    def test_gif_contains_whole_run(self):
        """GIF 从起点录到结束，帧数受 every 控制。"""
        from PIL import Image
        maze = Maze.from_json(MAZE)
        info = discover_algorithms()[0]["flood_fill"]
        path = export_gif(maze, info.create, self.out / "ff.gif", size=200, every=20)
        decisions = Runner(maze, info.create()).run().decision
        with Image.open(path) as gif:
            self.assertEqual(gif.n_frames, decisions // 20 + 1 + (decisions % 20 != 0))

    def test_command_line_batch_export(self):
        """命令行批量导出：每张地图一张 PNG；指定算法时文件名带算法名。"""
        core = [str(ROOT / "mazes" / "classic" / f"external_{name}.json")
                for name in ("1stworld", "japan2017ef", "uk2011f")]  # 3 张核心迷宫
        with contextlib.redirect_stdout(io.StringIO()):
            app_main(["--export", *core, "-o", str(self.out), "--size", "300"])
            app_main(["--export", str(MAZE), "-o", str(self.out), "--strategy", "dfs"])
        self.assertEqual(len(list(self.out.glob("external_*.png"))), 4)
        self.assertTrue((self.out / "external_uk2011f_dfs.png").exists())


if __name__ == "__main__":
    unittest.main()
