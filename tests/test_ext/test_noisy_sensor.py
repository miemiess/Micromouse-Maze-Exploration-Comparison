"""E2 噪声观测层（src/ext/rules/noisy_sensor.py）与置信度重规划（src/ext/algorithms/belief_astar.py）。"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Direction as D, Maze, Runner, load_algorithm, run_episode  # noqa: E402
from core.environment import Observation  # noqa: E402
from core.rules import BASIC, Ruleset, parse_rule  # noqa: E402
from ext.rules.noisy_sensor import NoisySensorLayer  # noqa: E402

CLASSIC = ROOT / "mazes" / "classic"
MAPS = [CLASSIC / f"{name}.json" for name in
        ("external_1stworld", "external_uk2011f", "external_japan2017ef",
         "gen_wilson_16x16_s3", "gen_kruskal_16x16_s5_l30")]


def open_maze(start=(2, 2)) -> Maze:
    return Maze({"maze_id": "open_5x5", "width": 5, "height": 5, "start": list(start),
                 "start_heading": "N", "goals": [[4, 4]], "blocked_edges": []})


class Script:
    name = "script"
    supported_rules = {"noisy_sensor"}

    def __init__(self, *moves):
        self.moves = moves

    def reset(self, **_kwargs):
        self.directions, self.inputs = iter(self.moves), []

    def choose_direction(self, obs):
        self.inputs.append(obs)
        return next(self.directions)


class SensorModelTests(unittest.TestCase):
    def test_error_rates_follow_relative_direction(self):
        """无墙地图中央朝北：前 / 侧 / 后的误报率分别约为 1 − p_front、1 − p_side、1 − p_back。"""
        rule = parse_rule("noisy_sensor:p_front=0.9,p_side=0.8,p_back=0.7")
        maze, trials = open_maze(), 4000
        errors = {d: 0 for d in D}
        for seed in range(trials):
            for d in rule.make_env(maze, None, seed=seed).reset().walls:
                errors[d] += 1
        rates = {d: errors[d] / trials for d in D}
        self.assertAlmostEqual(rates[D.NORTH], 0.1, delta=0.02)
        self.assertAlmostEqual(rates[D.EAST], 0.2, delta=0.025)
        self.assertAlmostEqual(rates[D.WEST], 0.2, delta=0.025)
        self.assertAlmostEqual(rates[D.SOUTH], 0.3, delta=0.025)

    def test_boundary_always_correct_and_perfect_sensor_is_ideal(self):
        corner = open_maze(start=(0, 0))
        noisy = parse_rule("noisy_sensor:p_front=0.51,p_side=0.51,p_back=0.51")
        for seed in range(200):
            walls = noisy.make_env(corner, None, seed=seed).reset().walls
            self.assertTrue({D.SOUTH, D.WEST} <= walls)
        maze = Maze.from_json(MAPS[0])
        ideal = run_episode(maze, load_algorithm("belief_astar"), seed=3)
        perfect = run_episode(maze, load_algorithm("belief_astar"), seed=3,
                              rule=parse_rule("noisy_sensor:p_front=1,p_side=1,p_back=1"))
        self.assertEqual((ideal["path"], ideal["status"]), (perfect["path"], perfect["status"]))
        self.assertEqual(perfect["collisions"], 0)

    def test_noise_is_reproducible_by_seed(self):
        maze = Maze.from_json(MAPS[1])
        rule = parse_rule("noisy_sensor")
        runs = [run_episode(maze, load_algorithm("belief_astar"), seed=s, rule=rule)["path"] for s in (5, 5, 6)]
        self.assertEqual(runs[0], runs[1])
        self.assertNotEqual(runs[0], runs[2])

    def test_contact_feedback_is_reliable(self):
        """传感器很差时也一样：撞墙后的观测一定包含撞到的方向。"""
        maze = Maze({"maze_id": "contact", "width": 2, "height": 2, "start": [0, 0], "start_heading": "N",
                     "goals": [[0, 1]], "blocked_edges": [[[0, 0], [1, 0]]]})
        rule = parse_rule("noisy_sensor:p_front=0.51,p_side=0.51,p_back=0.51")
        for seed in range(50):
            script = Script(D.EAST, D.NORTH)
            snap = Runner(maze, script, seed=seed, rule=rule).run()
            self.assertIn(D.EAST, script.inputs[1].walls)
            self.assertEqual(script.inputs[1].collision_wall, D.EAST)
            self.assertEqual((snap.status, snap.stats["collisions"]), ("success", 1))

    def test_layer_defaults_and_combination(self):
        """噪声层默认撞墙后继续，叠加撞墙处理层可设上限；参数校验；对数几率权重。"""
        self.assertIsNone(parse_rule("noisy_sensor").collision_limit)
        rule = parse_rule("turn_cost:weight=2+noisy_sensor+collision:limit=5")
        self.assertEqual(rule.collision_limit, 5)
        self.assertEqual(parse_rule(rule.spec), rule)
        self.assertEqual([l.dimension for l in rule.layers], ["cost", "observation", "contact"])
        with self.assertRaises(ValueError):
            parse_rule("noisy_sensor:p_front=0.5")
        layer = NoisySensorLayer(p_front=0.9)
        self.assertAlmostEqual(layer.evidence_weight(D.NORTH, D.NORTH), math.log(9))
        self.assertEqual(NoisySensorLayer(p_back=1.0).evidence_weight(D.NORTH, D.SOUTH), math.inf)

    def test_only_declared_explorers_are_allowed(self):
        rule = parse_rule("noisy_sensor")
        maze = Maze.from_json(MAPS[0])
        for name in ("repeated_astar", "turn_aware_astar", "flood_fill"):
            with self.assertRaisesRegex(ValueError, "does not support"):
                Runner(maze, load_algorithm(name), rule=rule)
        self.assertTrue(rule.supports(load_algorithm("rule_optimal")))   # 已知地图规划器不受观测层影响
        self.assertEqual(run_episode(maze, load_algorithm("rule_optimal"), rule=rule)["collisions"], 0)


class BeliefAStarTests(unittest.TestCase):
    def test_fusion_accumulates_evidence(self):
        """两次读到有墙、一次读到没墙：融合后仍判为有墙；只信最近一次读数则判为没墙。"""
        rule = Ruleset((NoisySensorLayer(p_front=0.9, p_side=0.9, p_back=0.9),))
        for name, expect_wall in (("belief_astar", True), ("belief_astar_naive", False)):
            algo = load_algorithm(name)
            algo.configure(rule)
            algo.reset(width=3, height=3, start=(1, 1), goals=frozenset({(2, 2)}), initial_heading=D.NORTH)
            for walls in ({D.NORTH}, {D.NORTH}, set()):
                algo._observe(Observation((1, 1), D.NORTH, frozenset(walls), 0))
                algo.previous = None
            with self.subTest(algorithm=name):
                self.assertEqual(algo._believed_wall((1, 1), D.NORTH), expect_wall)

    def test_reaches_goal_under_noise(self):
        """默认噪声下，5 张固定地图 × 4 个种子全部到达；规则代价口径一致。"""
        rule = parse_rule("turn_cost:weight=1+noisy_sensor")
        for path in MAPS:
            maze = Maze.from_json(path)
            for seed in range(4):
                with self.subTest(maze=path.stem, seed=seed):
                    result = run_episode(maze, load_algorithm("belief_astar"), seed=seed, rule=rule)
                    self.assertEqual(result["status"], "success")
                    # 撞墙时的原地转向也计代价，所以规则代价 ≥ 只按实际路线计价
                    self.assertGreaterEqual(result["rule_cost"] + 1e-9,
                                            rule.cost(result["path"], maze.start_heading))
                    self.assertEqual(result["actions"], result["steps"] + result["collisions"])

    def test_ideal_observation_matches_turn_aware_astar(self):
        """没有噪声层时每次读数确定，与朝向 A* 走出相同路线。"""
        for path in MAPS[:3]:
            maze = Maze.from_json(path)
            for rule in (BASIC, parse_rule("turn_cost:weight=2")):
                a = run_episode(maze, load_algorithm("belief_astar"), rule=rule)
                b = run_episode(maze, load_algorithm("turn_aware_astar"), rule=rule)
                self.assertEqual(a["path"], b["path"])


if __name__ == "__main__":
    unittest.main()
