"""用仅依赖当前观测的探索过程，验证外部地图与环境的联动。"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 从项目目录导入环境，路径不依赖终端当前所在位置。
sys.path.insert(0, str(ROOT / "src"))
from environment import Direction, Maze, MazeEnvironment

# 每个方向对应的坐标变化；回溯时使用反方向。
MOVES = {
    Direction.NORTH: (0, 1), Direction.EAST: (1, 0),
    Direction.SOUTH: (0, -1), Direction.WEST: (-1, 0),
}
OPPOSITE = {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}
FILES = ("external_1stworld.json", "external_japan2017ef.json", "external_uk2011f.json")


class ExternalMazeIntegrationTests(unittest.TestCase):
    def test_observation_driven_exploration(self):
        """逐张加载外部地图，让电脑鼠依靠观测探索到目标。"""
        for filename in FILES:
            with self.subTest(maze=filename):
                path = ROOT / "mazes" / filename
                raw = json.loads(path.read_text(encoding="utf-8"))
                maze = Maze.from_json(path)
                env = MazeEnvironment(maze)
                observation = env.reset()
                # 仅用于测试预期观测；探索决策本身只使用 observation 和访问记录。
                walls = {frozenset(map(tuple, edge)) for edge in raw["blocked_edges"]}
                # visited 记录探索过的格子，stack 记录前进方向以便回溯。
                visited = {observation.position}
                stack = []
                route = [observation.position]
                turns = repeats = 0
                heading = observation.heading

                while env.status == "running":
                    x, y = observation.position
                    # 从地图文件独立计算墙壁，与环境返回的当前格观测比较。
                    expected_walls = frozenset(
                        direction for direction, (dx, dy) in MOVES.items()
                        if not (0 <= x + dx < maze.width and 0 <= y + dy < maze.height)
                        or frozenset(((x, y), (x + dx, y + dy))) in walls
                    )
                    self.assertEqual(observation.walls, expected_walls)
                    self.assertEqual(observation.step_count, len(route) - 1)
                    self.assertEqual(set(vars(observation)), {"position", "heading", "walls", "step_count"})

                    # 未访问的邻格优先；无路时按原路逐格回溯。
                    direction = next((d for d, (dx, dy) in MOVES.items()
                                      if d not in observation.walls
                                      and (x + dx, y + dy) not in visited), None)
                    if direction is None:
                        self.assertTrue(stack, f"{filename} 无法到达目标")
                        direction = OPPOSITE[stack.pop()]
                    else:
                        stack.append(direction)
                    # 独立累计转弯、重复访问和路径，最后与环境统计对照。
                    order = list(Direction)
                    diff = abs(order.index(direction) - order.index(heading))
                    turns += min(diff, 4 - diff)
                    dx, dy = MOVES[direction]
                    destination = (x + dx, y + dy)
                    repeats += destination in visited
                    visited.add(destination)
                    route.append(destination)
                    heading = direction
                    result = env.step(direction)
                    self.assertTrue(result.moved)
                    self.assertEqual(result.observation.position, destination)
                    self.assertEqual(result.observation.heading, direction)
                    observation = result.observation

                # 检查最终到达目标，且环境统计与逐步记录的结果一致。
                self.assertEqual(env.status, "success")
                self.assertIn(observation.position, maze.goals)
                summary = env.summary()
                self.assertEqual(summary["path"], route)
                self.assertEqual(summary["steps"], len(route) - 1)
                self.assertEqual(summary["turns_90"], turns)
                self.assertEqual(summary["repeat_visits"], repeats)


if __name__ == "__main__":
    unittest.main()
