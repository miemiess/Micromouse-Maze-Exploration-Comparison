"""两阶段比赛（D5，flow 维度）：先探索，再从起点冲刺；成绩 = 冲刺代价 + 探索代价 / explore_divisor。

真实电脑鼠比赛允许先探索迷宫，再从起点冲刺，成绩主要看冲刺，探索用时只按一定比例计入。
本层的模型（“走—停—转”代价沿用当前代价层；没有代价层时代价 = 步数）：
    1. 探索阶段：到达目标不再结束运行。声明 explores_after_goal 的算法可继续探索，返回 None 结束探索；
       其他算法第一次到达目标即结束探索（“到达即停”，作为对照）。动作预算耗尽时，到过目标也视为结束探索；
    2. 返回起点：结束探索后沿已确认可走的边返回起点，代价计入探索代价（return_cost）；
    3. 冲刺：从起点、初始朝向出发，只能走已确认可走的边（被观测确认没有墙、或实际走过的边；
       噪声观测下只算走过的边），走代价最小的路线到目标（sprint_cost）；
    4. 成绩 total_score = sprint_cost + (探索代价 + return_cost) / explore_divisor。
explore_divisor 默认 30：参考经典电脑鼠比赛“成绩 = 冲刺用时 + 探索总用时 / 30”的计分方式（来源待核查），可用参数覆盖。
运行结果另含：explore_cost（含返回）、return_cost、sprint_cost、optimal_sprint_cost（已知完整地图时的最优冲刺代价）、
sprint_ratio（= sprint_cost / optimal_sprint_cost）、total_score；没到过目标时冲刺相关字段为空。
写法：two_phase、two_phase:explore_divisor=10；可与代价层组合，如 turn_cost:weight=2+two_phase。
"""

from dataclasses import dataclass
from typing import ClassVar

from core.planning import heading_search, step
from core.rules import RuleLayer


def confirmed_blocked(width: int, height: int, known_open):
    """只把已确认可走的边当作通路（冲刺与返回起点使用）。"""
    def blocked(cell, direction):
        neighbour = step(cell, direction)
        return not (0 <= neighbour[0] < width and 0 <= neighbour[1] < height) \
            or frozenset((cell, neighbour)) not in known_open
    return blocked


@dataclass(frozen=True)
class TwoPhaseLayer(RuleLayer):
    """先探索、返回起点，再沿已确认的通路冲刺；成绩 = 冲刺 + 探索 / 系数。"""

    key: ClassVar[str] = "two_phase"
    title: ClassVar[str] = "两阶段比赛"
    dimension: ClassVar[str] = "flow"
    color: ClassVar[str] = "#2b8a3e"
    summary: ClassVar[str] = "到达目标后可继续探索；冲刺只能走已确认的通路；成绩 = 冲刺代价 + 探索代价 / 系数"
    param_labels: ClassVar[dict[str, tuple[str, str]]] = {"explore_divisor": ("探索折算系数", "")}
    param_ranges: ClassVar[dict[str, tuple[float, float]]] = {"explore_divisor": (1, 1000)}

    explore_divisor: float = 30.0

    def __post_init__(self):
        if not self.explore_divisor >= 1:
            raise ValueError("explore_divisor must be ≥ 1")

    def env_options(self) -> dict:
        return {"stop_at_goal": False}

    def summarize(self, record) -> dict:
        maze, cost = record.maze, record.rule.cost_model
        empty = {"explore_cost": None, "return_cost": None, "sprint_cost": None,
                 "optimal_sprint_cost": None, "sprint_ratio": None, "total_score": None}
        if record.status != "success":
            return empty
        blocked = confirmed_blocked(maze.width, maze.height, record.known_open)
        back = heading_search(record.position, record.heading, [maze.start], blocked, cost)
        sprint = heading_search(maze.start, maze.start_heading, maze.goals, blocked, cost)
        if not (back.found and sprint.found):
            return empty
        explore = record.explore_cost + back.cost
        optimal = record.rule.optimal_cost(maze)
        return {"explore_cost": round(explore, 6), "return_cost": back.cost, "sprint_cost": sprint.cost,
                "optimal_sprint_cost": optimal,
                "sprint_ratio": round(sprint.cost / optimal, 4) if optimal else None,
                "total_score": round(sprint.cost + explore / self.explore_divisor, 6)}


LAYERS = [TwoPhaseLayer]
