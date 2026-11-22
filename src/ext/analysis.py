"""扩展实验分析（按冻结的 Docs/ext/experiment-plan.md 第 5 节）：配对胜负、符号检验、分组一致性与曲线。

读取 results/ext/turn、noise、two_phase 下各子实验的 runs.csv，输出 results/ext/analysis/report.md 与图表。
结论标准（与计划一致，运行前确定）：
    - 配对：X1、X3 按地图配对，X2 按（地图, 种子）配对；只用两种算法都成功的配对；|差| < 1e-9 记平局；
    - 显著性：胜负次数的双侧符号检验（精确二项检验），p < 0.05 才写“更好 / 更差”，否则“无显著差异”；
    - 分组：外部迷宫库（external_*）与生成图分别报告；全部地图显著、且两组胜负方向一致时才写成总体结论，
      方向不一致时写“取决于地图来源”。
运行：python src/ext/analysis.py
"""

import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "results" / "ext"
OUT = RESULTS / "analysis"
TIE = 1e-9
ALPHA = 0.05


# ====================================================================== 统计

def sign_test(wins: int, losses: int) -> float:
    """双侧精确符号检验的 p 值（平局已剔除）。"""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def source(maze_id: str) -> str:
    return "external" if maze_id.startswith("external_") else "generated"


def paired(rows: list[dict], a: str, b: str, metric: str, lower_is_better: bool = True) -> dict:
    """算法 a 对 b 的配对比较（a 更好记胜）。返回 {组: {wins, losses, ties, n, p, mean_a, mean_b}}。"""
    table = defaultdict(dict)
    for r in rows:
        if r["algorithm"] in (a, b) and r["status"] == "success" and r.get(metric) not in ("", None):
            table[(r["maze_id"], r["seed"])][r["algorithm"]] = float(r[metric])
    out = {}
    for group in ("ALL", "external", "generated"):
        pairs = [(v[a], v[b]) for (m, _), v in table.items()
                 if a in v and b in v and group in ("ALL", source(m))]
        better = sum(1 for x, y in pairs if x < y - TIE)       # a 的数值更小
        worse = sum(1 for x, y in pairs if x > y + TIE)
        wins, losses = (better, worse) if lower_is_better else (worse, better)
        out[group] = {"n": len(pairs), "wins": wins, "losses": losses, "ties": len(pairs) - wins - losses,
                      "p": sign_test(wins, losses),
                      "mean_a": statistics.mean(x for x, _ in pairs) if pairs else None,
                      "mean_b": statistics.mean(y for _, y in pairs) if pairs else None}
    return out


def verdict(result: dict) -> str:
    """按计划第 5 节给出结论文字（a 相对 b）。"""
    overall = result["ALL"]
    if overall["n"] == 0:
        return "无可比配对"
    if overall["p"] >= ALPHA:
        return "无显著差异"
    direction = overall["wins"] > overall["losses"]
    groups = [result[g] for g in ("external", "generated") if result[g]["n"] > 0]
    if any((g["wins"] > g["losses"]) != direction for g in groups if g["wins"] != g["losses"]):
        return "取决于地图来源"
    return "更好" if direction else "更差"


def fmt_pair(result: dict, label: str) -> list[str]:
    """一行配对结果的 Markdown（三组）。"""
    cells = []
    for group in ("ALL", "external", "generated"):
        r = result[group]
        if r["n"] == 0:
            cells.append("-")
            continue
        cells.append(f"{r['wins']}/{r['losses']}/{r['ties']}（p = {r['p']:.3g}）")
    return [f"| {label} | " + " | ".join(cells) + f" | **{verdict(result)}** |"]


PAIR_HEADER = ["| 比较 | 全部：胜/负/平 | 外部迷宫库 | 生成图 | 结论 |", "| --- | --- | --- | --- | --- |"]


# ====================================================================== 读取

def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def experiments(folder: str) -> dict[str, list[dict]]:
    base = RESULTS / folder
    return {d.name: load(d / "runs.csv") for d in sorted(base.iterdir()) if (d / "runs.csv").exists()} \
        if base.exists() else {}


def mean_of(rows, algorithm, metric, *, success_only=True):
    values = [float(r[metric]) for r in rows if r["algorithm"] == algorithm and r.get(metric) not in ("", None)
              and (r["status"] == "success" or not success_only)]
    return statistics.mean(values) if values else None


def success_rate(rows, algorithm):
    runs = [r for r in rows if r["algorithm"] == algorithm]
    return sum(r["status"] == "success" for r in runs) / len(runs) if runs else None


# ====================================================================== 各问题

def turn_section(turn: dict) -> tuple[list[str], dict]:
    lines = ["## X1 转弯代价与运动时间（Q1～Q4）", ""]
    curves = {}
    lines += ["### Q1 朝向 A* 与重复 A*（主指标：规则代价 / 最优，越低越好）", "", *PAIR_HEADER]
    for name, rows in turn.items():
        lines += fmt_pair(paired(rows, "turn_aware_astar", "repeated_astar", "rule_cost_ratio"),
                          f"{name}：turn_aware_astar vs repeated_astar")
    lines += ["", "### Q2 平均代价比排名（成功运行；括号内为成功率）", ""]
    algorithms = sorted({r["algorithm"] for rows in turn.values() for r in rows})
    lines += ["| 子实验 | 第 1 | 第 2 | 第 3 | 最差 |", "| --- | --- | --- | --- | --- |"]
    for name, rows in turn.items():
        ranked = sorted((a for a in algorithms if mean_of(rows, a, "rule_cost_ratio") is not None),
                        key=lambda a: mean_of(rows, a, "rule_cost_ratio"))
        cell = lambda a: f"{a} {mean_of(rows, a, 'rule_cost_ratio'):.3f}（{success_rate(rows, a):.0%}）"  # noqa: E731
        lines.append(f"| {name} | " + " | ".join(cell(a) for a in ranked[:3]) + f" | {cell(ranked[-1])} |")
        for a in algorithms:
            curves.setdefault(a, {})[name] = mean_of(rows, a, "rule_cost_ratio")
    lines += ["", "### Q3 加权 A*（w = 2）与 w = 1", "", *PAIR_HEADER]
    for name, rows in turn.items():
        lines += fmt_pair(paired(rows, "turn_aware_astar_w2", "turn_aware_astar", "rule_cost_ratio"),
                          f"{name}：代价比，w2 vs w1")
        lines += fmt_pair(paired(rows, "turn_aware_astar_w2", "turn_aware_astar", "expanded_nodes"),
                          f"{name}：扩展状态数，w2 vs w1")
    lines += ["", "### Q4 D* Lite 与重复 A*（计算时间：3 次重复的中位数，毫秒）", "", *PAIR_HEADER]
    for name, rows in turn.items():
        lines += fmt_pair(paired(rows, "dstar_lite", "repeated_astar", "compute_ms"),
                          f"{name}：计算时间，dstar_lite vs repeated_astar")
    first = next(iter(turn.values()), [])
    if first:
        med = lambda a: statistics.median(float(r["compute_ms"]) for r in first if r["algorithm"] == a)  # noqa: E731
        lines += ["", f"计算时间中位数（{next(iter(turn))}）：dstar_lite {med('dstar_lite'):.2f} ms，"
                      f"repeated_astar {med('repeated_astar'):.2f} ms。", ""]
        lines += [same_route_line(first)]
    lines.append("")
    return lines, curves


def same_route_line(rows: list[dict]) -> str:
    """Q4 路线：两种算法都按步数选路，与代价规则无关；在测试集上重新运行比较完整路线。"""
    from core.algorithm_api import Maze, load_algorithm, run_episode
    maze_ids = sorted({r["maze_id"] for r in rows})
    same = 0
    for m in maze_ids:
        maze = Maze.from_json(ROOT / "mazes" / "classic" / f"{m}.json")
        a = run_episode(maze, load_algorithm("dstar_lite"))["path"]
        b = run_episode(maze, load_algorithm("repeated_astar"))["path"]
        same += a == b
    return (f"路线完全相同的地图：{same}/{len(maze_ids)}（{same / len(maze_ids):.0%}；"
            "两种算法都只按步数选路，路线与代价规则无关，因此在基础规则下重新运行比较）。")


def noise_section(noise: dict) -> tuple[list[str], dict]:
    lines = ["## X2 噪声观测（Q5、Q6）", "",
             "### Q5 置信度融合与只信最近读数（主指标：步数 / 最短路，按地图 × 种子配对）", "", *PAIR_HEADER]
    for name, rows in noise.items():
        lines += fmt_pair(paired(rows, "belief_astar", "belief_astar_naive", "ratio"),
                          f"{name}：belief_astar vs naive")
        if "collisions" in rows[0]:
            lines += fmt_pair(paired(rows, "belief_astar", "belief_astar_naive", "collisions"),
                              f"{name}：撞墙次数，belief_astar vs naive")
    lines += ["", "### Q6 各档噪声与理想观测（均值；成功率含全部运行）", "",
              "| 子实验 | 算法 | 成功率 | 步数 / 最短路 | 撞墙次数 |", "| --- | --- | --- | --- | --- |"]
    curves = {}
    for name, rows in noise.items():
        for a in ("belief_astar", "belief_astar_naive"):
            ratio = mean_of(rows, a, "ratio")
            coll = mean_of(rows, a, "collisions", success_only=False) if "collisions" in rows[0] else 0.0
            lines.append(f"| {name} | {a} | {success_rate(rows, a):.1%} | {ratio:.3f} | {coll:.1f} |")
            curves.setdefault(a, {})[name] = (ratio, coll)
    lines.append("")
    return lines, curves


def two_phase_section(two: dict) -> tuple[list[str], dict]:
    eps = {"bounded_explore_e0": 0.0, "bounded_explore_e10": 0.1, "bounded_explore_e25": 0.25}
    baselines = ["repeated_astar", "flood_fill", "turn_aware_astar"]
    lines = ["## X3 两阶段比赛（Q7）", "", "### 均值（成功运行）", "",
             "| 子实验 | 算法 | 成功率 | 探索代价（含返回） | 冲刺 / 最优 | 成绩 |", "| --- | --- | --- | --- | --- | --- |"]
    curves = {}
    for name, rows in two.items():
        for a in baselines + list(eps):
            lines.append(f"| {name} | {a} | {success_rate(rows, a):.1%} | {mean_of(rows, a, 'explore_cost'):.1f} | "
                         f"{mean_of(rows, a, 'sprint_ratio'):.3f} | {mean_of(rows, a, 'total_score'):.2f} |")
            curves.setdefault(name, {})[a] = mean_of(rows, a, "total_score")
    lines += ["", "### 理论保证核对：冲刺 / 最优 ≤ 1 + ε", ""]
    for name, rows in two.items():
        for a, e in eps.items():
            worst = max((float(r["sprint_ratio"]) for r in rows if r["algorithm"] == a and r["status"] == "success"),
                        default=None)
            ok = worst is not None and worst <= 1 + e + 1e-6
            lines.append(f"- {name} / {a}：最大冲刺 / 最优 = {worst:.4f}，上限 {1 + e:g} → {'成立' if ok else '**不成立**'}")
    lines += ["", "### 成绩配对比较（越低越好）", "", *PAIR_HEADER]
    for name, rows in two.items():
        for a in eps:
            for b in baselines:
                lines += fmt_pair(paired(rows, a, b, "total_score"), f"{name}：{a} vs {b}")
    lines.append("")
    return lines, curves


# ====================================================================== 图表

def plot(turn_curves, noise_curves, two_curves) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from core.experiments import INK, PALETTE, SURFACE, _style
    files = []

    def save(fig, name):
        fig.patch.set_facecolor(SURFACE)
        fig.tight_layout()
        fig.savefig(OUT / name, dpi=150)
        plt.close(fig)
        files.append(name)

    lambdas = [("lambda_0.5", 0.5), ("lambda_1", 1), ("lambda_2", 2), ("lambda_4", 4)]
    if turn_curves:
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for i, (a, values) in enumerate(sorted(turn_curves.items())):
            xs = [x for key, x in lambdas if values.get(key) is not None]
            ys = [values[key] for key, _ in lambdas if values.get(key) is not None]
            ax.plot(xs, ys, marker="o", color=PALETTE[i % len(PALETTE)], label=a, linewidth=1.6)
        ax.set_xscale("log", base=2)
        _style(ax, "Turn cost: mean rule cost / optimal vs lambda", "rule cost / optimal")
        ax.set_xlabel("lambda", color=INK)
        ax.legend(fontsize=7, ncol=2, frameon=False)
        save(fig, "lambda_curve.png")
    if noise_curves:
        levels = ["ideal", "high", "mid", "low"]
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
        for i, (a, values) in enumerate(sorted(noise_curves.items())):
            a1.plot(levels, [values[l][0] for l in levels], marker="o", color=PALETTE[i], label=a)
            a2.plot(levels, [values[l][1] for l in levels], marker="o", color=PALETTE[i], label=a)
        _style(a1, "Noise: steps / shortest", "steps / shortest")
        _style(a2, "Noise: collisions per run", "collisions")
        a1.legend(fontsize=8, frameon=False)
        save(fig, "noise_curve.png")
    if two_curves:
        fig, ax = plt.subplots(figsize=(7.5, 4))
        eps = [("bounded_explore_e0", 0), ("bounded_explore_e10", 0.1), ("bounded_explore_e25", 0.25)]
        for i, (name, values) in enumerate(two_curves.items()):
            ax.plot([e for _, e in eps], [values[a] for a, _ in eps], marker="o", color=PALETTE[i], label=f"{name}: bounded")
            ax.axhline(values["repeated_astar"], color=PALETTE[i], linestyle="--", linewidth=1,
                       label=f"{name}: repeated_astar (stop at goal)")
        _style(ax, "Two-phase: mean total score vs epsilon", "total score (lower is better)")
        ax.set_xlabel("epsilon", color=INK)
        ax.legend(fontsize=7, frameon=False)
        save(fig, "epsilon_curve.png")
    return files


def main() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    turn, noise, two = experiments("turn"), experiments("noise"), experiments("two_phase")
    lines = ["# 扩展实验分析", "",
             "按冻结的 [实验计划](../../../Docs/ext/experiment-plan.md) 第 5 节：配对胜负（a 相对 b，a 更好记胜）、"
             "双侧符号检验（p < 0.05）、外部迷宫库与生成图两组方向一致才写总体结论。由 `python src/ext/analysis.py` 生成。", ""]
    turn_curves = noise_curves = two_curves = {}
    if turn:
        section, turn_curves = turn_section(turn)
        lines += section
    if noise:
        section, noise_curves = noise_section(noise)
        lines += section
    if two:
        section, two_curves = two_phase_section(two)
        lines += section
    files = plot(turn_curves, noise_curves, two_curves)
    lines += ["## 图", ""] + [f"![{f}]({f})" for f in files] + [""]
    path = OUT / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


if __name__ == "__main__":
    print(main())
