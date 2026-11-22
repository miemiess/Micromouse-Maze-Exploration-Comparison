"""E1 运动时间模型：梯形 / 三角形速度曲线、转向耗时、与转弯代价的换算、最优用时。"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Direction, Maze, load_algorithm, run_episode  # noqa: E402
from core.rules import Ruleset, parse_rule  # noqa: E402
from ext.rules.motion_time import MotionTimeLayer  # noqa: E402

MAP = ROOT / "mazes" / "classic" / "external_uk2011f.json"


class MotionModelTests(unittest.TestCase):
    def setUp(self):
        self.layer = MotionTimeLayer()   # 0.18 m 格，0.5 m/s，2 m/s²，转 90° 0.3 s，掉头 0.5 s

    def test_trapezoid_and_triangle_profiles(self):
        """长直道：t = d / v + v / a；短直道（到不了最高速）：t = 2 √(d / a)；两者在 d* = v² / a 处连续。"""
        layer = self.layer
        self.assertAlmostEqual(layer.run_cost(4), 0.72 / 0.5 + 0.5 / 2.0)
        short = MotionTimeLayer(v_max=1.0)          # d* = 0.5 m，单格 0.18 m 到不了最高速
        self.assertAlmostEqual(short.run_cost(1), 2 * math.sqrt(0.18 / 2.0))
        boundary = MotionTimeLayer(cell=0.125)      # 单格恰好等于 d* = 0.125 m
        self.assertAlmostEqual(boundary.run_cost(1), 2 * math.sqrt(0.125 / 2.0))

    def test_long_runs_are_cheaper_than_split_runs(self):
        """连续直行比中途停车再走更快（次可加性），因此最优路线偏好长直道。"""
        for k1 in range(1, 6):
            for k2 in range(1, 6):
                self.assertLess(self.layer.run_cost(k1 + k2),
                                self.layer.run_cost(k1) + self.layer.run_cost(k2))

    def test_turn_times_and_equivalent_weight(self):
        self.assertEqual((self.layer.turn_cost(1), self.layer.turn_cost(2)), (0.3, 0.5))
        self.assertAlmostEqual(self.layer.equivalent_weight(), 0.3 / self.layer.run_cost(1))

    def test_path_time(self):
        """朝北出发：北 2 格、右转、东 1 格、掉头、西 1 格。"""
        rule = Ruleset((self.layer,))
        path = [(0, 0), (0, 1), (0, 2), (1, 2), (0, 2)]
        expected = self.layer.run_cost(2) + 0.3 + self.layer.run_cost(1) + 0.5 + self.layer.run_cost(1)
        self.assertAlmostEqual(rule.cost(path, Direction.NORTH), expected)

    def test_run_and_optimum(self):
        """运行中的规则代价为预计用时；规则最优用时不高于任何探索算法，也不高于 BFS 最短路的用时。"""
        rule = parse_rule("motion_time")
        maze = Maze.from_json(MAP)
        optimal = rule.optimal_cost(maze)
        shortest = run_episode(maze, load_algorithm("bfs"), rule=rule)
        self.assertLessEqual(optimal, shortest["rule_cost"] + 1e-9)
        for name in ("dfs", "flood_fill", "repeated_astar"):
            result = run_episode(maze, load_algorithm(name), rule=rule)
            self.assertAlmostEqual(result["rule_cost"], rule.cost(result["path"], maze.start_heading))
            self.assertGreaterEqual(result["rule_cost"] + 1e-9, optimal)

    def test_parameters_from_spec(self):
        rule = parse_rule("motion_time:v_max=1,accel=3")
        self.assertEqual((rule.cost_layer.v_max, rule.cost_layer.accel), (1.0, 3.0))
        self.assertEqual(parse_rule(rule.spec), rule)
        with self.assertRaises(ValueError):
            parse_rule("motion_time:v_max=0")


if __name__ == "__main__":
    unittest.main()
