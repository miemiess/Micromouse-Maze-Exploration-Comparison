"""用临时小地图分别检查环境的基本规则。"""

import sys
import unittest
from pathlib import Path

# 把项目的 src 目录加入搜索路径，以便导入环境模块。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from environment import Direction as D, Maze, MazeEnvironment


def maze(**changes):
    """生成测试用地图；参数可覆盖起点、目标或墙壁等默认设置。"""
    data = {"maze_id": "test", "width": 3, "height": 2, "start": [0, 0],
            "start_heading": "N", "goals": [[2, 1]],
            "blocked_edges": [[[1, 0], [1, 1]]], "metadata": {}}
    data.update(changes)
    return Maze(data)


class EnvironmentTests(unittest.TestCase):
    def test_walls_are_symmetric_and_illegal_move_ends_run(self):
        """同一面墙在相邻两格都可见，尝试穿墙会终止运行。"""
        env = MazeEnvironment(maze())
        self.assertEqual(env.observe().walls, frozenset({D.SOUTH, D.WEST}))
        env.step(D.EAST)
        self.assertIn(D.NORTH, env.observe().walls)
        result = env.step(D.NORTH)
        self.assertEqual((result.status, result.moved, env.steps), ("invalid_action", False, 1))
        self.assertEqual(env.turns_90, 1)
        env = MazeEnvironment(maze(start=[1, 1]))
        self.assertIn(D.SOUTH, env.observe().walls)

    def test_revisits_turns_and_reset(self):
        """验证回到旧格子、掉头计数和重置后的初始状态。"""
        env = MazeEnvironment(maze())
        env.step(D.EAST)
        env.step(D.WEST)
        self.assertEqual((env.steps, env.repeat_visits, env.turns_90), (2, 1, 3))
        self.assertEqual(len(env.path), env.steps + 1)
        env.reset()
        self.assertEqual((env.steps, env.repeat_visits, env.turns_90), (0, 0, 0))

    def test_goal_wins_over_budget_and_start_goal(self):
        """最后一步到达目标时优先成功；起点是目标也立即成功。"""
        env = MazeEnvironment(maze(goals=[[1, 0]]), max_steps=1)
        self.assertEqual(env.step(D.EAST).status, "success")
        env = MazeEnvironment(maze(), max_steps=1)
        self.assertEqual(env.step(D.EAST).status, "budget_exceeded")
        self.assertEqual(MazeEnvironment(maze(goals=[[0, 0]])).status, "success")

    def test_invalid_map_and_action(self):
        """重复墙、非相邻墙和不符合方向类型的动作应被拒绝。"""
        with self.assertRaises(ValueError):
            maze(blocked_edges=[[[0, 0], [1, 0]], [[1, 0], [0, 0]]])
        with self.assertRaises(ValueError):
            maze(blocked_edges=[[[0, 0], [2, 0]]])
        env = MazeEnvironment(maze())
        self.assertEqual(env.step("E").status, "invalid_action")
        self.assertEqual(env.path, [(0, 0)])

    def test_external_finish(self):
        """外部执行器可以结束运行，结束后不能继续移动。"""
        env = MazeEnvironment(maze())
        env.finish("no_path")
        self.assertEqual(env.summary()["status"], "no_path")
        with self.assertRaises(RuntimeError):
            env.step(D.EAST)


if __name__ == "__main__":
    unittest.main()
