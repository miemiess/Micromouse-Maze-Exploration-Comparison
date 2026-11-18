"""src/ 中各算法的验证：DFS、贪心 DFS、Flood-Fill、重复 A*、沿墙法、随机游走（探索），
BFS、A*（已知地图规划）。

探索算法只依赖观测、能到达目标或正确判定无路、结果可复现；BFS 给出最短路参照。
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from algorithm_api import run_episode  # noqa: E402
from astar import AStarPlanner  # noqa: E402
from bfs import BfsPlanner  # noqa: E402
from dfs import DfsStrategy  # noqa: E402
from environment import Maze, MazeEnvironment  # noqa: E402
from flood_fill import FloodFillStrategy  # noqa: E402
from greedy_dfs import GreedyDfsStrategy  # noqa: E402
from random_walk import RandomWalkStrategy  # noqa: E402
from repeated_astar import RepeatedAStarStrategy  # noqa: E402
from wall_follower import LeftWallFollower, RightWallFollower  # noqa: E402

EXTERNAL = sorted((ROOT / "mazes").glob("external_*.json"))


def run(maze: Maze, strategy) -> dict:
    """按 src/README.md 的调用示例运行一次，返回环境统计。"""
    env = MazeEnvironment(maze)
    strategy.reset(width=maze.width, height=maze.height, start=maze.start,
                   goals=frozenset(maze.goals), initial_heading=maze.start_heading, seed=0)
    observation = env.reset()
    while env.status == "running":
        direction = strategy.choose_direction(observation)
        if direction is None:
            env.finish("no_path")
            break
        observation = env.step(direction).observation
    return env.summary()


def small_maze(**changes) -> Maze:
    """3×3 小地图，默认无内部墙、目标在右上角。"""
    data = {"maze_id": "t", "width": 3, "height": 3, "start": [0, 0],
            "start_heading": "N", "goals": [[2, 2]], "blocked_edges": [], "metadata": {}}
    data.update(changes)
    return Maze(data)


class StrategyTests(unittest.TestCase):
    STRATEGIES = (DfsStrategy, GreedyDfsStrategy, FloodFillStrategy, RepeatedAStarStrategy)

    def test_reach_goal_on_external_mazes(self):
        """两种策略在三张比赛迷宫上都能在预算内到达目标，路径为逐格真实移动。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            for cls in self.STRATEGIES:
                with self.subTest(maze=path.stem, strategy=cls.name):
                    summary = run(maze, cls())
                    self.assertEqual(summary["status"], "success")
                    self.assertEqual(len(summary["path"]), summary["steps"] + 1)
                    self.assertIn(summary["path"][-1], maze.goals)

    def test_dfs_moves_at_most_twice_per_cell(self):
        """DFS 每格最多进出各一次，因此步数不超过 2 × 格子数。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            self.assertLessEqual(run(maze, DfsStrategy())["steps"], 2 * maze.width * maze.height)

    def test_flood_fill_goes_straight_on_open_map(self):
        """没有内部墙时 Flood-Fill 走最短路，并优先保持朝向（只转一次弯）。"""
        summary = run(small_maze(), FloodFillStrategy())
        self.assertEqual((summary["steps"], summary["turns_90"]), (4, 1))
        self.assertEqual(summary["repeat_visits"], 0)

    def test_enclosed_goal_reports_no_path(self):
        """目标被墙围住时，两种策略都在探索完可达区域后返回 None。"""
        maze = small_maze(blocked_edges=[[[1, 2], [2, 2]], [[2, 1], [2, 2]]])
        for cls in self.STRATEGIES:
            with self.subTest(strategy=cls.name):
                self.assertEqual(run(maze, cls())["status"], "no_path")

    def test_deterministic_and_reusable_after_reset(self):
        """同一对象 reset 后再次运行，结果完全相同。"""
        maze = Maze.from_json(EXTERNAL[0])
        for cls in self.STRATEGIES:
            strategy = cls()
            self.assertEqual(run(maze, strategy), run(maze, strategy))

    def test_debug_view_format(self):
        """debug_view 返回可视化工具约定的键，且坐标在地图内。"""
        maze = Maze.from_json(EXTERNAL[0])
        for cls in self.STRATEGIES:
            strategy = cls()
            run(maze, strategy)
            view = strategy.debug_view()
            self.assertTrue(set(view) <= {"known_walls", "cell_text", "cell_color", "plan"})
            for x, y, _ in view["cell_text"]:
                self.assertTrue(0 <= x < maze.width and 0 <= y < maze.height)


class WallFollowerTests(unittest.TestCase):
    def test_reaches_goal_on_wall_connected_path(self):
        """目标与外墙相连时，左手法沿外墙走到目标。"""
        summary = run(small_maze(), LeftWallFollower())
        self.assertEqual((summary["status"], summary["steps"]), ("success", 4))

    def test_detects_loop_when_goal_is_an_island(self):
        """中央目标不与外墙相连：左右手法都绕外圈一周后判定循环，返回 no_path。"""
        maze = small_maze(goals=[[1, 1]])
        for cls in (LeftWallFollower, RightWallFollower):
            with self.subTest(strategy=cls.name):
                strategy = cls()
                summary = run(maze, strategy)
                self.assertEqual(summary["status"], "no_path")
                self.assertTrue(strategy.loop_detected)
                self.assertNotIn((1, 1), summary["path"])

    def test_always_terminates_on_external_mazes(self):
        """比赛迷宫上必定在 4 × 格子数次决策内结束（到达目标或判定循环）。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            for cls in (LeftWallFollower, RightWallFollower):
                with self.subTest(maze=path.stem, strategy=cls.name):
                    summary = run(maze, cls())
                    self.assertIn(summary["status"], {"success", "no_path"})
                    self.assertLessEqual(summary["steps"], 4 * maze.width * maze.height)


class BfsPlannerTests(unittest.TestCase):
    def test_shortest_path_and_runner(self):
        """BFS 给出最短路；驱动逐格执行后步数等于路径长度，并报告扩展节点数。"""
        result = run_episode(small_maze(), BfsPlanner())
        self.assertEqual((result["status"], result["steps"], result["mode"]),
                         ("success", 4, "known_map"))
        self.assertGreater(result["expanded_nodes"], 0)

    def test_no_explorer_beats_the_known_map_shortest_path(self):
        """在比赛迷宫上，任何探索算法的步数都不少于 BFS 最短路（BFS 是全知最优参照）。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            shortest = run_episode(maze, BfsPlanner())["steps"]
            for cls in (DfsStrategy, FloodFillStrategy):
                with self.subTest(maze=path.stem, strategy=cls.name):
                    self.assertGreaterEqual(run(maze, cls())["steps"], shortest)

    def test_unreachable_goal(self):
        """目标被墙封闭时规划返回 None，运行记为 no_path。"""
        maze = small_maze(blocked_edges=[[[1, 2], [2, 2]], [[2, 1], [2, 2]]])
        self.assertIsNone(BfsPlanner().plan(maze))
        self.assertEqual(run_episode(maze, BfsPlanner())["status"], "no_path")


class RandomWalkTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self):
        """同一种子结果完全相同，不同种子路线不同；seed 为 None 时等同于 0。"""
        maze = Maze.from_json(EXTERNAL[0])
        first = run_episode(maze, RandomWalkStrategy(), seed=7, max_steps=300)
        again = run_episode(maze, RandomWalkStrategy(), seed=7, max_steps=300)
        self.assertEqual(first["path"], again["path"])  # 计算耗时每次不同，只比较路线
        other = run_episode(maze, RandomWalkStrategy(), seed=8, max_steps=300)
        self.assertNotEqual(first["path"], other["path"])
        self.assertEqual(run_episode(maze, RandomWalkStrategy(), seed=None, max_steps=50)["path"],
                         run_episode(maze, RandomWalkStrategy(), seed=0, max_steps=50)["path"])

    def test_small_maze_and_budget(self):
        """小地图上能随机走到目标；比赛迷宫上通常耗尽预算，记为 budget_exceeded。"""
        self.assertEqual(run_episode(small_maze(), RandomWalkStrategy(), seed=1)["status"], "success")
        result = run_episode(Maze.from_json(EXTERNAL[0]), RandomWalkStrategy(), seed=1, max_steps=200)
        self.assertEqual((result["status"], result["steps"]), ("budget_exceeded", 200))


class GreedyDfsTests(unittest.TestCase):
    def test_only_the_order_differs_from_dfs(self):
        """贪心 DFS 与 DFS 只在邻格顺序上不同：开阔小地图上直奔目标，比赛迷宫上路线不同。"""
        self.assertEqual(run(small_maze(), GreedyDfsStrategy())["steps"], 4)
        maze = Maze.from_json(EXTERNAL[0])
        self.assertNotEqual(run(maze, GreedyDfsStrategy())["path"], run(maze, DfsStrategy())["path"])


class RepeatedAStarTests(unittest.TestCase):
    def test_replans_only_when_needed(self):
        """只在计划被新墙挡住时重新规划：规划次数明显少于移动步数。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            strategy = RepeatedAStarStrategy()
            summary = run(maze, strategy)
            with self.subTest(maze=path.stem):
                self.assertEqual(summary["status"], "success")
                self.assertLess(strategy.replans, summary["steps"])
                self.assertGreater(strategy.expanded_total, 0)


class AStarPlannerTests(unittest.TestCase):
    def test_same_length_as_bfs_with_fewer_expansions(self):
        """每步代价为 1 时 A* 与 BFS 最短路长度相同；启发式使扩展节点数不多于 BFS。"""
        for path in EXTERNAL:
            maze = Maze.from_json(path)
            astar, bfs = run_episode(maze, AStarPlanner()), run_episode(maze, BfsPlanner())
            with self.subTest(maze=path.stem):
                self.assertEqual(astar["status"], "success")
                self.assertEqual(astar["steps"], bfs["steps"])
                self.assertLessEqual(astar["expanded_nodes"], bfs["expanded_nodes"])

    def test_unreachable_goal(self):
        """目标被墙封闭时返回 None，运行记为 no_path。"""
        maze = small_maze(blocked_edges=[[[1, 2], [2, 2]], [[2, 1], [2, 2]]])
        self.assertIsNone(AStarPlanner().plan(maze))
        self.assertEqual(run_episode(maze, AStarPlanner())["status"], "no_path")


if __name__ == "__main__":
    unittest.main()
