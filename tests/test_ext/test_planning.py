"""公共规划工具（core.planning）与扩展算法的接入约定。

- 已知墙记录与乐观地图；
- （格子, 朝向）搜索：A*（下界启发式）与 Dijkstra 代价相同、扩展更少；加权 A* 不超过 w 倍；
- 启发式不高估（逐状态与真实剩余代价比较）；
- 探索算法的 stats() 并入运行统计；designed_for 登记；
- 每个扩展算法在每套规则下都能正常运行、规则代价口径一致（新增算法自动纳入检查）。
"""

import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import (Direction, Maze, Runner, discover_algorithms, load_algorithm,  # noqa: E402
                                run_episode)
from core.environment import Observation  # noqa: E402
from core.planning import KnownWalls, cost_lower_bound, heading_search, maze_blocked  # noqa: E402
from core.rules import BASIC, Ruleset, available_layers, parse_rule, preset_rules  # noqa: E402

CLASSIC = ROOT / "mazes" / "classic"
MAPS = [CLASSIC / f"{name}.json" for name in
        ("external_1stworld", "external_uk2011f", "gen_wilson_16x16_s3", "gen_kruskal_16x16_s5_l30")]
TRADEOFF = ROOT / "tests" / "test_ext" / "fixtures" / "turn_cost_tradeoff.json"
RULES = [BASIC, parse_rule("turn_cost:weight=2"), parse_rule("motion_time")]


def truth(maze: Maze):
    return maze_blocked(maze.width, maze.height, maze.walls)


class KnownWallsTests(unittest.TestCase):
    def test_observe_and_optimistic_moves(self):
        walls = KnownWalls(4, 4)
        obs = Observation(position=(0, 0), heading=Direction.NORTH, walls=frozenset({Direction.NORTH}), step_count=0)
        new = walls.observe(obs)
        self.assertEqual(new, {frozenset(((0, 0), (0, 1)))})
        self.assertEqual(walls.observe(obs), set())                    # 再次观测不算新墙
        self.assertTrue(walls.blocked((0, 0), Direction.NORTH))         # 已知墙
        self.assertTrue(walls.blocked((0, 0), Direction.WEST))          # 地图边界
        self.assertFalse(walls.blocked((1, 1), Direction.NORTH))        # 未知边视为通路
        self.assertEqual([d for d, _ in walls.open_moves((0, 0))], [Direction.EAST])
        self.assertTrue(walls.route_blocked([(1, 0), (0, 0), (0, 1)]))
        self.assertEqual(len(walls), 1)


class HeadingSearchTests(unittest.TestCase):
    def test_astar_matches_dijkstra_with_fewer_expansions(self):
        """下界启发式的 A* 与 Dijkstra 最优代价相同，且扩展的状态更少。"""
        for rule in RULES:
            cost = rule.cost_model
            plain_total = astar_total = 0
            for path in MAPS + [TRADEOFF]:
                maze = Maze.from_json(path)
                with self.subTest(rule=rule.key, maze=path.stem):
                    plain = heading_search(maze.start, maze.start_heading, maze.goals, truth(maze), cost)
                    astar = heading_search(maze.start, maze.start_heading, maze.goals, truth(maze), cost,
                                           heuristic=lambda c, h: cost_lower_bound(cost, c, h, maze.goals))
                    self.assertAlmostEqual(astar.cost, plain.cost)
                    if rule.cost_layer is not None:
                        self.assertAlmostEqual(rule.cost(astar.route, maze.start_heading), astar.cost)
                    plain_total += plain.expanded
                    astar_total += astar.expanded
            self.assertLess(astar_total, plain_total)

    def test_weighted_astar_within_bound(self):
        """加权 A*（w = 2）的路线代价 ≤ 2 × 最优。"""
        for rule in RULES:
            cost = rule.cost_model
            for path in MAPS:
                maze = Maze.from_json(path)
                optimal = rule.optimal_cost(maze)
                weighted = heading_search(maze.start, maze.start_heading, maze.goals, truth(maze), cost,
                                          heuristic=lambda c, h: cost_lower_bound(cost, c, h, maze.goals),
                                          weight=2.0)
                self.assertLessEqual(weighted.cost, 2 * optimal + 1e-9)

    def test_lower_bound_never_overestimates(self):
        """随机抽取（格子, 朝向），启发式 ≤ 从该状态出发的真实最优代价。"""
        rng = random.Random(7)
        for rule in RULES:
            cost = rule.cost_model
            for path in MAPS[:2]:
                maze = Maze.from_json(path)
                for _ in range(40):
                    cell = (rng.randrange(maze.width), rng.randrange(maze.height))
                    heading = rng.choice(list(Direction))
                    exact = heading_search(cell, heading, maze.goals, truth(maze), cost).cost
                    self.assertLessEqual(cost_lower_bound(cost, cell, heading, maze.goals), exact + 1e-9)

    def test_cost_layers_satisfy_heuristic_assumptions(self):
        """启发式要求 run_cost 单调不减且次可加：检查每个已发现的代价层（默认参数）。"""
        for key, cls in available_layers().items():
            layer = cls()
            if not hasattr(layer, "run_cost"):
                continue
            with self.subTest(layer=key):
                for a in range(1, 17):
                    self.assertLessEqual(layer.run_cost(a), layer.run_cost(a + 1) + 1e-12)
                    for b in range(1, 17 - a):
                        self.assertLessEqual(layer.run_cost(a + b), layer.run_cost(a) + layer.run_cost(b) + 1e-12)

    def test_unreachable(self):
        maze = Maze.from_json(MAPS[0])
        result = heading_search(maze.start, maze.start_heading, maze.goals, lambda c, d: True, BASIC.cost_model)
        self.assertFalse(result.found)
        self.assertEqual(result.expanded, 4)   # 只能原地转向：起点格的 4 个朝向


class _CountingExplorer:
    """测试用探索策略：沿右手前进，stats() 报告决策次数。"""
    name = "_counting"
    designed_for = ("turn_cost",)

    def reset(self, **_kwargs):
        self.calls = 0

    def choose_direction(self, observation):
        self.calls += 1
        free = [d for d in Direction if d not in observation.walls]
        return free[0] if free else None

    def stats(self):
        return {"expanded_nodes": self.calls}


class InterfaceTests(unittest.TestCase):
    def test_exploration_stats_are_collected(self):
        """探索算法的 stats() 每步读取，进入快照与 run_episode 结果。"""
        maze = Maze.from_json(MAPS[0])
        runner = Runner(maze, _CountingExplorer(), max_steps=20)
        runner.run()
        self.assertEqual(runner.snapshot().stats["expanded_nodes"], runner.snapshot().decision)
        result = run_episode(maze, _CountingExplorer(), max_steps=20)
        self.assertEqual(result["expanded_nodes"], 20)

    def test_designed_for_uses_known_layer_keys(self):
        """designed_for 只能写已存在的规则层 key；只影响标记，不影响能否运行。"""
        layers = set(available_layers())
        for name, info in discover_algorithms()[0].items():
            with self.subTest(algorithm=name):
                self.assertLessEqual(info.designed_for, layers)
                self.assertFalse(info.designed_for_rule(BASIC))
                if info.designed_for:
                    self.assertTrue(info.designed_for_rule(parse_rule(sorted(info.designed_for)[0])))


class ExtAlgorithmContractTests(unittest.TestCase):
    """每个扩展算法（src/ext/algorithms/）都要满足的最低要求，新增算法自动纳入。"""

    def test_every_ext_algorithm_runs_under_every_rule(self):
        infos = discover_algorithms(layer="ext")[0]
        self.assertIn("rule_optimal", infos)
        for rule in preset_rules().values():
            for name, info in infos.items():
                if not rule.supports(info):
                    continue
                for path in MAPS[:2] + [TRADEOFF]:
                    maze = Maze.from_json(path)
                    with self.subTest(rule=rule.key, algorithm=name, maze=path.stem):
                        result = run_episode(maze, info.create(), seed=1, rule=rule)
                        self.assertIsNone(result["error"])
                        self.assertNotEqual(result["status"], "invalid_action")
                        self.assertEqual(result["status"], "success")
                        if rule.cost_layer is not None:
                            self.assertAlmostEqual(result["rule_cost"],
                                                   rule.cost(result["path"], maze.start_heading))
                            self.assertGreaterEqual(result["rule_cost"] + 1e-9, rule.optimal_cost(maze))


if __name__ == "__main__":
    unittest.main()
