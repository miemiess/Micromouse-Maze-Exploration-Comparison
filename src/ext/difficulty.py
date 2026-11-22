"""迷宫难度刻画与对抗式生成（D4，可选研究）。

两部分：
1. 难度特征（features）：只看迷宫结构、与算法无关的指标——
       loop_ratio     环路比例 = 独立环路数 / 格子数，独立环路数 = 可走边数 − 格子数 + 连通块数（0 表示没有环路）；
       dead_end_ratio 死胡同比例 = 只有一个出口的格子 / 格子数；
       branch_ratio   分岔比例 = 有 3 个以上出口的格子 / 格子数；
       shortest       起点到目标的最短步数；
       detour         绕路系数 = 最短步数 / 起点到最近目标的曼哈顿距离（“看起来近、实际远”的程度，
                      也是乐观假设被误导的上限来源）；
       shortest_turns 最短路中转弯最少的一条的 90° 转向数（基础规则最优路线的转向）。
   correlate() 读取基础阶段实验 1 的 results/basic/main/runs.csv，计算每个特征与各算法“步数 / 最短路”的
   Spearman 秩相关（只用成功运行）。这是对已公开结果的描述性分析，不检验事先的假设。
2. 对抗式生成（adversarial）：用模拟退火搜索让某个算法“步数 / 最短路”尽量大的迷宫。
       初始迷宫：开发集的生成图（不碰测试集）；
       邻域：翻转一面内部墙（目标区内部不加墙），要求所有格子仍从起点可达；
       目标：目标算法的步数 / 最短路（越大越“难”）；
       接受：更好就接受，更差以 exp(Δ / T) 的概率接受，T 按几何级数从 t_start 降到 t_end；
       固定随机种子，可复现。输出最难迷宫（项目 JSON 格式，metadata 记录来源与得分）与各算法在其上的表现。
命令行（项目根目录）：
    python src/ext/difficulty.py features                         → results/ext/difficulty/features.csv、correlations.md
    python src/ext/difficulty.py adversarial --algorithm repeated_astar --iterations 2000 --seed 0
                                                                   → results/ext/difficulty/adversarial_<算法>.json / .md
"""

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from core.algorithm_api import Maze, load_algorithm, open_neighbours, run_episode  # noqa: E402
from core.planning import quarter_turns  # noqa: E402

OUT_DIR = ROOT / "results" / "ext" / "difficulty"
BASIC_RUNS = ROOT / "results" / "basic" / "main" / "runs.csv"
FEATURES = ["loop_ratio", "dead_end_ratio", "branch_ratio", "shortest", "detour", "shortest_turns"]
# 对抗生成的初始迷宫：开发集生成图（种子 101～110），不使用测试集
DEFAULT_SEED_MAZE = ROOT / "mazes" / "classic" / "gen_backtracker_16x16_s101.json"
COMPARE_ALGORITHMS = ["repeated_astar", "flood_fill", "dfs", "greedy_dfs", "wall_follower_left",
                      "turn_aware_astar", "dstar_lite", "frontier"]


# ====================================================================== 难度特征

def distances(maze: Maze, sources) -> dict:
    """从 sources 出发的 BFS 步数（真值地图）。"""
    dist = {tuple(s): 0 for s in sources}
    queue = deque(dist)
    while queue:
        cell = queue.popleft()
        for _, nxt in open_neighbours(maze, cell):
            if nxt not in dist:
                dist[nxt] = dist[cell] + 1
                queue.append(nxt)
    return dist


def features(maze: Maze) -> dict:
    """迷宫的结构难度特征（见模块说明）。目标不可达时 shortest、detour、shortest_turns 为 None。"""
    cells = maze.width * maze.height
    degree = {(x, y): sum(1 for _ in open_neighbours(maze, (x, y)))
              for x in range(maze.width) for y in range(maze.height)}
    open_edges = sum(degree.values()) // 2
    components, seen = 0, set()
    for cell in degree:
        if cell not in seen:
            components += 1
            seen |= set(distances(maze, [cell]))
    reach = distances(maze, [maze.start])
    goal_steps = [reach[g] for g in maze.goals if g in reach]
    shortest = min(goal_steps) if goal_steps else None
    manhattan = min(abs(g[0] - maze.start[0]) + abs(g[1] - maze.start[1]) for g in maze.goals)
    # 转向数取“最短路中转向最少”的一条：步数优先、转向次之
    turns = _min_turns_among_shortest(maze, shortest) if shortest is not None else None
    return {"maze_id": maze.maze_id,
            "loop_ratio": round((open_edges - cells + components) / cells, 4),   # 圈数（独立环路数）
            "dead_end_ratio": round(sum(d == 1 for d in degree.values()) / cells, 4),
            "branch_ratio": round(sum(d >= 3 for d in degree.values()) / cells, 4),
            "shortest": shortest,
            "detour": round(shortest / manhattan, 4) if shortest and manhattan else None,
            "shortest_turns": turns}


def _min_turns_among_shortest(maze: Maze, shortest: int) -> int:
    """最短路（步数 = shortest）中 90° 转向最少的一条的转向数：用极小的转弯代价做朝向 Dijkstra。"""
    from core.planning import heading_search, maze_blocked

    class _TieBreak:
        def run_cost(self, cells):
            return float(cells) * 1000.0

        def turn_cost(self, quarters):
            return float(quarters)

    result = heading_search(maze.start, maze.start_heading, maze.goals,
                            maze_blocked(maze.width, maze.height, maze.walls), _TieBreak())
    route, heading, turns = result.route, maze.start_heading, 0
    for a, b in zip(route, route[1:]):
        move = next(d for d, n in open_neighbours(maze, a) if n == b)
        turns += quarter_turns(heading, move)
        heading = move
    assert len(route) - 1 == shortest
    return turns


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman 秩相关系数（并列取平均秩）；样本少于 3 或某一列为常数时返回 None。"""
    if len(xs) < 3:
        return None

    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        result = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                result[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return result

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if sx == 0 or sy == 0:
        return None
    return round(sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy), 4)


def _display(path) -> str:
    """项目内路径显示为相对路径。"""
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def correlate(runs_csv: Path = BASIC_RUNS, out_dir: Path = OUT_DIR) -> Path:
    """计算基础阶段实验 1 中全部地图的特征，以及特征与各探索算法“步数 / 最短路”的 Spearman 相关。"""
    with Path(runs_csv).open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["experiment_mode"] == "unknown_exploration"]
    maze_ids = sorted({r["maze_id"] for r in rows})
    table = {m: features(Maze.from_json(ROOT / "mazes" / "classic" / f"{m}.json")) for m in maze_ids}
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "features.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["maze_id", *FEATURES])
        writer.writeheader()
        writer.writerows(table[m] for m in maze_ids)

    algorithms = sorted({r["algorithm"] for r in rows})
    lines = ["# 迷宫难度特征与算法表现（D4，描述性分析）", "",
             f"数据：`{_display(runs_csv)}`（基础规则实验 1，{len(maze_ids)} 张地图）。"
             "单元格为特征与该算法“步数 / 最短路”的 Spearman 秩相关（只用成功运行，n 为样本数）；"
             "正值表示特征越大，算法相对最短路走得越多。这是对已公开结果的描述，不是事先假设的检验。", "",
             "| 算法 | n | " + " | ".join(FEATURES) + " |",
             "| --- | --- | " + " | ".join("---" for _ in FEATURES) + " |"]
    for algorithm in algorithms:
        ok = [r for r in rows if r["algorithm"] == algorithm and r["status"] == "success" and r["ratio"]]
        cells = []
        for feature in FEATURES:
            pairs = [(table[r["maze_id"]][feature], float(r["ratio"])) for r in ok
                     if table[r["maze_id"]][feature] is not None]
            rho = spearman([p[0] for p in pairs], [p[1] for p in pairs])
            cells.append("-" if rho is None else f"{rho:+.2f}")
        lines.append(f"| {algorithm} | {len(ok)} | " + " | ".join(cells) + " |")
    summary = {f: statistics.mean(table[m][f] for m in maze_ids if table[m][f] is not None) for f in FEATURES}
    lines += ["", "特征均值：" + "，".join(f"{f} = {v:.3f}" for f, v in summary.items()), "",
              "说明：16×16 地图起点到中央目标的曼哈顿距离相同，detour 与 shortest 成正比，两列相关系数一致；"
              "沿墙法只统计成功运行（n 较小），相关系数有选择偏差。", ""]
    path = out_dir / "correlations.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ====================================================================== 对抗式生成

def _data(maze: Maze) -> dict:
    return {"maze_id": maze.maze_id, "width": maze.width, "height": maze.height,
            "start": list(maze.start), "start_heading": maze.start_heading.value,
            "goals": [list(g) for g in sorted(maze.goals)],
            "blocked_edges": sorted(sorted(map(list, e)) for e in maze.walls),
            "metadata": dict(maze.metadata)}


def _connected(maze: Maze) -> bool:
    return len(distances(maze, [maze.start])) == maze.width * maze.height


def _difficulty(maze: Maze, algorithm: str) -> float:
    """目标算法在 maze 上的“步数 / 最短路”；失败（未到达）时按动作预算记分，鼓励但不偏好失败。"""
    shortest = min(distances(maze, [maze.start]).get(g, math.inf) for g in maze.goals)
    result = run_episode(maze, load_algorithm(algorithm), seed=0)
    steps = result["steps"] if result["status"] == "success" else 20 * maze.width * maze.height
    return steps / shortest


def candidate_edges(maze: Maze) -> list[frozenset]:
    """可以翻转的内部边：不含目标区内部的边（目标区保持连通、无墙）。"""
    edges = []
    for x in range(maze.width):
        for y in range(maze.height):
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if nx < maze.width and ny < maze.height:
                    edge = frozenset(((x, y), (nx, ny)))
                    if not edge <= maze.goals:
                        edges.append(edge)
    return edges


def adversarial(algorithm: str = "repeated_astar", *, seed_maze: Path = DEFAULT_SEED_MAZE,
                iterations: int = 2000, seed: int = 0, t_start: float = 0.5, t_end: float = 0.01,
                out_dir: Path | None = OUT_DIR) -> dict:
    """模拟退火：翻转内部墙使 algorithm 的“步数 / 最短路”尽量大。返回最好结果（含迷宫数据与得分轨迹）。"""
    rng = random.Random(seed)
    current = Maze.from_json(seed_maze)
    edges = candidate_edges(current)
    current_score = start_score = _difficulty(current, algorithm)
    best, best_score = current, current_score
    trace = [round(current_score, 4)]
    for i in range(iterations):
        temperature = t_start * (t_end / t_start) ** (i / max(1, iterations - 1))
        data = _data(current)
        edge = rng.choice(edges)
        walls = {frozenset(map(tuple, e)) for e in data["blocked_edges"]}
        walls ^= {edge}
        data["blocked_edges"] = [sorted(map(list, e)) for e in walls]
        candidate = Maze(data)
        if not _connected(candidate):
            continue
        score = _difficulty(candidate, algorithm)
        if score >= current_score or rng.random() < math.exp((score - current_score) / temperature):
            current, current_score = candidate, score
            if score > best_score:
                best, best_score = candidate, score
        if (i + 1) % max(1, iterations // 20) == 0:
            trace.append(round(best_score, 4))

    data = _data(best)
    data["maze_id"] = f"adversarial_{algorithm}_s{seed}"
    data["metadata"] = {"generator": "simulated_annealing (src/ext/difficulty.py)", "target_algorithm": algorithm,
                        "derived_from": Path(seed_maze).stem, "iterations": iterations, "seed": seed,
                        "t_start": t_start, "t_end": t_end, "start_score": round(start_score, 4),
                        "best_score": round(best_score, 4)}
    final = Maze(data)
    comparison = {}
    for name in COMPARE_ALGORITHMS:
        for maze, label in ((Maze.from_json(seed_maze), "seed"), (final, "adversarial")):
            comparison.setdefault(name, {})[label] = round(_difficulty(maze, name), 4)
    result = {"maze": data, "start_score": start_score, "best_score": best_score, "trace": trace,
              "comparison": comparison, "features": {"seed": features(Maze.from_json(seed_maze)),
                                                     "adversarial": features(final)}}
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"adversarial_{algorithm}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        lines = [f"# 对抗式迷宫：{algorithm}（D4）", "",
                 f"初始迷宫 `{Path(seed_maze).stem}`（开发集），模拟退火 {iterations} 次（种子 {seed}，"
                 f"T 从 {t_start} 几何降到 {t_end}），目标为 {algorithm} 的“步数 / 最短路”。"
                 f"迷宫文件：`adversarial_{algorithm}.json`（可用上位机打开）。", "",
                 f"得分：{start_score:.3f} → {best_score:.3f}；每 5% 迭代的最好得分：{trace}", "",
                 "| 算法 | 初始迷宫 | 对抗迷宫 |", "| --- | --- | --- |"]
        lines += [f"| {n} | {v['seed']:.3f} | {v['adversarial']:.3f} |" for n, v in comparison.items()]
        lines += ["", "| 特征 | 初始迷宫 | 对抗迷宫 |", "| --- | --- | --- |"]
        lines += [f"| {f} | {result['features']['seed'][f]} | {result['features']['adversarial'][f]} |"
                  for f in FEATURES]
        lines += ["", "说明：对抗迷宫针对目标算法的具体实现（包括同代价时的选路顺序），对其他算法不一定同样困难；"
                  "比较“初始 / 对抗”两列可以看出陷阱利用的是乐观假设本身，还是某个实现细节。"]
        (out_dir / f"adversarial_{algorithm}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("features", help="难度特征与基础结果的相关分析")
    adv = sub.add_parser("adversarial", help="模拟退火生成对抗迷宫")
    adv.add_argument("--algorithm", default="repeated_astar")
    adv.add_argument("--seed-maze", type=Path, default=DEFAULT_SEED_MAZE)
    adv.add_argument("--iterations", type=int, default=2000)
    adv.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    if args.command == "features":
        print(correlate())
    else:
        result = adversarial(args.algorithm, seed_maze=args.seed_maze, iterations=args.iterations, seed=args.seed)
        print(f"{args.algorithm}: {result['start_score']:.3f} -> {result['best_score']:.3f}  "
              f"({OUT_DIR / f'adversarial_{args.algorithm}.json'})")


if __name__ == "__main__":
    main()
