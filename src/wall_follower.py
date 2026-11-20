"""沿墙法（左手 / 右手）：始终让一只"手"贴着墙走，是最简单的局部探索策略。

信息假设：只使用每步的当前格四向墙壁观测和自身朝向，不记忆地图。
决策规则（左手法；右手法左右对调）：
    按"左转 → 直行 → 右转 → 掉头"的顺序，选第一个没有墙的方向。
循环终止：策略是确定性的，下一步只取决于（位置, 朝向）。同一个（位置, 朝向）第二次
    出现时，之后的路线一定会无限重复，因此立即返回 None，并设 loop_detected = True（运行状态记为 loop_detected）。
    最多经过 4 × 格子数 次决策就会到达目标或判定循环。
已知局限：目标被环路包围、不与外墙相连时（比赛迷宫的中央目标正是这样设计的）
    沿墙法会一直绕外圈，永远到不了目标，这里作为反面基线保留这种失败。
复杂度：每步决策 O(1)；循环检测额外占用 O(格子数 × 4) 内存。
随机性：无，seed 参数被忽略。
"""

from algorithm_api import (OPPOSITE, Cell, Direction, Observation, inside, step_cell,
                           turn_left, turn_right)


class _WallFollower:
    """左手法和右手法的共同实现；由子类设定 name 和 hand。"""

    name = ""
    hand = "left"

    def reset(self, *, width: int, height: int, start: Cell, goals: frozenset[Cell],
              initial_heading: Direction, seed: int | None = None) -> None:
        """清空循环检测和显示用的记录，参数含义见 src/README.md 的 Strategy 接口。"""
        self._size = (width, height)
        self._states: set[tuple[Cell, Direction]] = set()
        self._visits: dict[Cell, int] = {}
        self._walls: set[frozenset[Cell]] = set()
        self.loop_detected = False

    def _preference(self, heading: Direction) -> list[Direction]:
        """按贴墙的手决定尝试顺序：贴墙一侧 → 直行 → 另一侧 → 掉头。"""
        if self.hand == "left":
            return [turn_left(heading), heading, turn_right(heading), OPPOSITE[heading]]
        return [turn_right(heading), heading, turn_left(heading), OPPOSITE[heading]]

    def choose_direction(self, observation: Observation) -> Direction | None:
        """返回贴墙方向；陷入循环或四面都是墙时返回 None。"""
        here, heading = observation.position, observation.heading
        state = (here, heading)
        if state in self._states:
            self.loop_detected = True
            return None
        self._states.add(state)
        self._visits[here] = self._visits.get(here, 0) + 1
        for direction in observation.walls:
            neighbour = step_cell(here, direction)
            if inside(neighbour, *self._size):
                self._walls.add(frozenset((here, neighbour)))

        for direction in self._preference(heading):
            if direction not in observation.walls:
                return direction
        return None

    def debug_view(self) -> dict:
        """供可视化工具显示：每格经过次数和已观测的墙；判定循环后把经过的格子标红。"""
        view = {
            "known_walls": [sorted(map(list, wall)) for wall in self._walls],
            "cell_text": [[x, y, str(n)] for (x, y), n in self._visits.items()],
        }
        if self.loop_detected:
            view["cell_color"] = [[x, y, "#ffadad"] for x, y in self._visits]
        return view


class LeftWallFollower(_WallFollower):
    """左手沿墙法：左手始终贴墙。"""

    name = "wall_follower_left"
    hand = "left"


class RightWallFollower(_WallFollower):
    """右手沿墙法：右手始终贴墙。"""

    name = "wall_follower_right"
    hand = "right"
