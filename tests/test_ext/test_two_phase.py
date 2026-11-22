"""D5 两阶段比赛（src/ext/rules/two_phase.py）与有界提前停止（src/ext/algorithms/bounded_explore.py）。"""

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Direction as D, Maze, MazeEnvironment, Runner, load_algorithm, run_episode  # noqa: E402
from core.rules import BASIC, parse_rule  # noqa: E402

CLASSIC = ROOT / "mazes" / "classic"
MAPS = [CLASSIC / f"{name}.json" for name in
        ("external_1stworld", "external_uk2011f", "gen_wilson_16x16_s103", "gen_kruskal_16x16_s105_l30")]
EPSILONS = {"bounded_explore_e0": 0.0, "bounded_explore_e10": 0.1, "bounded_explore_e25": 0.25}


def corridor() -> Maze:
    """1×3 走廊：起点 (0,0) 朝北，目标 (0,1)。"""
    return Maze({"maze_id": "corridor", "width": 1, "height": 3, "start": [0, 0], "start_heading": "N",
                 "goals": [[0, 1]], "blocked_edges": []})


class EnvironmentTests(unittest.TestCase):
    def test_goal_does_not_end_exploration(self):
        env = MazeEnvironment(corridor(), stop_at_goal=False)
        with self.assertRaises(ValueError):
            env.finish("success")                      # 还没到过目标，不能宣布探索成功
        env.step(D.NORTH)
        self.assertEqual((env.status, env.goal_reached), ("running", True))
        env.step(D.NORTH)                              # 越过目标继续探索
        env.finish("success")
        self.assertEqual(env.status, "success")
        self.assertTrue(env.summary()["goal_reached"])

    def test_budget_after_goal_counts_as_finished_exploration(self):
        env = MazeEnvironment(corridor(), max_steps=2, stop_at_goal=False)
        env.step(D.NORTH)
        env.step(D.NORTH)
        self.assertEqual(env.status, "success")
        env = MazeEnvironment(Maze({**corridor_data(), "goals": [[0, 2]]}), max_steps=1, stop_at_goal=False)
        env.step(D.NORTH)
        self.assertEqual(env.status, "budget_exceeded")

    def test_basic_rule_unchanged(self):
        env = MazeEnvironment(corridor())
        env.step(D.NORTH)
        self.assertEqual(env.status, "success")
        self.assertNotIn("goal_reached", env.summary())


def corridor_data() -> dict:
    return {"maze_id": "corridor", "width": 1, "height": 3, "start": [0, 0], "start_heading": "N",
            "goals": [[0, 1]], "blocked_edges": []}


class TwoPhaseRuleTests(unittest.TestCase):
    def test_spec_and_score(self):
        rule = parse_rule("turn_cost:weight=2+two_phase:explore_divisor=10")
        self.assertEqual(parse_rule(rule.spec), rule)
        self.assertEqual([l.dimension for l in rule.layers], ["cost", "flow"])
        with self.assertRaises(ValueError):
            parse_rule("two_phase:explore_divisor=0.5")
        result = run_episode(Maze.from_json(MAPS[0]), load_algorithm("repeated_astar"), rule=rule)
        self.assertAlmostEqual(result["total_score"], result["sprint_cost"] + result["explore_cost"] / 10, places=5)
        self.assertAlmostEqual(result["explore_cost"], result["rule_cost"] + result["return_cost"], places=5)

    def test_non_exploring_algorithms_stop_at_first_arrival(self):
        """没有声明 explores_after_goal 的算法第一次到达目标即结束探索：路线与基础规则相同。"""
        rule = parse_rule("two_phase")
        for path in MAPS[:2]:
            maze = Maze.from_json(path)
            for name in ("repeated_astar", "flood_fill", "dfs", "turn_aware_astar"):
                with self.subTest(maze=path.stem, algorithm=name):
                    base = run_episode(maze, load_algorithm(name))
                    two = run_episode(maze, load_algorithm(name), rule=rule)
                    self.assertEqual((two["status"], two["path"]), ("success", base["path"]))
                    self.assertGreaterEqual(two["sprint_ratio"], 1.0)
                    self.assertEqual(two["optimal_sprint_cost"], BASIC.optimal_cost(maze))

    def test_sprint_uses_only_confirmed_edges(self):
        """冲刺代价 ≥ 已知地图最优；返回起点后探索代价 = 运行代价 + 返回代价。"""
        maze = Maze.from_json(MAPS[1])
        result = run_episode(maze, load_algorithm("dfs"), rule=parse_rule("two_phase"))
        self.assertGreaterEqual(result["sprint_cost"], result["optimal_sprint_cost"])
        self.assertEqual(result["explore_cost"], result["steps"] + result["return_cost"])

    def test_noise_confirms_only_traversed_edges(self):
        """噪声观测下读数不可信，冲刺只能走实际走过的边：冲刺代价 ≤ 探索路线上第一次到达目标的路程。"""
        maze = Maze.from_json(MAPS[0])
        result = run_episode(maze, load_algorithm("belief_astar"), seed=1, rule=parse_rule("noisy_sensor+two_phase"))
        self.assertEqual(result["status"], "success")
        path = [tuple(c) for c in result["path"]]
        traversed = {frozenset(e) for e in zip(path, path[1:])}
        cells = {c for e in traversed for c in e}
        self.assertLessEqual(result["sprint_cost"], result["steps"])
        self.assertTrue(set(maze.goals) & cells)


class BoundedExploreTests(unittest.TestCase):
    def test_sprint_bound_is_guaranteed(self):
        """核心保证：停止时冲刺代价 ≤ (1 + ε) × 已知地图最优；ε = 0 时恰为最优。"""
        for spec in ("two_phase", "turn_cost:weight=2+two_phase", "motion_time+two_phase"):
            rule = parse_rule(spec)
            for path in MAPS:
                maze = Maze.from_json(path)
                for name, eps in EPSILONS.items():
                    with self.subTest(rule=spec, maze=path.stem, algorithm=name):
                        result = run_episode(maze, load_algorithm(name), rule=rule)
                        self.assertEqual(result["status"], "success")
                        self.assertLessEqual(result["sprint_cost"], (1 + eps) * result["optimal_sprint_cost"] + 1e-6)
                        self.assertLessEqual(result["lower_bound"], result["optimal_sprint_cost"] + 1e-6)
                        if eps == 0:
                            self.assertAlmostEqual(result["sprint_cost"], result["optimal_sprint_cost"])

    def test_explores_beyond_first_arrival_and_basic_rule_still_works(self):
        maze = Maze.from_json(MAPS[1])
        rule = parse_rule("two_phase")
        explorer = run_episode(maze, load_algorithm("bounded_explore_e0"), rule=rule)
        stopper = run_episode(maze, load_algorithm("repeated_astar"), rule=rule)
        self.assertGreater(explorer["steps"], stopper["steps"])
        self.assertLessEqual(explorer["sprint_cost"], stopper["sprint_cost"])
        basic = run_episode(maze, load_algorithm("bounded_explore_e0"))     # 基础规则：到达目标即结束
        self.assertEqual(basic["status"], "success")

    def test_experiment_columns(self):
        from core.experiments import FLOW_RUN_FIELDS, main
        with TemporaryDirectory() as out:
            main(["--maps", str(MAPS[2]), "--rule", "two_phase", "--algorithms", "repeated_astar",
                  "bounded_explore_e10", "--out", out, "--no-plot"])
            with (Path(out) / "runs.csv").open(encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(all(row[k] != "" for row in rows for k in FLOW_RUN_FIELDS))
            self.assertIn("平均成绩", (Path(out) / "summary.md").read_text(encoding="utf-8"))

    def test_runner_snapshot_has_scores_only_after_finish(self):
        runner = Runner(Maze.from_json(MAPS[2]), load_algorithm("bounded_explore_e25"), rule=parse_rule("two_phase"))
        runner.run(max_decisions=3)
        self.assertNotIn("total_score", runner.snapshot().stats)
        runner.run()
        self.assertIsNotNone(runner.snapshot().stats["total_score"])


if __name__ == "__main__":
    unittest.main()
