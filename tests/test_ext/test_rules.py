"""E0 验收：规则对象（基础规则 + 叠加层）、Runner / 实验框架的规则钩子与分层约束。"""

import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Maze, Runner, load_algorithm, run_episode  # noqa: E402
from core.experiments import main  # noqa: E402
from core.rules import (BASIC, CostLayer, RuleLayer, Ruleset, available_layers,  # noqa: E402
                        parse_rule, preset_rules)
from ext.rules.motion_time import MotionTimeLayer  # noqa: E402
from ext.rules.turn_cost import TurnCostLayer  # noqa: E402

MAP = ROOT / "mazes" / "classic" / "external_1stworld.json"


@dataclass(frozen=True)
class _ShortBudget(RuleLayer):
    """测试用观测层：改变观测（因此只对声明支持的算法开放），并把移动预算压到 2 步。"""
    key = "short_budget"
    title = "短预算"
    dimension = "observation"
    changes_observation = True

    def wrap_env(self, env):
        env.max_steps = 2
        return env


class RulesetTests(unittest.TestCase):
    def test_basic_is_default_and_adds_nothing(self):
        """不传规则与显式基础规则结果完全相同，且不追加任何规则字段（基础结果格式不变）。"""
        maze = Maze.from_json(MAP)
        for name in ("random_walk", "bfs", "repeated_astar"):
            default = run_episode(maze, load_algorithm(name), seed=3)
            explicit = run_episode(maze, load_algorithm(name), seed=3, rule=BASIC)
            for result in (default, explicit):
                result.pop("compute_seconds")
            self.assertEqual(default, explicit)
            self.assertNotIn("rule_cost", default)

    def test_composition_key_spec_title(self):
        """规则 = 基础规则 + 叠加层；每个维度最多一层；spec 可被 parse_rule 还原。"""
        self.assertTrue(BASIC.is_basic)
        self.assertEqual((BASIC.key, BASIC.spec, BASIC.title), ("basic", "basic", "基础规则"))
        rule = Ruleset((TurnCostLayer(weight=2),))
        self.assertEqual(rule.key, "turn_cost")
        self.assertEqual(rule.spec, "turn_cost:weight=2")
        self.assertEqual(rule.title, "基础规则 + 转弯代价（λ = 2）")
        self.assertEqual(parse_rule(rule.spec), rule)
        self.assertEqual(hash(parse_rule("turn_cost:weight=2")), hash(rule))
        with self.assertRaisesRegex(ValueError, "每个维度最多叠加一层"):
            Ruleset((TurnCostLayer(), MotionTimeLayer()))
        self.assertEqual(rule.with_layer(MotionTimeLayer()).key, "motion_time")
        self.assertEqual(rule.with_layer(None, "cost"), BASIC)
        combined = Ruleset((_ShortBudget(), TurnCostLayer()))
        self.assertEqual(combined.key, "turn_cost+short_budget")  # 按维度固定顺序

    def test_parse_rule_errors(self):
        with self.assertRaisesRegex(ValueError, "unknown rule layer"):
            parse_rule("nope")
        with self.assertRaisesRegex(ValueError, "has no parameter"):
            parse_rule("turn_cost:lambda=2")
        with self.assertRaisesRegex(ValueError, "non-negative"):
            parse_rule("turn_cost:weight=-1")

    def test_layers_are_discovered_from_ext(self):
        """src/ext/rules/ 中的层被自动发现；预设规则 = 基础规则 + 每个层各一套。"""
        layers = available_layers()
        self.assertEqual(layers["turn_cost"], TurnCostLayer)
        self.assertEqual(layers["motion_time"], MotionTimeLayer)
        self.assertTrue(all(issubclass(c, CostLayer) for c in layers.values()))
        self.assertEqual(set(preset_rules()), {"basic", "turn_cost", "motion_time"})

    def test_core_does_not_import_ext(self):
        """分层约束：公共接口层 src/core/ 不静态导入扩展层（规则层只经自动发现接入）。"""
        for path in (ROOT / "src" / "core").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("from ext", text, path.name)
            self.assertNotIn("import ext", text, path.name)


class RunnerHookTests(unittest.TestCase):
    def test_observation_layer_needs_declared_support_and_wraps_env(self):
        """改变观测的层只对声明支持的算法开放；wrap_env 生效；configure 在每次规划前调用。"""
        rule = Ruleset((_ShortBudget(),))
        maze = Maze.from_json(MAP)
        planner = load_algorithm("bfs")
        with self.assertRaisesRegex(ValueError, "does not support"):
            Runner(maze, planner, rule=rule)
        planner.supported_rules = {"short_budget"}
        order = []
        plan = planner.plan
        planner.configure = lambda received: order.append(received)

        def record_plan(m):
            order.append("plan")
            return plan(m)
        planner.plan = record_plan
        runner = Runner(maze, planner, rule=rule)
        runner.reset()
        self.assertEqual(order, [rule, "plan", rule, "plan"])
        snap = runner.run()
        self.assertEqual((snap.status, snap.stats["steps"]), ("budget_exceeded", 2))

    def test_cost_layers_open_to_every_algorithm(self):
        """代价层不改变观测：所有算法都能运行，结果多出 rule_cost。"""
        rule = parse_rule("turn_cost")
        result = run_episode(Maze.from_json(MAP), load_algorithm("dfs"), rule=rule)
        self.assertEqual(result["rule_cost"], result["steps"] + result["turns_90"])


class ExperimentRuleTests(unittest.TestCase):
    def test_cli_records_rule_and_cost_columns(self):
        """--rule 写入 metadata（含 spec），runs.csv 追加规则代价列；基础规则不追加。"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            main(["--rule", "turn_cost:weight=2", "--maps", str(MAP), "--algorithms", "dfs",
                  "rule_optimal", "--out", str(out / "tc"), "--no-plot"])
            metadata = json.loads((out / "tc" / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["rule"], parse_rule("turn_cost:weight=2").metadata())
            header = (out / "tc" / "runs.csv").read_text(encoding="utf-8").splitlines()[0]
            self.assertTrue(header.endswith("rule,rule_cost,optimal_rule_cost,rule_cost_ratio"))
            self.assertIn("规则：基础规则 + 转弯代价", (out / "tc" / "summary.md").read_text(encoding="utf-8"))
            main(["--maps", str(MAP), "--algorithms", "dfs", "--out", str(out / "basic"), "--no-plot"])
            header = (out / "basic" / "runs.csv").read_text(encoding="utf-8").splitlines()[0]
            self.assertTrue(header.endswith("peak_memory_bytes,error"))

    def test_plan_rejects_extra_rule(self):
        """正式计划自带规则，--plan 与 --rule 不能同时使用。"""
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            main(["--plan", "basic", "--rule", "turn_cost", "--out", tmp])


if __name__ == "__main__":
    unittest.main()
