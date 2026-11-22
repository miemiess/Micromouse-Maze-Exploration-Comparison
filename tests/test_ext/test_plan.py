"""扩展实验计划（src/ext/plan.py）：地图划分固定且互不重叠、划分文件与代码一致、计划可注册。只检查设置，不运行实验。"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.experiments import available_plans  # noqa: E402
from ext.plan import (NOISE_ALGORITHMS, NOISE_RULES, NOISE_SEEDS, SPLIT_FILE, TURN_ALGORITHMS,  # noqa: E402
                      TURN_RULES, build_noise, build_turn, split)


class ExtPlanTests(unittest.TestCase):
    def test_split_is_fixed_and_disjoint(self):
        s = split()
        self.assertEqual(s, split())                                   # 固定种子，重复计算结果相同
        self.assertEqual(set(s["dev"]) & set(s["test"]), set())
        self.assertLessEqual(set(s["noise"]), set(s["test"]))
        self.assertEqual(len(s["noise"]), 200)
        for group in ("dev", "test"):                                  # 两组都同时包含外部图与生成图（分层）
            self.assertTrue(any(m.startswith("external_") for m in s[group]))
            self.assertTrue(any(m.startswith("gen_") for m in s[group]))
        dev_seed = re.compile(r"_s1(0[1-9]|10)(_|$)")                  # 开发生成图：种子 101～110
        self.assertFalse(any(dev_seed.search(m) for m in s["test"]))
        self.assertEqual(sum(bool(dev_seed.search(m)) for m in s["dev"]), 120)

    def test_split_file_matches_code(self):
        data = json.loads(SPLIT_FILE.read_text(encoding="utf-8"))
        self.assertEqual({k: data[k] for k in ("dev", "test", "noise")}, split())

    def test_plans_are_registered_and_valid(self):
        plans = available_plans()
        self.assertEqual(plans["ext_turn"][1], "ext/turn")
        self.assertEqual(plans["ext_noise"][1], "ext/noise")
        turn, noise = build_turn(), build_noise()
        self.assertEqual([r.experiment for r in turn], list(TURN_RULES))
        self.assertEqual([r.experiment for r in noise], list(NOISE_RULES))
        for run in turn:
            self.assertEqual(run.algorithms, TURN_ALGORITHMS)
            self.assertTrue(run.has_rule_cost)
            self.assertEqual(len(run.maze_paths), len(split()["test"]))
        for run in noise:
            self.assertEqual((run.algorithms, run.seeds), (NOISE_ALGORITHMS, NOISE_SEEDS))
        self.assertEqual([r.rule.collision_limit for r in noise], [1, None, None, None])
        two = plans["ext_two_phase"][0]()
        self.assertEqual(plans["ext_two_phase"][1], "ext/two_phase")
        self.assertEqual([r.experiment for r in two], ["steps", "lambda_2"])
        self.assertTrue(all(r.has_flow and len(r.maze_paths) == len(split()["test"]) for r in two))


if __name__ == "__main__":
    unittest.main()
