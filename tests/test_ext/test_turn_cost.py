"""E1 转弯代价规则：路线拆分、增量计价、规则最优路线（含独立实现交叉验证）与参照规划器。"""

import heapq
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import (Direction, Maze, Runner, load_algorithm, open_neighbours,  # noqa: E402
                                run_episode)
from core.rules import BASIC, Ruleset, parse_rule, quarter_turns, segments, turn_points  # noqa: E402
from ext.rules.turn_cost import TurnCostLayer  # noqa: E402

CLASSIC = ROOT / "mazes" / "classic"
MAPS = [CLASSIC / f"{name}.json" for name in
        ("external_1stworld", "external_uk2011f", "external_japan2017ef",
         "gen_wilson_16x16_s3", "gen_kruskal_16x16_s5_l30")]
TRADEOFF = ROOT / "tests" / "test_ext" / "fixtures" / "turn_cost_tradeoff.json"
EXPLORERS = ("dfs", "flood_fill", "repeated_astar", "wall_follower_left", "random_walk")


def turn_cost(weight: float) -> Ruleset:
    return Ruleset((TurnCostLayer(weight=weight),))


def reference_optimum(maze: Maze, weight: float) -> float:
    """独立实现：逐格移动的（格子, 朝向）Dijkstra，每步代价 1 + λ × 转向次数。"""
    start = (maze.start, maze.start_heading)
    best, heap = {start: 0.0}, [(0.0, 0, start)]
    counter = 0
    while heap:
        cost, _, (cell, heading) = heapq.heappop(heap)
        if cost > best[(cell, heading)]:
            continue
        if cell in maze.goals:
            return cost
        for move, neighbour in open_neighbours(maze, cell):
            total = cost + 1 + weight * quarter_turns(heading, move)
            if total < best.get((neighbour, move), float("inf")):
                best[(neighbour, move)] = total
                counter += 1
                heapq.heappush(heap, (total, counter, (neighbour, move)))
    raise AssertionError("goal unreachable")


class SegmentTests(unittest.TestCase):
    def test_segments_match_environment_counts(self):
        """直线段长度之和 = steps，转向之和 = turns_90（与环境口径一致）。"""
        for path in MAPS[:3]:
            maze = Maze.from_json(path)
            for name in EXPLORERS:
                with self.subTest(maze=path.stem, algorithm=name):
                    result = run_episode(maze, load_algorithm(name), seed=1)
                    parts = segments(result["path"], maze.start_heading)
                    self.assertEqual(sum(n for _, n in parts), result["steps"])
                    self.assertEqual(sum(t for t, _ in parts), result["turns_90"])
                    self.assertEqual(sum(q for _, q in turn_points(result["path"], maze.start_heading)),
                                     result["turns_90"])

    def test_segment_examples(self):
        """手算例子：朝北出发，北 2 格、东 1 格、掉头向西 1 格。"""
        path = [(0, 0), (0, 1), (0, 2), (1, 2), (0, 2)]
        self.assertEqual(segments(path, Direction.NORTH), [(0, 2), (1, 1), (2, 1)])
        self.assertEqual(turn_points(path, Direction.NORTH), [((0, 2), 1), ((1, 2), 2)])
        self.assertEqual(turn_cost(1.5).cost(path, Direction.NORTH), 4 + 1.5 * 3)
        self.assertIsNone(BASIC.cost(path, Direction.NORTH))


class TurnCostRuleTests(unittest.TestCase):
    def test_rule_cost_is_steps_plus_weighted_turns(self):
        """运行中增量计价的结果 = 步数 + λ × turns_90 = 对整条路线重新计价。"""
        for weight in (0.0, 0.5, 2.0):
            rule = turn_cost(weight)
            for path in MAPS[:2]:
                maze = Maze.from_json(path)
                for name in EXPLORERS:
                    with self.subTest(weight=weight, maze=path.stem, algorithm=name):
                        result = run_episode(maze, load_algorithm(name), seed=2, rule=rule)
                        self.assertAlmostEqual(result["rule_cost"],
                                               result["steps"] + weight * result["turns_90"])
                        self.assertAlmostEqual(result["rule_cost"],
                                               rule.cost(result["path"], maze.start_heading))

    def test_rule_does_not_change_movement(self):
        """代价层只改计价，不改环境：路线、步数、状态与基础规则完全相同。"""
        maze = Maze.from_json(MAPS[0])
        for name in EXPLORERS:
            base = run_episode(maze, load_algorithm(name), seed=4)
            ruled = run_episode(maze, load_algorithm(name), seed=4, rule=turn_cost(3))
            self.assertEqual((base["path"], base["status"]), (ruled["path"], ruled["status"]))

    def test_optimal_matches_independent_implementation(self):
        """按直线段搜索的最优代价 = 逐格（格子, 朝向）Dijkstra 的结果。"""
        for weight in (0.0, 0.7, 2.0, 5.0):
            for path in MAPS + [TRADEOFF]:
                maze = Maze.from_json(path)
                with self.subTest(weight=weight, maze=path.stem):
                    self.assertAlmostEqual(turn_cost(weight).optimal_cost(maze),
                                           reference_optimum(maze, weight))

    def test_optimal_is_lower_bound_and_route_is_consistent(self):
        """最优路线自身的代价等于最优代价，且不高于任何探索算法的规则代价。"""
        rule = turn_cost(1.5)
        for path in MAPS[:3]:
            maze = Maze.from_json(path)
            cost, route = rule.optimal_plan(maze)
            self.assertAlmostEqual(rule.cost(route, maze.start_heading), cost)
            for name in EXPLORERS[:3]:
                result = run_episode(maze, load_algorithm(name), rule=rule)
                self.assertGreaterEqual(result["rule_cost"] + 1e-9, cost)

    def test_tradeoff_fixture_switches_route_with_weight(self):
        """取舍地图：最短路 6 步 5 次转向，另一条 8 步 3 次转向；λ = 1 时两者相等，λ 越大越偏向少转弯。"""
        maze = Maze.from_json(TRADEOFF)
        shortest = run_episode(maze, load_algorithm("bfs"))
        self.assertEqual((shortest["steps"], shortest["turns_90"]), (6, 5))
        low = run_episode(maze, load_algorithm("rule_optimal"), rule=turn_cost(0.5))
        self.assertEqual((low["steps"], low["turns_90"], low["optimal_cost"]), (6, 5, 8.5))
        high = run_episode(maze, load_algorithm("rule_optimal"), rule=turn_cost(3))
        self.assertEqual((high["steps"], high["turns_90"], high["optimal_cost"]), (8, 3, 17.0))
        self.assertEqual(turn_cost(1).optimal_cost(maze), 11.0)
        self.assertEqual(turn_cost(3).cost(shortest["path"], maze.start_heading), 21.0)


class RuleOptimalPlannerTests(unittest.TestCase):
    def test_basic_rule_equals_bfs_length(self):
        """基础规则下，规则最优路线长度等于 BFS 最短路。"""
        for path in MAPS:
            maze = Maze.from_json(path)
            with self.subTest(maze=path.stem):
                optimal = run_episode(maze, load_algorithm("rule_optimal"))
                self.assertEqual(optimal["status"], "success")
                self.assertEqual(optimal["steps"], run_episode(maze, load_algorithm("bfs"))["steps"])

    def test_planner_receives_rule_through_configure(self):
        """规划器经 configure 拿到规则，规划结果的代价写入 stats。"""
        maze = Maze.from_json(MAPS[0])
        rule = parse_rule("turn_cost:weight=2")
        snap = Runner(maze, load_algorithm("rule_optimal"), rule=rule).run()
        self.assertEqual(snap.status, "success")
        self.assertAlmostEqual(snap.stats["rule_cost"], snap.stats["optimal_cost"])
        self.assertAlmostEqual(snap.stats["optimal_cost"], rule.optimal_cost(maze))


if __name__ == "__main__":
    unittest.main()
