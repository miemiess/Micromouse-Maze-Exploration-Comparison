"""基础规则实验计划（src/basic/plan.py）：地图集合、开发 / 测试划分与算法清单。"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from basic.plan import (DEV_SEEDS, MAIN_ALGORITHMS, PLANS, build_plan,  # noqa: E402
                        plan_generated_names)
from core.algorithm_api import Maze, discover_algorithms  # noqa: E402
from core.experiments import available_plans, map_group  # noqa: E402


class BasicPlanTests(unittest.TestCase):
    def test_plan_map_set_exists(self):
        """实验计划的 120 张生成地图都在地图库中，且分组名称正确。"""
        names = plan_generated_names()
        self.assertEqual(len(names), 120)
        missing = [n for n in names if not (ROOT / "mazes" / "classic" / n).exists()]
        self.assertEqual(missing, [])
        maze = Maze.from_json(ROOT / "mazes" / "classic" / "gen_wilson_16x16_s3_l30.json")
        self.assertEqual(map_group(maze), "wilson_loop30")
        self.assertEqual(map_group(Maze.from_json(ROOT / "mazes" / "classic" / "gen_backtracker_16x16_s1.json")),
                         "backtracker_loop0")

    def test_dev_and_test_sets_are_disjoint(self):
        """开发集（种子 101～110）与测试集不重叠，且不进入任何正式实验。"""
        dev = plan_generated_names(DEV_SEEDS)
        self.assertEqual(len(dev), 120)
        self.assertEqual(set(dev) & set(plan_generated_names()), set())
        runs = {run.experiment: run for run in build_plan()}
        self.assertEqual(set(runs), {"main", "randomness"})
        used = {p.name for run in runs.values() for p in run.maze_paths}
        self.assertEqual(used & set(dev), set())

    def test_algorithms_are_basic_layer_and_registered(self):
        """实验 1 的 13 个算法都在基础层；消融变体由类属性声明；计划已注册为 --plan basic。"""
        infos, errors = discover_algorithms()
        self.assertEqual(errors, [])
        self.assertEqual(len(MAIN_ALGORITHMS), 13)
        self.assertTrue(all(infos[a].layer == "basic" for a in MAIN_ALGORITHMS))
        variants = {n for n, i in infos.items() if i.ablation_of == "prior_astar"}
        self.assertEqual(variants, {"prior_astar_no_penalty", "prior_astar_no_post", "prior_astar_fixed"})
        self.assertEqual(infos["prior_astar"].ablation_baseline, "repeated_astar")
        self.assertIn("basic", PLANS)
        self.assertIn("basic", available_plans())


if __name__ == "__main__":
    unittest.main()
