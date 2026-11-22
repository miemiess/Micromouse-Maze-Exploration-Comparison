"""事后验证脚本 src/ext/posthoc.py：诊断变体不改变原算法行为；去掉接触反馈后撞墙不再记为确定的墙。"""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from core.algorithm_api import Direction, run_episode  # noqa: E402
from core.environment import ContactObservation, Maze  # noqa: E402
from core.rules import parse_rule  # noqa: E402
from ext.algorithms.belief_astar import BeliefAStarStrategy  # noqa: E402
from ext.posthoc import VARIANTS, rescore  # noqa: E402

NOISY = parse_rule("noisy_sensor:p_front=0.8,p_side=0.7,p_back=0.6")
MAZE = ROOT / "mazes" / "classic" / "gen_backtracker_16x16_s1.json"


class PosthocTests(unittest.TestCase):
    def test_probe_variant_reproduces_original(self):
        maze = Maze.from_json(MAZE)
        original = run_episode(maze, BeliefAStarStrategy(), seed=3, rule=NOISY)
        probed = VARIANTS["belief_astar"]()
        result = run_episode(maze, probed, seed=3, rule=NOISY)
        self.assertEqual((original["steps"], original["collisions"]), (result["steps"], result["collisions"]))
        self.assertLessEqual(probed.fallback_collisions, result["collisions"])

    def test_nocontact_ignores_collision(self):
        for name, certain in (("belief_astar", True), ("belief_nocontact", False)):
            algo = VARIANTS[name]()
            algo.configure(NOISY)
            algo.reset(width=4, height=4, start=(0, 0), goals=[(3, 3)], initial_heading=Direction.NORTH)
            obs = ContactObservation((1, 1), Direction.NORTH, frozenset(), 1, Direction.NORTH)
            algo.choose_direction(obs)
            score = algo.score[frozenset(((1, 1), (1, 2)))]
            self.assertEqual(math.isinf(score) and score > 0, certain, name)

    def test_rescore_matches_formula(self):
        rows = [{"status": "success", "sprint_cost": "10", "explore_cost": "60"}, {"status": "failed"}]
        out = rescore(rows, 30)
        self.assertAlmostEqual(out[0]["score"], 12.0)
        self.assertNotIn("score", out[1])


if __name__ == "__main__":
    unittest.main()
