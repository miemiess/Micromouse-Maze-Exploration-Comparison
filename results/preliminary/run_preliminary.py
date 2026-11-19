"""初步实验：为 Docs/Result.md 第 2 章生成对比数据（不替代 D2 的正式批量实验）。

地图：mazes/classic/ 中 3 张核心比赛迷宫 + 30 张随机生成的 16×16 迷宫
      （环路比例 0%、10%、30% 各 10 张，种子 1～10，生成器见 tools/MazesTest/maze_document.py）。
算法：src/ 中自动发现的全部算法；随机游走的种子等于地图种子（比赛迷宫用 0）。
规则：src/algorithm_api.run_episode，默认预算 20 × 格子数，计时只含算法自身。

用法（项目根目录）：
    python results/preliminary/run_preliminary.py
输出：同目录下 preliminary_runs.csv（每次运行一行）和 summary.md（汇总表）。
"""

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools" / "MazesTest"))

from algorithm_api import KNOWN_MAP, Maze, discover_algorithms, run_episode  # noqa: E402
from maze_document import generate  # noqa: E402

OUT = Path(__file__).resolve().parent
LOOPS = (0.0, 0.1, 0.3)
SEEDS = range(1, 11)


def maze_set():
    """返回 [(地图组, 地图, 种子)]。"""
    core = ("external_1stworld.json", "external_japan2017ef.json", "external_uk2011f.json")
    mazes = [("external", Maze.from_json(ROOT / "mazes" / "classic" / name), 0) for name in core]
    for loop in LOOPS:
        for seed in SEEDS:
            mazes.append((f"gen_loop{int(loop * 100)}", generate(16, 16, seed=seed, loop_fraction=loop).to_maze(), seed))
    return mazes


def main():
    algorithms, errors = discover_algorithms()
    if errors:
        raise SystemExit(errors)
    rows = []
    for group, maze, seed in maze_set():
        shortest = run_episode(maze, algorithms["bfs"].create())["steps"]
        for name, info in algorithms.items():
            result = run_episode(maze, info.create(), seed=seed)
            rows.append({"group": group, "maze_id": maze.maze_id, "algorithm": name, "mode": info.mode,
                         "status": result["status"], "steps": result["steps"],
                         "turns_90": result["turns_90"], "repeat_visits": result["repeat_visits"],
                         "compute_ms": round(result["compute_seconds"] * 1000, 3),
                         "expanded_nodes": result.get("expanded_nodes", ""),
                         "shortest": shortest,
                         "ratio": round(result["steps"] / shortest, 3) if result["status"] == "success" else ""})
    with (OUT / "preliminary_runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    lines = ["| 地图组 | 算法 | 成功率 | 平均步数（成功） | 步数 / 最短路 | 平均转向 | 平均重复访问 | 平均计算 ms | 平均扩展节点 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    groups = ["external"] + [f"gen_loop{int(l * 100)}" for l in LOOPS]
    for group in groups:
        for name in algorithms:
            runs = [r for r in rows if r["group"] == group and r["algorithm"] == name]
            ok = [r for r in runs if r["status"] == "success"]
            mean = lambda key, rs=ok: f"{statistics.mean(r[key] for r in rs):.1f}" if rs else "-"
            exp = [r["expanded_nodes"] for r in runs if r["expanded_nodes"] != ""]
            lines.append(f"| {group} | {name} | {len(ok)}/{len(runs)} | {mean('steps')} | "
                         f"{(f'{statistics.mean(r['ratio'] for r in ok):.2f}' if ok else '-')} | "
                         f"{mean('turns_90')} | {mean('repeat_visits')} | "
                         f"{statistics.mean(r['compute_ms'] for r in runs):.2f} | "
                         f"{(f'{statistics.mean(exp):.0f}' if exp else '-')} |")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
