"""碰撞计数、接触反馈和规则组合的回归用例。"""

from dataclasses import dataclass, replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.algorithm_api import Direction as D, Maze, Runner
from core.rules import RuleLayer, Ruleset, parse_rule


def maze():
    return Maze(dict(maze_id="collision", width=2, height=2, start=[0, 0],
                     start_heading="N", goals=[[0, 1]], blocked_edges=[[[0, 0], [1, 0]]]))


class Script:
    name = "script"
    supported_rules = {"false_negative"}

    def __init__(self, *moves):
        self.moves = moves

    def reset(self, **kwargs):
        self.directions = iter(self.moves)
        self.inputs = []

    def choose_direction(self, obs):
        self.inputs.append(obs)
        return next(self.directions)


@dataclass(frozen=True)
class FalseNegative(RuleLayer):
    """测试观测层：东侧传感器始终漏报墙，但物理接触必须可靠。"""
    key = "false_negative"
    dimension = "observation"
    changes_observation = True

    def wrap_env(self, base):
        class Sensor:
            def __getattr__(self, name):
                return getattr(base, name)

            def reset(self):
                obs = base.reset()
                return replace(obs, walls=obs.walls - {D.EAST})

            def step(self, direction):
                result = base.step(direction)
                return replace(result, observation=replace(result.observation,
                                                           walls=result.observation.walls - {D.EAST}))
        return Sensor()


class CollisionTests(unittest.TestCase):
    def test_first_collision_and_illegal_direction(self):
        for spec in ("basic", "collision:limit=1"):
            r = Runner(maze(), Script(D.EAST), rule=parse_rule(spec))
            snap = r.step()
            self.assertEqual((snap.status, snap.heading, snap.stats["collisions"], snap.stats["steps"]),
                             ("invalid_action", D.NORTH, 1, 0))
        r = Runner(maze(), Script("E"), rule=parse_rule("collision:limit=unlimited"))
        snap = r.step()
        self.assertEqual((snap.status, snap.blocked, snap.stats["collisions"]), ("invalid_action", None, 0))

    def test_limit_and_budget(self):
        for limit, budget, status in ((2, 2, "collision_limit"), (3, 2, "budget_exceeded"),
                                       (None, 2, "budget_exceeded")):
            r = Runner(maze(), Script(D.EAST, D.EAST), rule=Ruleset(collision_limit=limit), max_steps=budget)
            first = r.step()
            self.assertEqual((first.status, first.position, first.heading), ("running", (0, 0), D.EAST))
            last = r.step()
            self.assertEqual(last.status, status)
            self.assertEqual((last.stats["actions"], last.stats["collisions"], last.stats["steps"],
                              last.stats["repeat_visits"], last.stats["turns_90"]), (2, 2, 0, 0, 1))
            self.assertEqual(r.env.path, [(0, 0)])

    def test_sensor_feedback_and_cost(self):
        for cost in ("turn_cost:weight=2", "motion_time"):
            rule = parse_rule(cost + "+collision:limit=unlimited").with_layer(FalseNegative())
            strategy = Script(D.EAST, D.NORTH)
            r = Runner(maze(), strategy, rule=rule, max_steps=2)
            snap = r.run()
            self.assertNotIn(D.EAST, strategy.inputs[0].walls)
            self.assertIn(D.EAST, strategy.inputs[1].walls)
            self.assertEqual(strategy.inputs[1].collision_wall, D.EAST)
            self.assertEqual((snap.status, snap.stats["actions"], snap.stats["steps"]), ("success", 2, 1))
            expected = 2 * rule.cost_model.turn_cost(1) + rule.cost_model.run_cost(1)
            self.assertAlmostEqual(snap.stats["rule_cost"], expected, places=6)

    def test_spec_roundtrip_and_validation(self):
        for value in ("unlimited", "2", "1"):
            rule = parse_rule(f"collision:limit={value}+turn_cost")
            self.assertEqual(parse_rule(rule.spec), rule)
            self.assertEqual(rule.metadata()["collision"]["limit"], rule.collision_limit)
        for value in ("-1", "0", "1.1", "x", "2+collision:limit=3"):
            with self.assertRaises(ValueError):
                parse_rule("collision:limit=" + value)

    def test_batch_csv_and_metadata(self):
        import csv
        import json
        from tempfile import TemporaryDirectory
        from core.experiments import main

        with TemporaryDirectory() as out:
            spec = "turn_cost:weight=2+collision:limit=3"
            main(["--maps", str(Path(__file__).parent / "fixtures/turn_cost_tradeoff.json"),
                  "--rule", spec, "--algorithms", "dfs", "--repeats", "1", "--out", out, "--no-plot"])
            with (Path(out) / "runs.csv").open() as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["actions"], row["steps"])
            self.assertEqual(row["collisions"], "0")
            meta = json.loads((Path(out) / "metadata.json").read_text())["rule"]
            self.assertEqual(meta["spec"], spec)
            self.assertEqual(meta["collision"], {"limit": 3})
