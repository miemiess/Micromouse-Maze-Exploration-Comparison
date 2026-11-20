"""运行核心与地图编辑模型的测试（不需要 matplotlib 或 PySide6）。"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "MazesTest"))
from maze_document import GENERATORS, MapLibrary, MazeDocument, default_goals, generate  # noqa: E402
from simulation import (EXPLORE, KNOWN_MAP, Direction, Maze, Runner,  # noqa: E402
                        discover_algorithms, load_algorithm, maze_walls)

MAZE = ROOT / "mazes" / "classic" / "external_uk2011f.json"


class Scripted:
    """按预设方向序列行动的策略，用于构造特定情况。"""
    name = "scripted"

    def __init__(self, moves=(), error=False):
        """moves: 依次返回的方向；用完后返回 None。error: 为 True 时决策抛出异常。"""
        self.moves, self.error = list(moves), error

    def reset(self, **kwargs):
        """无需初始化。"""

    def choose_direction(self, observation):
        """返回下一个预设方向。"""
        if self.error:
            raise RuntimeError("boom")
        return self.moves.pop(0) if self.moves else None


class RunnerTests(unittest.TestCase):
    def test_discovers_src_algorithms_by_mode(self):
        """自动发现 src/ 中的算法并按类别区分；接口文件和内部基类不会被当成算法。"""
        algorithms, errors = discover_algorithms()
        self.assertEqual(errors, [])
        modes = {name: info.mode for name, info in algorithms.items()}
        for name in ("dfs", "flood_fill", "greedy_dfs", "random_walk", "repeated_astar",
                     "wall_follower_left", "wall_follower_right"):
            self.assertEqual(modes[name], EXPLORE)
        self.assertEqual((modes["bfs"], modes["astar"]), (KNOWN_MAP, KNOWN_MAP))
        self.assertNotIn("", modes)  # 沿墙法的内部基类 _WallFollower
        self.assertEqual(set(discover_algorithms(mode=KNOWN_MAP)[0]), {"astar", "bfs"})
        self.assertEqual(load_algorithm("flood_fill").name, "flood_fill")
        self.assertEqual(load_algorithm("dfs:DfsStrategy").name, "dfs")
        with self.assertRaises(ValueError):
            load_algorithm("no_such_strategy")

    def test_known_map_runner(self):
        """已知地图规划器：开始即知道全部墙，规划耗时计入计算时间，逐格执行与路径一致。"""
        maze = Maze.from_json(MAZE)
        runner = Runner(maze, load_algorithm("bfs"))
        first = runner.snapshot()
        self.assertEqual(runner.mode, KNOWN_MAP)
        self.assertEqual(first.observed_walls, maze_walls(maze))
        self.assertGreater(first.stats["expanded_nodes"], 0)
        planned = [tuple(c) for c in first.debug["plan"]]
        snap = runner.run()
        self.assertEqual(snap.status, "success")
        self.assertEqual(list(snap.path[1:]), planned)
        self.assertFalse(any(runner.step().replanned for _ in range(3)))

    def test_invalid_plan_is_an_error(self):
        """规划器返回不从起点出发或不相邻的路径时，记为 error 而不是悄悄执行。"""
        class BadPlanner:
            name, mode = "bad", KNOWN_MAP

            def plan(self, maze):
                """返回一条跳格的非法路径。"""
                return [maze.start, (5, 5)]
        runner = Runner(Maze.from_json(MAZE), BadPlanner())
        self.assertEqual(runner.snapshot().status, "error")
        self.assertIn("not adjacent", runner.error)

    def test_snapshots_match_environment(self):
        """快照中的路径、统计与环境一致；观测到的墙都是真实存在的墙。"""
        maze = Maze.from_json(MAZE)
        runner = Runner(maze, load_algorithm("flood_fill"))
        seen, replans = set(runner.snapshot().observed_walls), 0
        while not runner.finished:
            snap = runner.step()
            self.assertTrue(snap.new_walls.isdisjoint(seen))
            seen |= snap.new_walls
            replans += snap.replanned
        summary = runner.summary()
        self.assertEqual(snap.status, "success")
        self.assertEqual(list(snap.path), summary["path"])
        self.assertEqual(snap.stats["steps"], summary["steps"])
        self.assertEqual(snap.observed_walls, frozenset(seen))
        self.assertTrue(snap.observed_walls <= maze_walls(maze))
        self.assertGreater(replans, 0, "撞上新墙后 Flood-Fill 应当重新规划")

    def test_reset_restarts_from_start(self):
        """reset 后从起点重新开始，并能得到相同结果。"""
        runner = Runner(Maze.from_json(MAZE), load_algorithm("dfs"))
        first = runner.run().stats
        runner.reset()
        self.assertEqual(runner.snapshot().path, (runner.maze.start,))
        self.assertEqual(runner.run().stats["steps"], first["steps"])

    def test_failure_statuses(self):
        """无路、循环、穿墙和异常分别记为 no_path、loop_detected、invalid_action、error。"""
        maze = Maze.from_json(MAZE)
        self.assertEqual(Runner(maze, Scripted()).run().status, "no_path")
        looping = Scripted()
        looping.loop_detected = True
        self.assertEqual(Runner(maze, looping).run().status, "loop_detected")
        # 起点 (0, 0) 东侧有墙。
        snap = Runner(maze, Scripted([Direction.EAST])).run()
        self.assertEqual((snap.status, snap.blocked), ("invalid_action", ((0, 0), Direction.EAST)))
        runner = Runner(maze, Scripted(error=True))
        self.assertEqual(runner.run().status, "error")
        self.assertIn("boom", runner.error)

    def test_budget_and_timeout(self):
        """移动预算用完记为 budget_exceeded；计算超时记为 timeout。"""
        maze = Maze.from_json(MAZE)
        self.assertEqual(Runner(maze, load_algorithm("dfs"), max_steps=5).run().status,
                         "budget_exceeded")
        self.assertEqual(Runner(maze, load_algorithm("dfs"), time_budget=0).run().status,
                         "timeout")


class DocumentTests(unittest.TestCase):
    def test_round_trip_external_maze(self):
        """读取后保存的文件与原地图内容等价，并能被 Maze 验证。"""
        doc = MazeDocument.load(MAZE)
        with tempfile.TemporaryDirectory() as tmp:
            saved = MazeDocument.load(doc.save(Path(tmp) / "copy.json"))
        self.assertEqual(saved.walls, set(maze_walls(Maze.from_json(MAZE))))
        self.assertEqual((saved.start, saved.goals), (doc.start, doc.goals))
        self.assertFalse(saved.dirty)

    def test_editing(self):
        """加墙、拆墙、设置起点和目标会记录修改；非相邻的墙被拒绝。"""
        doc = MazeDocument("t", 3, 3)
        self.assertEqual(doc.goals, {(1, 1)})
        self.assertTrue(doc.toggle_wall((0, 0), (1, 0)))
        self.assertFalse(doc.toggle_wall((1, 0), (0, 0)))
        doc.set_start((2, 2), Direction.SOUTH)
        self.assertFalse(doc.toggle_goal((1, 1)))
        self.assertTrue(doc.dirty)
        self.assertEqual(doc.revision, 4)
        errors, _ = doc.check()
        self.assertTrue(errors, "没有目标的地图应当报错")
        with self.assertRaises(ValueError):
            doc.set_wall((0, 0), (2, 0), True)

    def test_unreachable_goal_is_a_warning(self):
        """目标不可达只是提醒，地图仍可保存，用于无路测试。"""
        doc = MazeDocument("t", 3, 3)
        doc.goals = {(2, 2)}
        doc.set_wall((1, 2), (2, 2), True)
        doc.set_wall((2, 1), (2, 2), True)
        errors, warnings = doc.check()
        self.assertEqual(errors, [])
        self.assertTrue(any("no goal" in w for w in warnings))

    def test_generate_is_reproducible_and_connected(self):
        """同一种子生成同一张图；所有格子连通；环路比例越大墙越少。"""
        a, b = generate(10, 8, seed=3), generate(10, 8, seed=3)
        self.assertEqual(a.walls, b.walls)
        self.assertEqual(len(a.reachable_from_start()), 80)
        self.assertEqual(a.check(), ([], []))
        self.assertLess(len(generate(10, 8, seed=3, loop_fraction=0.3).walls), len(a.walls))
        self.assertEqual(a.metadata["seed"], 3)
        self.assertEqual(default_goals(16, 16), {(7, 7), (7, 8), (8, 7), (8, 8)})
        self.assertEqual(default_goals(5, 5), {(2, 2)})

    def test_all_generators_make_perfect_mazes(self):
        """每种生成算法都生成完美迷宫：全部连通、无环（开放边数 = 格子数 − 1），且可复现。"""
        width, height = 9, 7  # 奇数尺寸时目标只有一格，不会额外拆掉目标区内部的墙
        total_edges = (width - 1) * height + width * (height - 1)
        for algorithm in GENERATORS:
            with self.subTest(algorithm=algorithm):
                doc = generate(width, height, seed=5, algorithm=algorithm)
                self.assertEqual(len(doc.reachable_from_start()), width * height)
                self.assertEqual(total_edges - len(doc.walls), width * height - 1)
                self.assertEqual(doc.walls, generate(width, height, seed=5, algorithm=algorithm).walls)
                self.assertEqual(doc.check(), ([], []))
        # 统一命名：gen_<生成算法>_<宽>x<高>_s<种子>[_l<环路百分比>]
        self.assertEqual(generate(4, 4, seed=1).maze_id, "gen_backtracker_4x4_s1")
        self.assertEqual(generate(4, 4, seed=1, loop_fraction=0.1).maze_id,
                         "gen_backtracker_4x4_s1_l10")
        self.assertEqual(generate(4, 4, seed=1, algorithm="wilson").maze_id, "gen_wilson_4x4_s1")
        with self.assertRaises(ValueError):
            generate(4, 4, seed=1, algorithm="no_such_generator")


class MapLibraryTests(unittest.TestCase):
    def setUp(self):
        """每个测试使用独立的临时地图库。"""
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.library = MapLibrary(self.dir / "mazes")

    def tearDown(self):
        """删除临时文件夹。"""
        self.tmp.cleanup()

    def write(self, name: str, text: str) -> Path:
        """在库外写一个待导入的文件。"""
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_import_rejects_invalid_files(self):
        """非 JSON、字段缺失、墙不相邻、坐标越界的文件都被拒绝，且不写入库中。"""
        good = generate(4, 4, seed=1).to_dict()
        bad_cases = {
            "not_json.json": "{ broken",
            "missing.json": '{"maze_id": "x"}',
            "far_wall.json": str({**good, "blocked_edges": [[[0, 0], [2, 0]]]}).replace("'", '"'),
            "outside.json": str({**good, "start": [9, 9]}).replace("'", '"'),
        }
        for name, text in bad_cases.items():
            with self.subTest(file=name), self.assertRaises(ValueError):
                self.library.import_file(self.write(name, text))
        self.assertEqual(self.library.maps(), [])

    def test_import_copies_into_library(self):
        """合法文件以 <maze_id>.json 存入库中；重名时需要明确覆盖。"""
        source = generate(5, 5, seed=2, maze_id="my maze?").export(self.dir / "src.json")
        doc, warnings = self.library.import_file(source)
        self.assertEqual(warnings, [])
        self.assertEqual(doc.path, self.library.folder / "my maze_.json")
        self.assertEqual(self.library.maps(), [doc.path])
        with self.assertRaises(FileExistsError):
            self.library.import_file(source)
        self.library.import_file(source, overwrite=True)

    def test_import_reports_warnings(self):
        """目标不可达的地图可以导入，但会返回提醒。"""
        doc = MazeDocument("closed", 3, 3)
        doc.goals = {(2, 2)}
        doc.set_wall((1, 2), (2, 2), True)
        doc.set_wall((2, 1), (2, 2), True)
        _, warnings = self.library.import_file(doc.export(self.dir / "closed.json"))
        self.assertTrue(warnings)

    def test_save_never_modifies_outside_files(self):
        """编辑库外打开的外部迷宫后保存：在库中另存为改名后的新地图，原文件不变；之后原地保存。"""
        original = MAZE.read_bytes()
        doc = MazeDocument.load(MAZE)
        doc.toggle_wall((0, 0), (0, 1))
        path = self.library.save(doc)
        self.assertEqual((path.parent, path.name), (self.library.folder, "uk2011f_edit.json"))
        self.assertEqual(MAZE.read_bytes(), original)
        doc.toggle_wall((0, 0), (0, 1))
        self.assertEqual(self.library.save(doc), path)  # 新地图不再只读，原地保存

    def test_external_maps_are_read_only(self):
        """外部迷宫修改后保存会另存为新地图并记录来源；原文件不变；重复另存时编号递增。"""
        import shutil
        external = Path(shutil.copy(MAZE, self.library.folder / MAZE.name))
        original = external.read_bytes()

        doc = MazeDocument.load(external)
        self.assertTrue(doc.read_only)
        doc.toggle_wall((0, 0), (0, 1))
        path = self.library.save(doc)
        self.assertEqual(path.name, "uk2011f_edit.json")
        self.assertEqual(doc.metadata["derived_from"], "external_uk2011f")
        self.assertFalse(doc.read_only)
        self.assertEqual(external.read_bytes(), original)

        doc.toggle_wall((0, 0), (0, 1))
        self.assertEqual(self.library.save(doc), path)  # 新地图不再只读，原地保存

        again = MazeDocument.load(external)
        again.toggle_wall((1, 1), (1, 2))
        self.assertEqual(self.library.save(again).name, "uk2011f_edit2.json")
        with self.assertRaises(FileExistsError):  # 新地图之间重名仍需确认
            renamed = MazeDocument.load(path)
            renamed.maze_id = "uk2011f_edit2"
            self.library.save(renamed)
        self.library.save(MazeDocument.load(external), overwrite=True)  # 即使要求覆盖也不改原文件
        self.assertEqual(external.read_bytes(), original)

    def test_save_generated_skips_existing(self):
        """批量生成的地图存入地图库；同名文件已存在时跳过，不覆盖。"""
        first = self.library.save_generated(generate(5, 5, seed=1))
        self.assertEqual(first.parent, self.library.folder)
        self.assertIsNone(self.library.save_generated(generate(5, 5, seed=1)))

    def test_renaming_saves_as_new_file(self):
        """修改地图 ID 后保存会写入新文件，原文件保留。"""
        doc = generate(4, 4, seed=5, maze_id="first")
        first = self.library.save(doc)
        doc.maze_id = "second"
        self.assertEqual(self.library.save(doc).name, "second.json")
        self.assertTrue(first.exists())

    def test_export_keeps_document_path(self):
        """导出只写副本，不改变当前地图对应的文件和未保存状态。"""
        doc = generate(4, 4, seed=3)
        self.library.save(doc)
        doc.toggle_wall((0, 0), (1, 0))
        doc.export(self.dir / "copy.json")
        self.assertEqual(doc.path.parent, self.library.folder)
        self.assertTrue(doc.dirty)


if __name__ == "__main__":
    unittest.main()
