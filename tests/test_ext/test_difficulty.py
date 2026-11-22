"""D4 迷宫难度刻画与对抗式生成（src/ext/difficulty.py）。"""

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Maze  # noqa: E402
from ext.difficulty import adversarial, correlate, features, spearman  # noqa: E402


def maze(width, height, walls, goals=((2, 2),), start=(0, 0)) -> Maze:
    return Maze({"maze_id": "t", "width": width, "height": height, "start": list(start), "start_heading": "N",
                 "goals": [list(g) for g in goals], "blocked_edges": [[list(a), list(b)] for a, b in walls]})


class FeatureTests(unittest.TestCase):
    def test_open_room_has_loops_and_no_dead_ends(self):
        f = features(maze(3, 3, []))
        self.assertAlmostEqual(f["loop_ratio"], round((12 - 8) / 9, 4))     # 12 条边，生成树 8 条
        self.assertEqual((f["dead_end_ratio"], f["shortest"], f["detour"]), (0, 4, 1.0))
        self.assertEqual(f["shortest_turns"], 1)                             # 先北后东，只转一次

    def test_corridor_is_a_perfect_maze(self):
        # 3×1 走廊加一个死胡同的 1×3：起点 (0,0)，目标 (0,2)，只有一条路
        f = features(maze(2, 3, [((0, 0), (1, 0)), ((0, 1), (1, 1)), ((0, 2), (1, 2)), ((1, 0), (1, 1))],
                          goals=((0, 2),)))
        self.assertEqual(f["loop_ratio"], 0)
        self.assertGreater(f["dead_end_ratio"], 0)
        self.assertEqual((f["shortest"], f["shortest_turns"]), (2, 0))

    def test_spearman(self):
        self.assertEqual(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertEqual(spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertIsNone(spearman([1, 1, 1], [1, 2, 3]))
        self.assertIsNone(spearman([1, 2], [1, 2]))
        self.assertEqual(spearman([1, 2, 2, 3], [1, 2, 2, 3]), 1.0)            # 并列取平均秩

    def test_correlate_writes_outputs(self):
        ids = ["external_1stworld", "external_uk2011f", "external_japan2017ef", "gen_wilson_16x16_s103"]
        with TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs.csv"
            with runs.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["maze_id", "algorithm", "experiment_mode", "status", "ratio"])
                writer.writeheader()
                for i, m in enumerate(ids):
                    writer.writerow({"maze_id": m, "algorithm": "a", "experiment_mode": "unknown_exploration",
                                     "status": "success", "ratio": 1 + i})
            out = Path(tmp) / "out"
            path = correlate(runs, out)
            self.assertIn("| a | 4 |", path.read_text(encoding="utf-8"))
            with (out / "features.csv").open(encoding="utf-8") as f:
                self.assertEqual([r["maze_id"] for r in csv.DictReader(f)], sorted(ids))


class AdversarialTests(unittest.TestCase):
    def test_annealing_is_reproducible_and_keeps_maze_valid(self):
        first = adversarial("repeated_astar", iterations=25, seed=3, out_dir=None)
        second = adversarial("repeated_astar", iterations=25, seed=3, out_dir=None)
        self.assertEqual(first["maze"], second["maze"])
        self.assertGreaterEqual(first["best_score"], first["start_score"])
        result = Maze(first["maze"])
        f = features(result)
        self.assertIsNotNone(f["shortest"])                                  # 目标仍可达
        from ext.difficulty import _connected
        self.assertTrue(_connected(result))                                  # 所有格子可达
        self.assertFalse(any(edge <= result.goals for edge in result.walls))  # 目标区内部没有墙
        self.assertEqual(first["maze"]["metadata"]["target_algorithm"], "repeated_astar")
        self.assertIn("flood_fill", first["comparison"])


if __name__ == "__main__":
    unittest.main()
