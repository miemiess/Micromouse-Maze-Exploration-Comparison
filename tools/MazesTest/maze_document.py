"""可编辑的迷宫模型与地图库（不依赖界面库）：新建、改墙、设置起点与目标、随机生成，
读写项目 JSON，以及地图库的导入验证与保存。

保存的文件严格符合 src/README.md 的迷宫 JSON 格式，并由 environment.Maze 验证，
存入地图库 MAP 后即可供上位机和实验使用。随机生成的地图会在 metadata 中记录生成器和种子。
"""

import json
import random
from collections import deque
from pathlib import Path

from simulation import DELTAS, Direction, Maze, maze_walls

Cell = tuple[int, int]
Edge = frozenset


def default_goals(width: int, height: int) -> set[Cell]:
    """返回地图中央的目标格：边长为偶数时取中间两格，为奇数时取正中一格。"""
    xs = [width // 2 - 1, width // 2] if width % 2 == 0 else [width // 2]
    ys = [height // 2 - 1, height // 2] if height % 2 == 0 else [height // 2]
    return {(x, y) for x in xs for y in ys}


class MazeDocument:
    """一张正在编辑的迷宫。

    Attributes:
        maze_id: 地图唯一标识。
        width、height: 网格尺寸。
        start、start_heading: 起点和初始朝向。
        goals: 目标格集合。
        walls: 内部墙集合，每面墙是两个相邻格组成的 frozenset。
        metadata: 来源、种子等说明。
        path: 对应的文件路径；新建且未保存时为 None。
        dirty: 自上次保存或读取后是否被修改过。
        revision: 每次修改加一，界面据此判断是否需要刷新。
    """

    def __init__(self, maze_id: str, width: int, height: int):
        """新建一张没有内部墙的空地图，起点 (0, 0) 朝北，目标为中央格。"""
        if width < 2 or height < 2:
            raise ValueError("maze must be at least 2 × 2")
        self.maze_id = maze_id
        self.width, self.height = width, height
        self.start: Cell = (0, 0)
        self.start_heading = Direction.NORTH
        self.goals: set[Cell] = default_goals(width, height)
        self.walls: set[Edge] = set()
        self.metadata: dict = {"source": "handmade", "seed": None, "notes": ""}
        self.path: Path | None = None
        self.dirty = False
        self.revision = 0

    # -- 读写 -------------------------------------------------------------
    @classmethod
    def from_maze(cls, maze: Maze, path: Path | None = None) -> "MazeDocument":
        """从已验证的 Maze 创建可编辑副本。"""
        doc = cls(maze.maze_id, maze.width, maze.height)
        doc.start, doc.start_heading = maze.start, maze.start_heading
        doc.goals = set(maze.goals)
        doc.walls = set(maze_walls(maze))
        doc.metadata = dict(maze.metadata)
        doc.path = Path(path) if path else None
        return doc

    @classmethod
    def load(cls, path: str | Path) -> "MazeDocument":
        """读取并验证迷宫 JSON 文件。

        Raises:
            ValueError: 文件内容不符合迷宫格式。
        """
        return cls.from_maze(Maze.from_json(path), Path(path))

    def to_dict(self) -> dict:
        """转换为项目迷宫 JSON 格式；墙壁按坐标排序，便于在 Git 中比较差异。"""
        edges = sorted(sorted(list(cell) for cell in wall) for wall in self.walls)
        return {"maze_id": self.maze_id, "width": self.width, "height": self.height,
                "start": list(self.start), "start_heading": self.start_heading.value,
                "goals": sorted(list(goal) for goal in self.goals),
                "blocked_edges": edges, "metadata": self.metadata}

    def to_maze(self) -> Maze:
        """验证并转换为环境使用的 Maze。

        Raises:
            ValueError: 地图不合法（例如没有目标、坐标越界）。
        """
        return Maze(self.to_dict())

    def export(self, path: str | Path) -> Path:
        """验证后写出一份 JSON 副本；不改变本文档对应的文件和"未保存"状态。

        Raises:
            ValueError: 地图不合法时不写文件。
        """
        self.to_maze()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        return path

    def save(self, path: str | Path) -> Path:
        """验证后保存为 JSON，并把本文档对应的文件更新为 path。

        Raises:
            ValueError: 地图不合法时不写文件。
        """
        path = self.export(path)
        self.path, self.dirty = path, False
        return path

    # -- 检查 -------------------------------------------------------------
    def inside(self, cell: Cell) -> bool:
        """判断格子是否在地图范围内。"""
        return 0 <= cell[0] < self.width and 0 <= cell[1] < self.height

    def reachable_from_start(self) -> set[Cell]:
        """在真实墙壁下从起点出发能到达的格子。"""
        seen, queue = {self.start}, deque([self.start])
        while queue:
            x, y = queue.popleft()
            for dx, dy in DELTAS.values():
                neighbour = (x + dx, y + dy)
                if (self.inside(neighbour) and neighbour not in seen
                        and frozenset(((x, y), neighbour)) not in self.walls):
                    seen.add(neighbour)
                    queue.append(neighbour)
        return seen

    def check(self) -> tuple[list[str], list[str]]:
        """检查地图。

        Returns:
            (错误, 提醒)。有错误时不能保存或运行；提醒不阻止使用，
            例如目标不可达的地图可用于无路健壮性测试，但应与可达地图分开报告。
        """
        errors, warnings = [], []
        try:
            self.to_maze()
        except ValueError as exc:
            errors.append(str(exc))
            return errors, warnings
        reachable = self.reachable_from_start()
        if not self.goals & reachable:
            warnings.append("no goal is reachable from start")
        unreachable = self.width * self.height - len(reachable)
        if unreachable:
            warnings.append(f"{unreachable} cells are unreachable from start")
        return errors, warnings

    # -- 编辑 -------------------------------------------------------------
    def _changed(self) -> None:
        """记录一次修改。"""
        self.dirty = True
        self.revision += 1

    def has_wall(self, a: Cell, b: Cell) -> bool:
        """两个相邻格之间是否有墙。"""
        return frozenset((a, b)) in self.walls

    def set_wall(self, a: Cell, b: Cell, present: bool) -> None:
        """在两个相邻格之间加墙或拆墙。

        Raises:
            ValueError: 两格不相邻或不在地图内。
        """
        if not (self.inside(a) and self.inside(b)) or abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            raise ValueError("wall must be between two adjacent cells inside the maze")
        wall = frozenset((a, b))
        if present != (wall in self.walls):
            (self.walls.add if present else self.walls.discard)(wall)
            self._changed()

    def toggle_wall(self, a: Cell, b: Cell) -> bool:
        """切换两格之间的墙，返回切换后是否有墙。"""
        present = not self.has_wall(a, b)
        self.set_wall(a, b, present)
        return present

    def set_start(self, cell: Cell, heading: Direction | None = None) -> None:
        """设置起点（和可选的初始朝向）。"""
        if not self.inside(cell):
            raise ValueError("start outside maze")
        heading = heading or self.start_heading
        if (cell, heading) != (self.start, self.start_heading):
            self.start, self.start_heading = cell, heading
            self._changed()

    def toggle_goal(self, cell: Cell) -> bool:
        """把格子加入或移出目标集合，返回切换后是否为目标。"""
        if not self.inside(cell):
            raise ValueError("goal outside maze")
        (self.goals.discard if cell in self.goals else self.goals.add)(cell)
        self._changed()
        return cell in self.goals

    def clear_walls(self) -> None:
        """删除全部内部墙。"""
        if self.walls:
            self.walls.clear()
            self._changed()

    def fill_walls(self) -> None:
        """在所有相邻格之间加墙（通常作为手工挖通道的起点）。"""
        self.walls = set(all_edges(self.width, self.height))
        self._changed()


class MapLibrary:
    """地图库：一个专门存放迷宫 JSON 的文件夹（上位机使用 tools/MazesTest/MAP）。

    - 导入：先完整验证外部文件，合法后以规范格式保存为 <maze_id>.json；
    - 保存：库内地图原地覆盖；从库外打开的文件另存一份到库中，不修改原文件；
    - 重名时抛出 FileExistsError，由调用方决定是否覆盖。
    """

    def __init__(self, folder: str | Path):
        """使用指定文件夹作为地图库，不存在时自动创建。"""
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def maps(self) -> list[Path]:
        """库中所有地图文件，按文件名排序。"""
        return sorted(self.folder.glob("*.json"))

    def contains(self, path: str | Path | None) -> bool:
        """文件是否直接位于地图库文件夹中。"""
        return path is not None and Path(path).resolve().parent == self.folder.resolve()

    def path_for(self, maze_id: str) -> Path:
        """地图在库中的文件路径：<maze_id>.json，文件名中的非法字符替换为下划线。"""
        name = "".join("_" if c in '<>:"/\\|?*' or ord(c) < 32 else c for c in maze_id)
        return self.folder / f"{name.strip() or 'maze'}.json"

    @staticmethod
    def validate_file(path: str | Path) -> tuple[MazeDocument, list[str]]:
        """读取并验证一个迷宫文件，不写入地图库。

        检查内容：JSON 能否解析、字段与类型、坐标范围、墙两端是否相邻、重复墙
        （均由 environment.Maze 验证），以及目标是否可达等提醒。

        Returns:
            (地图, 提醒列表)。提醒不阻止导入，例如目标不可达的地图可用于无路测试。

        Raises:
            ValueError: 文件不是合法的迷宫，消息说明原因。
            OSError: 文件无法读取。
        """
        try:
            doc = MazeDocument.load(path)
        except json.JSONDecodeError as exc:
            raise ValueError(f"不是有效的 JSON（第 {exc.lineno} 行）：{exc.msg}") from exc
        except UnicodeDecodeError as exc:
            raise ValueError("文件不是 UTF-8 编码的文本") from exc
        except ValueError as exc:
            raise ValueError(f"迷宫格式不合法：{exc}") from exc
        errors, warnings = doc.check()
        if errors:
            raise ValueError("迷宫格式不合法：" + "；".join(errors))
        return doc, warnings

    def save(self, doc: MazeDocument, *, overwrite: bool = False) -> Path:
        """把地图保存进库中。

        Raises:
            FileExistsError: 目标文件已存在且不是本地图自己的文件，并且 overwrite 为 False。
            ValueError: 地图不合法。
        """
        target = doc.path if self.contains(doc.path) else self.path_for(doc.maze_id)
        same_file = doc.path is not None and Path(doc.path).resolve() == target.resolve()
        if target.exists() and not same_file and not overwrite:
            raise FileExistsError(str(target))
        return doc.save(target)

    def import_file(self, path: str | Path, *, overwrite: bool = False
                    ) -> tuple[MazeDocument, list[str]]:
        """验证外部文件并复制进库中（validate_file + save）。

        Returns:
            (库中的地图, 提醒列表)。
        """
        doc, warnings = self.validate_file(path)
        doc.path = None  # 视为新地图，按 maze_id 存入库中
        self.save(doc, overwrite=overwrite)
        return doc, warnings


def all_edges(width: int, height: int) -> list[Edge]:
    """列出网格中所有相邻格之间的边。"""
    edges = []
    for x in range(width):
        for y in range(height):
            if x + 1 < width:
                edges.append(frozenset(((x, y), (x + 1, y))))
            if y + 1 < height:
                edges.append(frozenset(((x, y), (x, y + 1))))
    return edges


def generate(width: int, height: int, *, seed: int, loop_fraction: float = 0.0,
             maze_id: str | None = None) -> MazeDocument:
    """用随机深度优先（递归回溯）生成迷宫，可再随机拆墙制造环路。

    生成的迷宫所有格子互相连通，因此目标一定可达；loop_fraction 为 0 时没有环路（完美迷宫），
    增大后出现多条路线，适合比较算法在环路下的表现。中央目标区内部的墙会被拆掉，
    与比赛迷宫一致。同一组参数和种子总是生成同一张图。

    Args:
        width、height: 尺寸，至少 2 × 2。
        seed: 随机种子，记录在 metadata 中以便复现。
        loop_fraction: 生成后再拆掉剩余内部墙的比例（0~1）。
        maze_id: 地图标识，默认 gen_<宽>x<高>_s<种子>[_l<比例>]。

    Returns:
        新的 MazeDocument（未保存）。
    """
    rng = random.Random(seed)
    if maze_id is None:
        maze_id = f"gen_{width}x{height}_s{seed}" + \
            (f"_l{round(loop_fraction * 100)}" if loop_fraction else "")
    doc = MazeDocument(maze_id, width, height)
    doc.walls = set(all_edges(width, height))

    visited, stack = {doc.start}, [doc.start]
    while stack:
        x, y = stack[-1]
        options = [(x + dx, y + dy) for dx, dy in DELTAS.values()
                   if doc.inside((x + dx, y + dy)) and (x + dx, y + dy) not in visited]
        if not options:
            stack.pop()
            continue
        nxt = rng.choice(options)
        doc.walls.discard(frozenset(((x, y), nxt)))
        visited.add(nxt)
        stack.append(nxt)

    for a in doc.goals:
        for b in doc.goals:
            doc.walls.discard(frozenset((a, b)))
    if loop_fraction > 0:
        remaining = sorted(doc.walls, key=lambda w: sorted(w))
        for wall in rng.sample(remaining, round(len(remaining) * min(loop_fraction, 1.0))):
            doc.walls.discard(wall)

    doc.metadata = {"source": "generated", "generator": "recursive_backtracker",
                    "seed": seed, "loop_fraction": loop_fraction,
                    "notes": "由 tools/MazesTest/maze_document.py 随机生成"}
    doc.dirty, doc.revision = True, 1
    return doc
