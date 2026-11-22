"""E3-1 验收测试：懂规则的重复 A*（turn_aware_astar / turn_aware_astar_w2）。

任务说明见 Docs/ext/tasks/E3-1-turn-aware-astar.md。算法文件建立之前，本文件的测试全部跳过；
建立之后自动生效。不要为了通过测试修改本文件——有疑问在任务说明的“问题记录”里写明，交给负责人决定。
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import EXPLORE, Maze, Runner, discover_algorithms, run_episode  # noqa: E402
from core.rules import BASIC, parse_rule  # noqa: E402

MODULE = "ext.algorithms.turn_aware_astar"
AVAILABLE = importlib.util.find_spec(MODULE) is not None
NAMES = {"turn_aware_astar": 1.0, "turn_aware_astar_w2": 2.0}
RULES = [BASIC, parse_rule("turn_cost:weight=2"), parse_rule("turn_cost:weight=0"), parse_rule("motion_time")]
CLASSIC = ROOT / "mazes" / "classic"
MAPS = [CLASSIC / f"{name}.json" for name in
        ("external_1stworld", "external_uk2011f", "external_japan2017ef",
         "gen_wilson_16x16_s3", "gen_kruskal_16x16_s5_l30")]


def open_maze() -> Maze:
    """没有内部墙的 6×6 地图：乐观地图等于真值地图，探索结果应等于规则最优。"""
    return Maze({"maze_id": "open_6x6", "width": 6, "height": 6, "start": [0, 0],
                 "start_heading": "N", "goals": [[4, 3]], "blocked_edges": []})


def cost_of(result: dict) -> float:
    """规则代价；基础规则下没有 rule_cost，用步数。"""
    return result.get("rule_cost", result["steps"])


@unittest.skipUnless(AVAILABLE, "E3-1 尚未实现：见 Docs/ext/tasks/E3-1-turn-aware-astar.md")
class TurnAwareAStarAcceptance(unittest.TestCase):
    def setUp(self):
        self.infos = discover_algorithms(layer="ext")[0]

    def create(self, name):
        return self.infos[name].create()

    def test_registered_as_rule_aware_explorers(self):
        """两个算法都被自动发现：扩展层、探索类、为转弯代价与运动时间设计。"""
        for name in NAMES:
            with self.subTest(algorithm=name):
                info = self.infos[name]
                self.assertEqual((info.layer, info.mode), ("ext", EXPLORE))
                self.assertEqual(info.designed_for, frozenset({"turn_cost", "motion_time"}))
                self.assertTrue(info.doc)

    def test_does_not_read_ground_truth(self):
        """探索算法只能用观测：源码中不得出现读取真值地图的工具。"""
        source = (ROOT / "src" / "ext" / "algorithms" / "turn_aware_astar.py").read_text(encoding="utf-8")
        for forbidden in ("maze_walls", "open_neighbours", "has_wall(", "maze_blocked", "from_json", "._walls"):
            self.assertNotIn(forbidden, source)

    def test_open_map_matches_rule_optimum(self):
        """无墙地图上没有意外：w = 1 的代价等于规则最优，w = 2 不超过 2 倍；只规划一次。"""
        maze = open_maze()
        for rule in RULES:
            optimal = rule.optimal_cost(maze)
            for name, weight in NAMES.items():
                with self.subTest(rule=rule.spec, algorithm=name):
                    result = run_episode(maze, self.create(name), rule=rule)
                    self.assertEqual(result["status"], "success")
                    if weight == 1.0:
                        self.assertAlmostEqual(cost_of(result), optimal)
                    else:
                        self.assertLessEqual(cost_of(result), weight * optimal + 1e-9)
                    self.assertEqual(result["replans"], 1)

    def test_reaches_goal_on_classic_maps(self):
        """固定地图、每套规则下都到达目标；规则代价不低于规则最优（下界）。"""
        for path in MAPS:
            maze = Maze.from_json(path)
            for rule in RULES:
                optimal = rule.optimal_cost(maze)
                for name in NAMES:
                    with self.subTest(maze=path.stem, rule=rule.spec, algorithm=name):
                        result = run_episode(maze, self.create(name), rule=rule)
                        self.assertEqual(result["status"], "success")
                        self.assertIsNone(result["error"])
                        self.assertGreaterEqual(cost_of(result) + 1e-9, optimal)

    def test_stats_and_determinism(self):
        """stats() 报告 replans 与 expanded_nodes；同一地图重复运行路线完全相同（无随机性）。"""
        maze = Maze.from_json(MAPS[0])
        rule = parse_rule("turn_cost:weight=2")
        for name in NAMES:
            with self.subTest(algorithm=name):
                first = run_episode(maze, self.create(name), rule=rule)
                second = run_episode(maze, self.create(name), rule=rule)
                self.assertEqual(first["path"], second["path"])
                self.assertGreaterEqual(first["replans"], 1)
                self.assertLessEqual(first["replans"], first["steps"])
                self.assertGreater(first["expanded_nodes"], 0)

    def test_rule_is_reconfigured_between_runs(self):
        """同一个对象换规则后重新运行，使用的是新规则（configure 生效，没有残留状态）。"""
        maze = open_maze()
        algorithm = self.create("turn_aware_astar")
        for rule in (parse_rule("turn_cost:weight=5"), BASIC, parse_rule("turn_cost:weight=5")):
            runner = Runner(maze, algorithm, rule=rule)
            runner.run()
            self.assertAlmostEqual(cost_of(runner.summary()), rule.optimal_cost(maze))

    def test_debug_view_for_gui(self):
        """debug_view() 提供上位机显示所需的 known_walls 与 plan。"""
        runner = Runner(Maze.from_json(MAPS[1]), self.create("turn_aware_astar"), rule=parse_rule("turn_cost"))
        runner.run(max_decisions=10)
        debug = runner.debug
        self.assertIn("known_walls", debug)
        self.assertIn("plan", debug)


if __name__ == "__main__":
    unittest.main()
