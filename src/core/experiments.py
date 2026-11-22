"""批量实验框架（公共接口层，与规则层无关）：在多张地图上运行多个算法，导出原始数据、汇总表、运行环境和图表。

本模块只提供通用的运行、汇总、导出与画图；“跑哪些地图、哪些算法、几个种子”由各层的实验计划决定：
    - 基础规则：src/basic/plan.py（Docs/basic/experiment-plan.md）；
    - 扩展：src/ext/plan.py（Docs/ext/experiment-plan.md）。
各计划模块定义 PLANS = {名称: (构建函数, 默认输出目录)}，命令行 --plan <名称> 自动找到它们。
本模块不依赖界面库，命令行与上位机“批量实验”页共用：
    - 每次运行都通过 algorithm_api.run_episode 执行，规则与上位机、测试完全一致；
    - 每张地图先用 BFS 求已知地图最短路，作为“步数 / 最短路”的分母；
    - 计时只含算法自身；repeats > 1 时同一组合重复运行，计算时间取中位数，并检查结果是否一致；
    - 失败的运行保留状态与原因，只与成功路径相关的指标（ratio）留空，不填 0。

命令行（项目根目录）：
    python src/run_experiments.py --plan basic                          # 基础规则的全部正式实验
    python src/run_experiments.py --maps "mazes/classic/external_*.json" --algorithms dfs flood_fill
    python src/run_experiments.py --plot results/basic/main             # 只从 summary.csv 重画图表
输出：runs.csv、summary.csv、summary.md、metadata.json、figures/*.png。
自选实验默认写到 results/local/<时间>/（不提交）；--plan 写到计划指定的目录（如 results/basic/）。
"""

import argparse
import csv
import glob
import importlib
import json
import platform
import statistics
import subprocess
import sys
import tracemalloc
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 只写文件、不弹窗口；与上位机（Qt）同时使用也不冲突
import matplotlib.pyplot as plt  # noqa: E402

from core.algorithm_api import EXPLORE, KNOWN_MAP, Maze, discover_algorithms, run_episode  # noqa: E402
from core.rules import BASIC, Ruleset, parse_rule  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]  # src/core/experiments.py → 项目根目录
MAZE_DIR = ROOT / "mazes" / "classic"
RESULTS = ROOT / "results"
LOCAL_RESULTS = RESULTS / "local"  # 自选 / 上位机实验的默认输出，不提交（见 .gitignore）
# 实验计划模块：每个模块定义 PLANS = {名称: (构建函数, 结果目录名)}；不存在的模块跳过。
PLAN_MODULES = ("basic.plan", "ext.plan")

RUN_FIELDS = ["run_id", "experiment", "maze_id", "map_group", "algorithm", "experiment_mode",
              "config_id", "seed", "status", "steps", "shortest", "ratio", "turns_90",
              "repeat_visits", "visited_cells", "coverage", "compute_ms",
              "compute_ms_min", "repeats", "consistent", "expanded_nodes", "peak_memory_bytes",
              "error"]
SUMMARY_FIELDS = ["map_group", "algorithm", "experiment_mode", "runs", "success", "success_rate",
                  "mean_steps", "mean_ratio", "median_ratio", "max_ratio", "mean_turns",
                  "mean_repeat_visits", "mean_coverage", "median_compute_ms", "mean_expanded_nodes"]
# 扩展规则（有代价层）时追加的列；基础规则不写这些列，输出格式与 basic-rules-v1 相同。
COLLISION_RUN_FIELDS = ["actions", "collisions"]
COLLISION_SUMMARY_FIELDS = ["mean_actions", "mean_collisions", "collision_run_rate"]
RULE_RUN_FIELDS = ["rule", "rule_cost", "optimal_rule_cost", "rule_cost_ratio"]
RULE_SUMMARY_FIELDS = ["mean_rule_cost", "mean_rule_cost_ratio", "median_rule_cost_ratio",
                       "max_rule_cost_ratio"]


# ====================================================================== 地图与分组

def map_group(maze: Maze) -> str:
    """地图分组：外部迷宫库（external_*）为 external；生成迷宫为 <生成算法>_loop<环路百分比>；其他为 other。"""
    meta = maze.metadata or {}
    if meta.get("source") == "generated":
        generator = meta.get("generator", "unknown").replace("recursive_", "")
        return f"{generator}_loop{round(float(meta.get('loop_fraction', 0)) * 100)}"
    if maze.maze_id.startswith("external_"):
        return "external"
    return "other"


def expand_maps(patterns: list[str]) -> list[Path]:
    """展开地图路径或通配符（相对路径相对于项目根目录），去重并保持顺序。"""
    paths: list[Path] = []
    for pattern in patterns:
        full = pattern if Path(pattern).is_absolute() else str(ROOT / pattern)
        matches = sorted(glob.glob(full)) if any(c in pattern for c in "*?[") else [full]
        paths.extend(Path(m) for m in matches if Path(m).suffix == ".json")
    return list(dict.fromkeys(paths))


# ====================================================================== 运行

class ExperimentRun:
    """一次批量实验：保存设置，逐个执行（地图 × 算法 × 种子）组合，收集结果行。

    上位机用 tasks() + run_task() 逐个推进以保持界面响应；命令行用 run_all()。
    """

    def __init__(self, maze_paths: list[Path], algorithms: list[str], *, seeds=(0,),
                 repeats: int = 1, max_steps: int | None = None, measure_memory: bool = False,
                 experiment: str = "custom", rule: Ruleset = BASIC, include_collision_stats: bool = False):
        """记录实验设置。

        Args:
            maze_paths: 地图文件。
            algorithms: 算法名（由 discover_algorithms 发现）。
            seeds: 传给算法的种子；每个种子单独运行一次（只影响随机算法）。
            repeats: 同一组合重复运行的次数，计算时间取中位数（用于稳定计时）。
            max_steps: 动作预算；None 时为 20 × 格子数。
            measure_memory: 是否用 tracemalloc 另外运行一轮测峰值内存（会变慢，与计时分开）。
            experiment: 写入结果的实验名称。
            rule: 比赛规则（core.rules），默认基础规则；有代价层时额外记录规则代价与最优规则代价。
            include_collision_stats: 首次撞墙终止模式也导出动作与碰撞统计。
        """
        self.infos, errors = discover_algorithms()
        if errors:
            raise RuntimeError("算法导入失败：" + "；".join(errors))
        unknown = [a for a in algorithms if a not in self.infos]
        if unknown:
            raise ValueError(f"unknown algorithms: {unknown}")
        self.rule = rule
        self.include_collision_stats = include_collision_stats or rule.collision_limit != 1
        for name in algorithms:
            if not rule.supports(self.infos[name]):
                raise ValueError(f"{name} does not support rule {rule.key}")
        self.maze_paths = list(maze_paths)
        self.algorithms = list(algorithms)
        self.seeds = list(seeds)
        self.repeats = max(1, repeats)
        self.max_steps = max_steps
        self.measure_memory = measure_memory
        self.experiment = experiment
        self.rows: list[dict] = []
        self.started = datetime.now()
        self._mazes: dict[Path, tuple[Maze, int | None, float | None]] = {}

    def tasks(self) -> list[tuple[Path, str, int]]:
        """全部（地图, 算法, 种子）组合。"""
        return [(m, a, s) for m in self.maze_paths for a in self.algorithms for s in self.seeds]

    @property
    def has_rule_cost(self) -> bool:
        """本次实验的规则是否有代价层（有则输出规则代价相关的列）。"""
        return self.rule.cost_layer is not None

    def run_fields(self) -> list[str]:
        """runs.csv 的列：基础列，以及启用的碰撞和规则代价列。"""
        collision_fields = COLLISION_RUN_FIELDS if self.include_collision_stats else []
        return RUN_FIELDS + collision_fields + (RULE_RUN_FIELDS if self.has_rule_cost else [])

    def _maze(self, path: Path) -> tuple[Maze, int | None, float | None]:
        """读取地图，计算已知地图最短路长度与本规则下的最优代价（不可达时为 None），结果缓存。"""
        if path not in self._mazes:
            maze = Maze.from_json(path)
            best = run_episode(maze, self.infos["bfs"].create()) if "bfs" in self.infos else None
            shortest = best["steps"] if best and best["status"] == "success" else None
            optimal = self.rule.optimal_cost(maze) if self.has_rule_cost else None
            self._mazes[path] = (maze, shortest, optimal)
        return self._mazes[path]

    def run_task(self, maze_path: Path, algorithm: str, seed: int) -> dict:
        """运行一个组合并返回结果行（同时追加到 self.rows）。"""
        maze, shortest, optimal = self._maze(maze_path)
        info = self.infos[algorithm]
        results = [run_episode(maze, info.create(), seed=seed, max_steps=self.max_steps, rule=self.rule,
                               include_collision_stats=self.include_collision_stats)
                   for _ in range(self.repeats)]
        first = results[0]
        times = [r["compute_seconds"] * 1000 for r in results]
        success = first["status"] == "success"
        path = first["path"]
        row = {
            "run_id": len(self.rows) + 1, "experiment": self.experiment,
            "maze_id": maze.maze_id, "map_group": map_group(maze), "algorithm": algorithm,
            "experiment_mode": "known_map_planning" if info.mode == KNOWN_MAP else "unknown_exploration",
            "config_id": f"{algorithm}:default", "seed": seed, "status": first["status"],
            "steps": first["steps"], "shortest": shortest if shortest is not None else "",
            "ratio": round(first["steps"] / shortest, 4) if success and shortest else "",
            "turns_90": first["turns_90"], "repeat_visits": first["repeat_visits"],
            "visited_cells": len(set(map(tuple, path))),
            "coverage": round(len(set(map(tuple, path))) / (maze.width * maze.height), 4),
            "compute_ms": round(statistics.median(times), 3),
            "compute_ms_min": round(min(times), 3), "repeats": self.repeats,
            "consistent": all(all(r.get(k) == first.get(k) for k in ("path", "status", "collisions", "actions", "turns_90"))
                              for r in results),
            "expanded_nodes": first.get("expanded_nodes", ""),
            "peak_memory_bytes": self._peak_memory(maze, info, seed) if self.measure_memory else "",
            "error": (first.get("error") or "").strip().splitlines()[-1] if first.get("error") else "",
        }
        if self.include_collision_stats:
            row.update(actions=first["actions"], collisions=first["collisions"])
        if self.has_rule_cost:
            cost = first.get("rule_cost")
            row.update({"rule": self.rule.key, "rule_cost": cost,
                        "optimal_rule_cost": optimal if optimal is not None else "",
                        "rule_cost_ratio": round(cost / optimal, 4) if success and optimal else ""})
        self.rows.append(row)
        return row

    def _peak_memory(self, maze: Maze, info, seed: int) -> int:
        """单独运行一轮，用 tracemalloc 测量 Python 对象的峰值内存（不代表进程总内存）。"""
        tracemalloc.start()
        try:
            run_episode(maze, info.create(), seed=seed, max_steps=self.max_steps, rule=self.rule)
            return tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()

    def run_all(self, progress=None) -> list[dict]:
        """依次运行全部组合；progress(完成数, 总数) 用于显示进度。"""
        tasks = self.tasks()
        for i, task in enumerate(tasks, 1):
            self.run_task(*task)
            if progress:
                progress(i, len(tasks))
        return self.rows

    @property
    def expected_rows(self) -> int:
        return len(self.maze_paths) * len(self.algorithms) * len(self.seeds)

    def settings(self) -> dict:
        """返回预览和结果元数据共用的实验设置。"""
        return {
            "experiment": self.experiment, "rule": self.rule.metadata(),
            "maps": len(self.maze_paths),
            "map_files": [path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT)
                          else path.as_posix() for path in self.maze_paths],
            "algorithms": self.algorithms,
            "algorithm_info": {name: {"layer": self.infos[name].layer, "mode": self.infos[name].mode,
                                      "designed_for": sorted(self.infos[name].designed_for),
                                      "designed_for_rule": self.infos[name].designed_for_rule(self.rule)}
                               for name in self.algorithms},
            "seeds": self.seeds, "repeats": self.repeats,
            "max_steps": self.max_steps or "20 × 格子数", "time_budget_seconds": 30.0,
            "measure_memory": self.measure_memory, "expected_rows": self.expected_rows,
            "timed_episodes": self.expected_rows * self.repeats, "run_fields": self.run_fields(),
        }

    def metadata(self) -> dict:
        """运行环境与设置，写入 metadata.json。"""
        return {
            **self.settings(), "started": self.started.isoformat(timespec="seconds"),
            "finished": datetime.now().isoformat(timespec="seconds"),
            "git_commit": _git_commit(), "python": sys.version.split()[0],
            "platform": platform.platform(), "processor": platform.processor(),
            "timing_scope": "只含算法 reset / plan / choose_direction；不含读图、环境检查、绘图与写盘",
            "runs": len(self.rows),
        }


def _git_commit() -> str:
    """当前代码的 git 提交号；src、tools、mazes 有未提交改动时加 +dirty；无法获取时返回空字符串。"""
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True,
                                capture_output=True, timeout=10).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "src", "tools", "mazes"],
                               cwd=ROOT, text=True, capture_output=True, timeout=10).stdout.strip()
        return commit + ("+dirty" if commit and dirty else "")  # +dirty：运行时代码或地图有未提交改动
    except (OSError, subprocess.SubprocessError):
        return ""


# ====================================================================== 汇总与导出

def summarize(rows: list[dict]) -> list[dict]:
    """按（地图分组, 算法）汇总；另加一组 ALL 表示全部地图。成功路径指标只统计成功的运行。"""
    def mean(values):
        values = [v for v in values if v != ""]
        return round(statistics.mean(values), 3) if values else ""

    keys = sorted({(r["map_group"], r["algorithm"], r["experiment_mode"]) for r in rows})
    keys += sorted({("ALL", r["algorithm"], r["experiment_mode"]) for r in rows})
    summary = []
    for group, algorithm, mode in keys:
        runs = [r for r in rows if r["algorithm"] == algorithm and group in ("ALL", r["map_group"])]
        ok = [r for r in runs if r["status"] == "success"]
        ratios = [r["ratio"] for r in ok if r["ratio"] != ""]
        summary.append({
            "map_group": group, "algorithm": algorithm, "experiment_mode": mode,
            "runs": len(runs), "success": len(ok), "success_rate": round(len(ok) / len(runs), 4),
            "mean_steps": mean([r["steps"] for r in ok]),
            "mean_ratio": mean(ratios), "median_ratio": round(statistics.median(ratios), 3) if ratios else "",
            "max_ratio": max(ratios) if ratios else "",
            "mean_turns": mean([r["turns_90"] for r in ok]),
            "mean_repeat_visits": mean([r["repeat_visits"] for r in ok]),
            "mean_coverage": mean([r["coverage"] for r in runs]),
            "median_compute_ms": round(statistics.median(r["compute_ms"] for r in runs), 3),
            "mean_expanded_nodes": mean([r["expanded_nodes"] for r in runs]),
        })
        if "collisions" in runs[0]:
            summary[-1].update({
                "mean_actions": mean([r["actions"] for r in runs]),
                "mean_collisions": mean([r["collisions"] for r in runs]),
                "collision_run_rate": round(sum(r["collisions"] > 0 for r in runs) / len(runs), 4),
            })
        if any("rule_cost" in r for r in runs):
            cost_ratios = [r["rule_cost_ratio"] for r in ok if r["rule_cost_ratio"] != ""]
            summary[-1].update({
                "mean_rule_cost": mean([r["rule_cost"] for r in ok]),
                "mean_rule_cost_ratio": mean(cost_ratios),
                "median_rule_cost_ratio": round(statistics.median(cost_ratios), 3) if cost_ratios else "",
                "max_rule_cost_ratio": max(cost_ratios) if cost_ratios else "",
            })
    return summary


def write_outputs(run: ExperimentRun, out_dir: Path, *, plot: bool = True) -> Path:
    """写出 runs.csv、summary.csv、summary.md、metadata.json，并（可选）生成图表。"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=run.run_fields())
        writer.writeheader()
        writer.writerows(run.rows)
    summary = summarize(run.rows)
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        fields = list(SUMMARY_FIELDS)
        if run.include_collision_stats:
            fields.extend(COLLISION_SUMMARY_FIELDS)
        if run.has_rule_cost:
            fields.extend(RULE_SUMMARY_FIELDS)
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)
    heading = "" if run.rule.is_basic else f"# 规则：{run.rule.title}\n\n"
    (out_dir / "summary.md").write_text(heading + summary_markdown(summary), encoding="utf-8")
    (out_dir / "metadata.json").write_text(json.dumps(run.metadata(), ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    if plot:
        plot_all(out_dir)
    return out_dir


def summary_markdown(summary: list[dict]) -> str:
    """把汇总表写成 Markdown，探索算法与已知地图算法分成两张表。"""
    lines = []
    for mode, title in (("unknown_exploration", "未知地图探索"), ("known_map_planning", "已知地图规划（参照）")):
        rows = [s for s in summary if s["experiment_mode"] == mode]
        if not rows:
            continue
        lines += [f"## {title}", "",
                  "| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for s in rows:
            lines.append(f"| {s['map_group']} | {s['algorithm']} | {s['success']}/{s['runs']} | "
                         f"{s['mean_steps']} | {s['mean_ratio']} | {s['median_ratio']} | {s['max_ratio']} | "
                         f"{s['mean_turns']} | {s['mean_repeat_visits']} | {s['median_compute_ms']} | "
                         f"{s['mean_expanded_nodes']} |")
        lines.append("")
        if "mean_collisions" in rows[0]:
            lines += ["动作与碰撞（含成功和失败运行）", "",
                      "| 地图组 | 算法 | 平均动作数 | 平均碰撞数 | 至少撞墙一次的比例 |",
                      "| --- | --- | --- | --- | --- |"]
            lines += [f"| {s['map_group']} | {s['algorithm']} | {s['mean_actions']} | "
                      f"{s['mean_collisions']} | {s['collision_run_rate']:.2%} |" for s in rows]
            lines.append("")
        if any("mean_rule_cost" in s for s in rows):
            lines += ["规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：", "",
                      "| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |",
                      "| --- | --- | --- | --- | --- | --- |"]
            lines += [f"| {s['map_group']} | {s['algorithm']} | {s['mean_rule_cost']} | "
                      f"{s['mean_rule_cost_ratio']} | {s['median_rule_cost_ratio']} | {s['max_rule_cost_ratio']} |"
                      for s in rows]
            lines.append("")
    return "\n".join(lines)


# ====================================================================== 图表

# 颜色按算法名固定分配（同一算法在所有图中颜色相同），取自经过色觉验证的默认分类色板。
# 分类色板（固定顺序，不循环）；颜色跟随算法，而不是排名。
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
ALGORITHM_COLORS = {
    "flood_fill": PALETTE[0], "repeated_astar": PALETTE[1], "dfs": PALETTE[2],
    "greedy_dfs": PALETTE[3], "wall_follower_left": PALETTE[4], "wall_follower_right": PALETTE[5],
    "random_walk": PALETTE[6], "prior_astar": PALETTE[7], "bfs": PALETTE[0], "astar": PALETTE[1],
}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#898781", "#e6e5e1", "#fcfcfb"
# 已知地图算法只是参照，与探索算法同图出现时用中性灰，避免与探索算法撞色。
REFERENCE_COLORS = {"bfs": "#898781", "astar": "#52514e", "rule_optimal": "#343a40"}


def read_summary(result_dir: Path) -> list[dict]:
    """读取 summary.csv，数值列转为 float（空值为 None）。"""
    with (Path(result_dir) / "summary.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key, value in row.items():
            if key not in ("map_group", "algorithm", "experiment_mode"):
                row[key] = float(value) if value != "" else None
    return rows


def _color(algorithm: str, index: int) -> str:
    """算法的固定颜色；新算法按出现顺序取色板中未使用的颜色。"""
    return ALGORITHM_COLORS.get(algorithm, PALETTE[index % len(PALETTE)])


def _style(ax, title: str, ylabel: str) -> None:
    """统一的坐标轴样式：浅色网格、无多余边框、文字用墨色。"""
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=12, loc="left")
    ax.set_ylabel(ylabel, color=INK)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=9)


def _grouped_bars(ax, groups: list[str], algorithms: list[str], value, colors=None) -> None:
    """分组柱状图：每个地图组一簇，每个算法一根；缺失值不画。colors 不给时用算法的固定颜色。"""
    width = 0.8 / max(1, len(algorithms))
    for i, algorithm in enumerate(algorithms):
        xs, ys = [], []
        for g, group in enumerate(groups):
            v = value(group, algorithm)
            if v is not None:
                xs.append(g - 0.4 + width * (i + 0.5))
                ys.append(v)
        ax.bar(xs, ys, width=width * 0.9, color=colors[i] if colors else _color(algorithm, i), label=algorithm,
               edgecolor=SURFACE, linewidth=1)
    ax.set_xticks(range(len(groups)), groups, rotation=20, ha="right")
    ax.legend(frameon=False, fontsize=8, ncols=min(4, len(algorithms)), loc="upper left")


def plot_all(result_dir: Path) -> list[Path]:
    """根据 summary.csv 生成全部图表（写入 <结果目录>/figures/），返回写出的文件。

    消融变体（类属性 ablation_of 非空的算法）不进主图；每个有消融变体的算法另画 ablation_<算法名>.png，
    包含它的消融基线（类属性 ablation_baseline）、全部变体与完整版。
    生成：ratio_by_group.png（各地图组的平均“步数 / 最短路”，对数坐标）、success_by_group.png（成功率）、
    compute_time.png（各算法计算时间中位数）、expanded_nodes.png（已知地图算法的扩展节点数）。
    图中文字使用英文，避免默认字体缺少中文字形；数值表见同目录 summary.md。
    """
    result_dir = Path(result_dir)
    metadata = result_dir / "metadata.json"
    settings = json.loads(metadata.read_text(encoding="utf-8")) if metadata.exists() else {}
    rule = settings.get("rule", {})
    rule_spec = rule.get("spec", rule.get("key", BASIC.spec))
    rows = read_summary(result_dir)
    out = result_dir / "figures"
    out.mkdir(exist_ok=True)
    lookup = {(r["map_group"], r["algorithm"]): r for r in rows}
    infos = discover_algorithms()[0]
    variants = {name for name, info in infos.items() if info.ablation_of}
    explore = [r for r in rows if r["experiment_mode"] == "unknown_exploration"
               and r["algorithm"] not in variants]
    known = [r for r in rows if r["experiment_mode"] == "known_map_planning"]
    groups = sorted({r["map_group"] for r in rows if r["map_group"] != "ALL"},
                    key=lambda g: (g != "external", g))
    written = []

    def save(fig, name):
        fig.patch.set_facecolor(SURFACE)
        if rule_spec != BASIC.spec:
            fig.suptitle(f"Rule: {rule_spec}", color=INK, fontsize=10, x=0.01, ha="left")
        fig.tight_layout()
        path = out / name
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)

    explorers = sorted({r["algorithm"] for r in explore},
                       key=lambda a: list(ALGORITHM_COLORS).index(a) if a in ALGORITHM_COLORS else 99)
    if explorers:
        fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(groups) + 3), 4.5))
        _grouped_bars(ax, groups, explorers,
                      lambda g, a: (lookup.get((g, a)) or {}).get("mean_ratio"))
        ax.set_yscale("log")
        ax.axhline(1, color=MUTED, linewidth=1, linestyle="--")
        _style(ax, "Steps / known-map shortest path (successful runs, mean; 1 = optimal)",
               "ratio (log scale)")
        save(fig, "ratio_by_group.png")

        fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(groups) + 3), 4.5))
        _grouped_bars(ax, groups, explorers,
                      lambda g, a: (lookup.get((g, a)) or {}).get("success_rate"))
        ax.set_ylim(0, 1.15)
        _style(ax, "Success rate within budget", "success rate")
        save(fig, "success_by_group.png")

        if any(r.get("mean_rule_cost_ratio") is not None for r in explore):
            fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(groups) + 3), 4.5))
            _grouped_bars(ax, groups, explorers,
                          lambda g, a: (lookup.get((g, a)) or {}).get("mean_rule_cost_ratio"))
            ax.axhline(1, color=MUTED, linewidth=1, linestyle="--")
            _style(ax, "Rule cost / known-map rule optimum (successful runs, mean; 1 = optimal)", "ratio")
            save(fig, "rule_cost_ratio_by_group.png")

    everyone = [r for r in rows if r["map_group"] == "ALL" and r["algorithm"] not in variants]
    if everyone:
        everyone.sort(key=lambda r: r["median_compute_ms"] or 0)
        fig, ax = plt.subplots(figsize=(7, 0.45 * len(everyone) + 1.5))
        ax.barh([r["algorithm"] + (" (reference)" if r["algorithm"] in REFERENCE_COLORS else "")
                 for r in everyone], [r["median_compute_ms"] for r in everyone],
                color=[REFERENCE_COLORS.get(r["algorithm"], _color(r["algorithm"], i))
                       for i, r in enumerate(everyone)], height=0.6)
        ax.set_xscale("log")
        _style(ax, "Algorithm compute time per run (median, all maps)", "")
        ax.set_xlabel("milliseconds (log scale)", color=INK)
        ax.grid(axis="x", color=GRID, linewidth=0.8)
        save(fig, "compute_time.png")

    planners = sorted({r["algorithm"] for r in known})
    if planners:
        fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(groups) + 3), 4.5))
        _grouped_bars(ax, groups, planners,
                      lambda g, a: (lookup.get((g, a)) or {}).get("mean_expanded_nodes"))
        _style(ax, "Known-map planners: nodes expanded (same shortest length)", "expanded nodes")
        save(fig, "expanded_nodes.png")

    present = {r["algorithm"] for r in rows}
    for full in sorted({infos[v].ablation_of for v in variants & present}):
        baseline = infos[full].ablation_baseline if full in infos else ""
        members = [a for a in [baseline, *sorted(v for v in variants & present
                                                 if infos[v].ablation_of == full), full]
                   if a and a in present]
        # 单独一张图，颜色按本图内顺序取色板（与主图的颜色无关）。
        fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(groups) + 3), 4.5))
        _grouped_bars(ax, groups, members,
                      lambda g, a: (lookup.get((g, a)) or {}).get("mean_ratio"),
                      colors=[PALETTE[i % len(PALETTE)] for i in range(len(members))])
        ax.axhline(1, color=MUTED, linewidth=1, linestyle="--")
        _style(ax, f"Ablation of {full}: steps / shortest path (mean; baseline = {baseline or 'none'})",
               "ratio")
        save(fig, f"ablation_{full}.png")
    return written



# ====================================================================== 实验计划注册

def available_plans() -> dict:
    """收集各层 plan 模块中的 PLANS：{名称: (构建函数, 结果目录名)}。尚未创建的计划模块跳过。"""
    plans = {}
    for module_name in PLAN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                continue
            raise
        plans.update(getattr(module, "PLANS", {}))
    return plans


def main(argv: list[str] | None = None) -> None:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    plans = available_plans()
    parser.add_argument("--plan", choices=sorted(plans), help="按某一层的实验计划运行全部正式实验")
    parser.add_argument("--rule", default=None, metavar="SPEC",
                        help="自选实验的规则，默认 basic；如 turn_cost:weight=2+collision:limit=3、collision:limit=unlimited、motion_time"
                             "（写法见 core.rules.parse_rule）。正式计划自带规则，不能另指定")
    parser.add_argument("--maps", nargs="+", help="地图路径或通配符")
    parser.add_argument("--algorithms", nargs="+", help="算法名，all 表示全部")
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--repeats", type=int, help="重复次数，计算时间取中位数")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--collision-stats", action="store_true",
                        help="自选实验中，即使首次撞墙就终止也导出动作和碰撞统计")
    parser.add_argument("--memory", action="store_true", help="另外运行一轮测量峰值内存")
    parser.add_argument("--out", type=Path, default=None,
                        help="输出目录；默认 --plan 写到计划目录，自选实验写到 results/local/<时间>")
    parser.add_argument("--no-plot", action="store_true")
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument("--dry-run", action="store_true", help="预览完整设置和输出路径，无执行和文件输出")
    output_mode.add_argument("--plot", nargs="+", type=Path, metavar="RESULT_DIR",
                        help="不运行实验，只从这些结果目录的 summary.csv 重画图表")
    args = parser.parse_args(argv)
    if args.plot:
        for directory in args.plot:
            for path in plot_all(directory):
                print(path)
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.plan:
        overrides = {"--rule": args.rule, "--maps": args.maps, "--algorithms": args.algorithms,
                     "--seeds": args.seeds, "--repeats": args.repeats, "--max-steps": args.max_steps,
                     "--memory": args.memory or None, "--collision-stats": args.collision_stats or None}
        supplied = [name for name, value in overrides.items() if value is not None]
        if supplied:
            parser.error(f"--plan 自带实验设置，不能覆盖 {', '.join(supplied)}")
        build, folder = plans[args.plan]
        runs = build()
        base = args.out or RESULTS / folder
    else:
        try:
            rule = parse_rule(args.rule or "basic")
        except ValueError as exc:
            parser.error(str(exc))
        infos = discover_algorithms()[0]
        algorithms = ([name for name, info in infos.items() if rule.supports(info)]
                      if args.algorithms in (None, ["all"]) else args.algorithms)
        runs = [ExperimentRun(expand_maps(args.maps or ["mazes/classic/*.json"]), algorithms,
                              seeds=args.seeds or [0], repeats=1 if args.repeats is None else args.repeats,
                              max_steps=args.max_steps,
                              measure_memory=args.memory, rule=rule,
                              include_collision_stats=args.collision_stats)]
        base = args.out or LOCAL_RESULTS / stamp
    outputs = [base / run.experiment if len(runs) > 1 else base for run in runs]
    if args.dry_run:
        preview = {"plan": args.plan, "plots": not args.no_plot,
                   "experiments": [{**run.settings(), "output_dir": str(out.resolve())}
                                   for run, out in zip(runs, outputs)]}
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return
    for run, out in zip(runs, outputs):
        total = run.expected_rows
        run.run_all(lambda done, n: print(f"\r{run.experiment}: {done}/{n}", end="", flush=True))
        print(f"\r{run.experiment}: {total}/{total} -> {write_outputs(run, out, plot=not args.no_plot)}")


if __name__ == "__main__":
    main()
