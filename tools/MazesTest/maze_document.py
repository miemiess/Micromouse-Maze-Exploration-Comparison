"""可编辑的迷宫模型与地图库（不依赖界面库）：新建、改墙、设置起点与目标、随机生成，
读写项目 JSON，以及地图库的导入验证与保存。

保存的文件严格符合 src/README.md 的迷宫 JSON 格式，并由 environment.Maze 验证，
存入地图库（默认项目的 mazes/classic/ 目录）后即可供上位机和实验使用。
随机生成的地图会在 metadata 中记录生成器和种子。

外部迷宫只读：文件名以 external_ 开头的地图（A3 整理的比赛迷宫）永远不会被覆盖，
修改后保存会自动另存为新地图，并在 metadata 中记录改自哪张地图。
"""

import json
import random
from collections import deque
from pathlib import Path

from simulation import DELTAS, Direction, Maze, maze_walls

Cell = tuple[int, int]
Edge = frozenset

# 外部比赛迷宫的文件名前缀（见 mazes/README.md），这类文件只读。
PROTECTED_PREFIX = "external_"


def is_protected_file(path: str | Path | None) -> bool:
    """文件是否为只读的外部迷宫：文件名以 external_ 开头且文件已存在。"""
    return path is not None and Path(path).name.startswith(PROTECTED_PREFIX) and Path(path).exists()


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

    @property
    def read_only(self) -> bool:
        """当前对应的文件是否为只读的外部迷宫（可以编辑，但保存时会另存为新地图）。"""
        return is_protected_file(self.path)

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

    def export(self, path: str | Path, *, compact: bool = False) -> Path:
        """验证后写出一份 JSON 副本；不改变本文档对应的文件和"未保存"状态。

        Args:
            path: 目标文件。
            compact: 为 True 时写成单行紧凑 JSON（批量生成用，体积约为缩进格式的 1/6）。

        Raises:
            ValueError: 地图不合法时不写文件。
        """
        self.to_maze()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = (json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":")) if compact
                else json.dumps(self.to_dict(), ensure_ascii=False, indent=2))
        path.write_text(text + "\n", encoding="utf-8")
        return path

    def save(self, path: str | Path, *, compact: bool = False) -> Path:
        """验证后保存为 JSON，并把本文档对应的文件更新为 path。

        Raises:
            ValueError: 地图不合法时不写文件。
        """
        path = self.export(path, compact=compact)
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
    """地图库：一个专门存放迷宫 JSON 的文件夹（上位机默认使用项目的 mazes/classic/）。

    - 导入：先完整验证外部文件，合法后以规范格式保存为 <maze_id>.json；
    - 保存：一律写到 <maze_id>.json。地图 ID 未改时原地覆盖；改了 ID 相当于另存为新文件；
      从库外打开的文件另存一份到库中，不修改原文件；
    - 只读保护：修改外部迷宫（external_*.json）后保存，或目标是已存在的外部迷宫时，绝不覆盖，
      自动改名另存（见 derive_id）；
    - 其他重名情况抛出 FileExistsError，由调用方决定是否覆盖。
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

    def derive_id(self, maze_id: str) -> str:
        """为改自外部迷宫的地图生成不冲突的新 ID。

        去掉 external_ 前缀（新地图不再是外部原始数据，也就不再只读），加 _edit 后缀；
        已存在时依次尝试 _edit2、_edit3……
        例如 external_uk2011f → uk2011f_edit。
        """
        base = maze_id.removeprefix(PROTECTED_PREFIX) + "_edit"
        candidate, number = base, 1
        while self.path_for(candidate).exists():
            number += 1
            candidate = f"{base}{number}"
        return candidate

    def save(self, doc: MazeDocument, *, overwrite: bool = False) -> Path:
        """把地图保存进库中，返回写入的文件。

        doc 本身来自外部迷宫文件，或目标是已存在的外部迷宫时，不会覆盖：doc 会改用
        derive_id 生成的新 ID，metadata 记录 derived_from（原地图 ID），然后保存为新文件。
        调用方可比较保存前后的 doc.maze_id 得知是否发生了另存。

        Raises:
            FileExistsError: 目标文件已存在、不是本地图自己的文件，且 overwrite 为 False。
            ValueError: 地图不合法。
        """
        target = self.path_for(doc.maze_id)
        if doc.read_only or is_protected_file(target):
            original = doc.maze_id
            doc.maze_id = self.derive_id(original)
            doc.metadata = {**doc.metadata, "derived_from": original,
                            "notes": f"基于外部迷宫 {original} 修改；原文件只读，自动另存"}
            target = self.path_for(doc.maze_id)
        same_file = doc.path is not None and Path(doc.path).resolve() == target.resolve()
        if target.exists() and not same_file and not overwrite:
            raise FileExistsError(str(target))
        return doc.save(target)

    def save_generated(self, doc: MazeDocument) -> Path | None:
        """把批量生成的地图存入地图库；同名文件已存在时跳过并返回 None（不覆盖）。"""
        target = self.path_for(doc.maze_id)
        if target.exists():
            return None
        return doc.save(target, compact=True)

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


def _neighbours(doc: "MazeDocument", cell: Cell) -> list[Cell]:
    """网格中与 cell 相邻、且在地图内的格子（不考虑墙）。"""
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in DELTAS.values() if doc.inside((x + dx, y + dy))]


def _carve(doc: "MazeDocument", a: Cell, b: Cell) -> None:
    """拆掉 a、b 之间的墙。"""
    doc.walls.discard(frozenset((a, b)))


def _carve_backtracker(doc: "MazeDocument", rng: random.Random) -> None:
    """递归回溯（随机深度优先）：从起点出发，随机走向未访问邻格，走不通就回退。

    特点：长走廊、分支较少，是有偏的生成方式。
    """
    visited, stack = {doc.start}, [doc.start]
    while stack:
        options = [n for n in _neighbours(doc, stack[-1]) if n not in visited]
        if not options:
            stack.pop()
            continue
        nxt = rng.choice(options)
        _carve(doc, stack[-1], nxt)
        visited.add(nxt)
        stack.append(nxt)


def _carve_wilson(doc: "MazeDocument", rng: random.Random) -> None:
    """Wilson 算法：用"擦除回路的随机游走"逐步把格子接入生成树。

    特点：在所有生成树中均匀随机抽取（无偏），没有特定的结构偏好。
    """
    cells = [(x, y) for x in range(doc.width) for y in range(doc.height)]
    in_tree = {rng.choice(cells)}
    rng.shuffle(cells)
    for origin in cells:
        if origin in in_tree:
            continue
        step: dict[Cell, Cell] = {}
        cur = origin
        while cur not in in_tree:  # 随机游走，重复经过的格子会覆盖去向，相当于擦除回路
            step[cur] = rng.choice(_neighbours(doc, cur))
            cur = step[cur]
        cur = origin
        while cur not in in_tree:
            in_tree.add(cur)
            _carve(doc, cur, step[cur])
            cur = step[cur]


def _carve_prim(doc: "MazeDocument", rng: random.Random) -> None:
    """随机 Prim 算法：维护"已连通区域"的边界墙，每次随机拆一面通向新格子的墙。

    特点：从起点向外扩散，分支多、短死胡同多。
    """
    in_maze = {doc.start}
    frontier = [(doc.start, n) for n in _neighbours(doc, doc.start)]
    while frontier:
        a, b = frontier.pop(rng.randrange(len(frontier)))
        if b in in_maze:
            continue
        _carve(doc, a, b)
        in_maze.add(b)
        frontier.extend((b, n) for n in _neighbours(doc, b) if n not in in_maze)


def _carve_kruskal(doc: "MazeDocument", rng: random.Random) -> None:
    """随机 Kruskal 算法：所有墙随机排序，两侧尚未连通就拆掉（并查集判断）。

    特点：各处同时生长，短死胡同分布较均匀。
    """
    parent = {(x, y): (x, y) for x in range(doc.width) for y in range(doc.height)}

    def find(cell: Cell) -> Cell:
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]]
            cell = parent[cell]
        return cell

    edges = sorted(all_edges(doc.width, doc.height), key=lambda e: sorted(e))
    rng.shuffle(edges)
    for edge in edges:
        a, b = tuple(edge)
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            _carve(doc, a, b)


# 可用的生成算法：键 → (显示名称, 实现, 特点说明)。都生成"完美迷宫"（无环、全连通）。
GENERATORS = {
    "backtracker": ("递归回溯", _carve_backtracker, "长走廊、分支少（有偏）"),
    "wilson": ("Wilson", _carve_wilson, "均匀随机生成树（无偏）"),
    "prim": ("随机 Prim", _carve_prim, "分支多、短死胡同多"),
    "kruskal": ("随机 Kruskal", _carve_kruskal, "短死胡同分布均匀"),
}


def generate(width: int, height: int, *, seed: int, loop_fraction: float = 0.0,
             maze_id: str | None = None, algorithm: str = "backtracker") -> MazeDocument:
    """随机生成迷宫：先用指定算法生成完美迷宫，再随机拆墙制造环路。

    生成的迷宫所有格子互相连通，因此目标一定可达；loop_fraction 为 0 时没有环路（完美迷宫），
    增大后出现多条路线，适合比较算法在环路下的表现。中央目标区内部的墙会被拆掉，
    与比赛迷宫一致。同一组参数和种子总是生成同一张图。
    不同生成算法有不同的结构偏好（见 GENERATORS），只用一种生成器得到的实验结论可能有偏差。

    Args:
        width、height: 尺寸，至少 2 × 2。
        seed: 随机种子，记录在 metadata 中以便复现。
        loop_fraction: 生成后再拆掉剩余内部墙的比例（0~1）。
        maze_id: 地图标识；默认递归回溯为 gen_<宽>x<高>_s<种子>[_l<比例>]，
            其他算法为 gen_<算法>_<宽>x<高>_s<种子>[_l<比例>]。
        algorithm: 生成算法，GENERATORS 的键之一。

    Returns:
        新的 MazeDocument（未保存）。

    Raises:
        ValueError: 未知的生成算法。
    """
    if algorithm not in GENERATORS:
        raise ValueError(f"unknown generator {algorithm!r}; available: {', '.join(GENERATORS)}")
    rng = random.Random(seed)
    if maze_id is None:
        prefix = "gen" if algorithm == "backtracker" else f"gen_{algorithm}"
        maze_id = f"{prefix}_{width}x{height}_s{seed}" +             (f"_l{round(loop_fraction * 100)}" if loop_fraction else "")
    doc = MazeDocument(maze_id, width, height)
    doc.walls = set(all_edges(width, height))
    GENERATORS[algorithm][1](doc, rng)

    for a in doc.goals:
        for b in doc.goals:
            doc.walls.discard(frozenset((a, b)))
    if loop_fraction > 0:
        remaining = sorted(doc.walls, key=lambda w: sorted(w))
        for wall in rng.sample(remaining, round(len(remaining) * min(loop_fraction, 1.0))):
            doc.walls.discard(wall)

    generator = "recursive_backtracker" if algorithm == "backtracker" else algorithm
    doc.metadata = {"source": "generated", "generator": generator,
                    "seed": seed, "loop_fraction": loop_fraction,
                    "notes": "由 tools/MazesTest/maze_document.py 随机生成"}
    doc.dirty, doc.revision = True, 1
    return doc
