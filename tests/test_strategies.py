"""DFS 与 Flood-Fill 策略的验证：只依赖观测、能到达目标、无路时正确停止、结果可复现。"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dfs import DfsStrategy  # noqa: E402
from environment import Maze, MazeEnvironment  # noqa: E402
from flood_fill import FloodFillStrategy  # noqa: E402

EXTERNAL = sorted((ROOT / "tools" / "MazesTest" / "MAP").glob("external_*.json"))


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
    STRATEGIES = (DfsStrategy, FloodFillStrategy)

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


if __name__ == "__main__":
    unittest.main()
