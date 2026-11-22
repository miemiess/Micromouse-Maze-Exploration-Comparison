"""核对增量距离修复、前沿路径的信息边界及无路终止。"""

import sys
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Maze, MazeEnvironment, step_cell
from ext.algorithms.dstar_lite import DStarLiteStrategy
from ext.algorithms.frontier import FrontierStrategy


class ExplorerTests(unittest.TestCase):
    def test_dstar_each_move_matches_fresh_optimistic_bfs(self):
        maze = Maze.from_json(ROOT / "mazes/classic/external_1stworld.json")
        env = MazeEnvironment(maze)
        strategy = DStarLiteStrategy()
        strategy.reset(width=maze.width, height=maze.height, start=maze.start,
                       goals=maze.goals, initial_heading=maze.start_heading)
        for _ in range(20 * maze.width * maze.height):
            obs = env.observe()
            if obs.position in maze.goals:
                break
            direction = strategy.choose_direction(obs)
            distance = dict.fromkeys(maze.goals, 0)
            queue = deque(maze.goals)
            while queue:
                cell = queue.popleft()
                for _, neighbour in strategy.walls.open_moves(cell):
                    if neighbour not in distance:
                        distance[neighbour] = distance[cell] + 1
                        queue.append(neighbour)
            self.assertEqual(distance[obs.position] - 1, distance[step_cell(obs.position, direction)])
            env.step(direction)
        self.assertIn(env.observe().position, maze.goals)
        self.assertGreater(strategy.repairs, 1)

    def test_unreachable_goal_and_confirmed_frontier_routes(self):
        maze = Maze({"maze_id": "isolated_goal", "width": 3, "height": 2,
                     "start": [0, 0], "goals": [[2, 1]], "start_heading": "N",
                     "blocked_edges": [[[2, 0], [2, 1]], [[1, 1], [2, 1]]]})
        for explorer in (FrontierStrategy(), DStarLiteStrategy()):
            env = MazeEnvironment(maze)
            explorer.reset(width=3, height=2, start=maze.start, goals=maze.goals, initial_heading=maze.start_heading)
            visited = set()
            for _ in range(30):
                obs = env.observe()
                visited.add(obs.position)
                direction = explorer.choose_direction(obs)
                if direction is None:
                    break
                if isinstance(explorer, FrontierStrategy):
                    route = list(explorer.route)
                    self.assertTrue(all(cell in visited for cell in route[:-1]))
                    self.assertNotIn(route[-1], visited)
                self.assertNotIn(direction, obs.walls)
                env.step(direction)
            else:
                self.fail("未能在有限步内判定目标不可达")
