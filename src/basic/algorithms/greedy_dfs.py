"""贪心 DFS：DFS＋实际回溯的框架完全不变，只把选择未访问邻格的顺序改为"离目标近的优先"。

与 dfs.py 的唯一差别是 _candidates 的排序规则，因此两者的步数之差就是"目标方向启发式"
带来的效果（消融对比）。
信息假设：只使用每步观测；目标坐标在 reset 时给出（Strategy 接口允许）。
决策规则：候选方向按"走过去后的格子到最近目标的曼哈顿距离"从小到大排序，
    距离相同时优先保持当前朝向（少转弯），再按 N/E/S/W；其余规则同 DFS
    （无未访问邻格时沿原路真实回溯，栈空返回 None）。
局限：曼哈顿距离不考虑墙，被墙挡住时启发式会误导，可能比固定顺序更差。
复杂度：每步 O(1)（4 个方向 × 目标数）；移动步数上界与 DFS 相同，不超过 2 × 可达格子数。
随机性：无。
"""

from algorithm_api import ORDER, Cell, Direction, step_cell
from dfs import DfsStrategy


def manhattan_to_goals(cell: Cell, goals) -> int:
    """格子到最近目标的曼哈顿距离（不考虑墙）。"""
    return min(abs(cell[0] - gx) + abs(cell[1] - gy) for gx, gy in goals)


class GreedyDfsStrategy(DfsStrategy):
    """目标方向优先的 DFS＋实际回溯。"""

    name = "greedy_dfs"

    def _candidates(self, here: Cell, heading: Direction) -> tuple[Direction, ...]:
        """按到目标的曼哈顿距离、是否直行、N/E/S/W 依次排序。"""
        return tuple(sorted(ORDER, key=lambda d: (
            manhattan_to_goals(step_cell(here, d), self._goals), d != heading, ORDER.index(d))))
