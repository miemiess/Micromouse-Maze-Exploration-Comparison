"""随机游走：每步在没有墙的方向中等概率随机选一个，作为所有探索算法的下界基线。

信息假设：只使用当前格观测，不记忆地图、不记录访问。
决策规则：从当前格无墙的方向中均匀随机选择（允许掉头）；四面都是墙时返回 None（no_path）。
终止：不保证到达目标，通常由移动预算终止（budget_exceeded），用于检验预算和失败记录流程。
随机性：使用 random.Random(seed)；seed 为 None 时固定使用 0，保证结果可复现。
    比较时应使用多个种子重复运行，报告均值与离散程度。
复杂度：每步 O(1)。
"""

import random

from core.algorithm_api import ORDER, Cell, Direction, Observation


class RandomWalkStrategy:
    """等概率随机游走（下界基线）。"""

    name = "random_walk"

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """按种子初始化随机数，并清空显示用的访问计数。"""
        self.seed = 0 if seed is None else seed
        self._rng = random.Random(self.seed)
        self._visits: dict[Cell, int] = {}

    def choose_direction(self, observation: Observation) -> Direction | None:
        """在无墙方向中随机选一个；四面都是墙时返回 None。"""
        here = observation.position
        self._visits[here] = self._visits.get(here, 0) + 1
        options = [d for d in ORDER if d not in observation.walls]
        return self._rng.choice(options) if options else None

    def debug_view(self) -> dict:
        """供可视化工具显示：每格经过次数。"""
        return {"cell_text": [[x, y, str(n)] for (x, y), n in self._visits.items()]}
