"""事后验证（看过 X2、X3 结果之后做的，不是冻结计划的一部分）：检验报告 3.8 节发现 11、12 的解释。

正式结论仍以冻结计划与 results/ext/analysis/report.md 为准；这里只检验“为什么”。

divisor —— 发现 12：两阶段成绩中探索折算系数 D 改变时，ε > 0 是否划算、有界提前停止是否仍优于到达即停。
    成绩 = 冲刺代价 + 探索代价（含返回）/ D。算法的停止判据只取决于 ε，不读 D，
    因此直接用 X3 的 runs.csv 重算成绩，结果与重新运行完全相同（脚本先核对 D = 30 时与原成绩一致）。

contact —— 发现 11：噪声下置信度融合为何没有优势。
    假设 A：撞墙给出确定的接触反馈，替代了累积证据的作用。
        检验：去掉“撞到即确定有墙”（撞墙后只得到普通的噪声读数），比较融合与只信最近读数。
        若假设成立，去掉后融合应显著优于只信最近读数。
    假设 B：低准确率下融合把真实通路累积成“更可能有墙”，乐观地图断开，频繁退回“只把确定的墙当墙”
        的兜底规划，兜底路线无视全部读数而撞墙更多。
        检验：统计兜底规划次数、发生在兜底路线上的撞墙数，以及结束时被误判为墙的通路数。
    地图与噪声档与 X2 相同（噪声子集 200 张，高 / 中 / 低三档）。有接触反馈的两个变体用种子 0～4，
    先核对它们的步数、撞墙次数与 X2 的 runs.csv 逐条一致；无接触反馈的两个变体常常耗尽动作预算、每局很慢，
    只用种子 0。不设计算时间上限（30 秒上限在多进程并行时取决于机器负载，结果不可复现），
    每局由动作预算（20 × 格子数）结束。

soft —— 发现 11 的改进：belief_astar_soft（兜底规划按置信度给可疑的边加代价 K · e^S）。
    K 在开发集（mazes/splits/ext_dev.json 的 199 张地图，三档噪声 × 种子 0～4）上按“步数 / 最短路”均值选定，
    相差不到 0.001 取较小的 K；之后冻结，在 X2 的噪声子集（200 张 × 种子 0～4）上与 belief_astar、
    belief_astar_naive 配对比较（后两者直接读取 X2 的 runs.csv）。

运行（项目根目录）：
    python src/ext/posthoc.py divisor     → results/ext/posthoc/divisor.md
    python src/ext/posthoc.py contact     → results/ext/posthoc/contact.md、contact_runs.csv
    python src/ext/posthoc.py soft        → results/ext/posthoc/soft.md、soft_runs.csv
"""

import argparse
import csv
import os
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from core.environment import Observation  # noqa: E402
from ext.analysis import paired, verdict  # noqa: E402
from ext.algorithms.belief_astar import BeliefAStarNaive, BeliefAStarStrategy  # noqa: E402

RESULTS = ROOT / "results" / "ext"
OUT = RESULTS / "posthoc"
HEADER = ("> **事后验证，不是冻结计划的一部分。** 设计与运行在看过正式结果之后，只用来检验报告 3.8 节的解释；"
          "正式结论以 `results/ext/analysis/report.md` 为准。由 `python src/ext/posthoc.py` 生成。")


def fmt(result: dict) -> str:
    g = result
    return f"{g['wins']}/{g['losses']}/{g['ties']}（p = {g['p']:.3g}）"


# --------------------------------------------------------------------------- divisor
DIVISORS = (1, 2, 4, 6, 8, 10, 15, 20, 30, 60, 100)
BOUNDED = ("bounded_explore_e0", "bounded_explore_e10", "bounded_explore_e25")
ARRIVE = ("repeated_astar", "flood_fill", "turn_aware_astar")


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rescore(rows: list[dict], divisor: float) -> list[dict]:
    out = []
    for r in rows:
        if r["status"] == "success":
            r = dict(r, score=float(r["sprint_cost"]) + float(r["explore_cost"]) / divisor)
        out.append(r)
    return out


def divisor_report() -> Path:
    lines = ["# 事后验证：探索折算系数 D 与 ε（发现 12）", "", HEADER, "",
             "成绩 = 冲刺代价 + 探索代价（含返回起点）/ D。正式实验 D = 30。表中为测试集 435 张的均值，"
             "配对比较为“前者 vs 后者”的胜 / 负 / 平（成绩更低记胜）与双侧符号检验，结论按计划第 5 节（两组方向一致）判定。", ""]
    for name in ("steps", "lambda_2"):
        rows = load(RESULTS / "two_phase" / name / "runs.csv")
        for r in rows:          # 核对：D = 30 重算的成绩与原成绩一致
            if r["status"] == "success":
                assert abs(float(r["sprint_cost"]) + float(r["explore_cost"]) / 30 - float(r["total_score"])) < 1e-3, r
        algs = ARRIVE + BOUNDED
        lines += [f"## {name}", "", "| D | " + " | ".join(algs) + " | 最好 |", "| --- " * (len(algs) + 2) + "|"]
        pair_lines = ["", "| D | e10 vs e0 | e25 vs e0 | e0 vs repeated_astar | e0 vs repeated_astar 结论 |",
                      "| --- | --- | --- | --- | --- |"]
        for d in DIVISORS:
            data = rescore(rows, d)
            means = {a: statistics.mean(r["score"] for r in data if r["algorithm"] == a and "score" in r) for a in algs}
            best = min(means, key=means.get)
            lines.append(f"| {d} | " + " | ".join(f"{means[a]:.2f}" for a in algs) + f" | {best} |")
            p10 = paired(data, "bounded_explore_e10", "bounded_explore_e0", "score")
            p25 = paired(data, "bounded_explore_e25", "bounded_explore_e0", "score")
            pra = paired(data, "bounded_explore_e0", "repeated_astar", "score")
            pair_lines.append(f"| {d} | {fmt(p10['ALL'])}，{verdict(p10)} | {fmt(p25['ALL'])}，{verdict(p25)} | "
                              f"{fmt(pra['ALL'])} | {verdict(pra)} |")
        # 均值意义下的盈亏点：mean(e) − mean(e0) = Δsprint + Δexplore / D = 0
        def mean_of(a, key):
            return statistics.mean(float(r[key]) for r in rows if r["algorithm"] == a and r["status"] == "success")
        lines += pair_lines + [""]
        for a in ("bounded_explore_e10", "bounded_explore_e25"):
            ds = mean_of(a, "sprint_cost") - mean_of("bounded_explore_e0", "sprint_cost")
            de = mean_of(a, "explore_cost") - mean_of("bounded_explore_e0", "explore_cost")
            lines.append(f"- {a} 相对 e0：冲刺 +{ds:.2f}，探索 {de:+.2f}；均值盈亏点 D = {-de / ds:.1f}"
                         "（D 小于它时 ε > 0 的平均成绩更好）")
        ds = mean_of("repeated_astar", "sprint_cost") - mean_of("bounded_explore_e0", "sprint_cost")
        de = mean_of("repeated_astar", "explore_cost") - mean_of("bounded_explore_e0", "explore_cost")
        lines += [f"- repeated_astar（到达即停）相对 e0：冲刺 +{ds:.2f}，探索 {de:+.2f}；均值盈亏点 D = {-de / ds:.1f}"
                  "（D 小于它时到达即停的平均成绩更好）", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "divisor.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- contact
LEVELS = {"high": "noisy_sensor:p_front=0.95,p_side=0.9,p_back=0.85",
          "mid": "noisy_sensor:p_front=0.9,p_side=0.8,p_back=0.7",
          "low": "noisy_sensor:p_front=0.8,p_side=0.7,p_back=0.6"}
SEEDS = range(5)
NOCONTACT_SEEDS = (0,)


class _Probe:
    """给置信度重规划加诊断：撞墙是否发生在兜底路线上；可选去掉接触反馈。"""

    use_contact = True

    def reset(self, **kwargs):
        super().reset(**kwargs)
        self.on_fallback = False
        self.pending = None                   # 上一步尝试的方向及当时是否走兜底路线
        self.fallback_collisions = 0

    def choose_direction(self, observation):
        contact = getattr(observation, "collision_wall", None)
        if contact is not None and self.pending and self.pending[0] == contact and self.pending[1]:
            self.fallback_collisions += 1
        if not self.use_contact and contact is not None:
            observation = Observation(observation.position, observation.heading, observation.walls,
                                      observation.step_count)       # 只剩普通的噪声读数
        before = (self.replans, self.fallbacks)
        direction = super().choose_direction(observation)
        if self.replans != before[0]:
            self.on_fallback = self.fallbacks != before[1]
        self.pending = (direction, self.on_fallback)
        return direction

    def false_walls(self, maze) -> int:
        """结束时被判为“更可能有墙”（S > 0）但实际是通路的边数。"""
        return sum(1 for edge, s in self.score.items() if s > 0 and edge not in maze.walls)


def _variant(base, name, use_contact):
    return type(name, (_Probe, base), {"name": name, "use_contact": use_contact})


VARIANTS = {"belief_astar": _variant(BeliefAStarStrategy, "belief_astar", True),
            "belief_astar_naive": _variant(BeliefAStarNaive, "belief_astar_naive", True),
            "belief_nocontact": _variant(BeliefAStarStrategy, "belief_nocontact", False),
            "naive_nocontact": _variant(BeliefAStarNaive, "naive_nocontact", False)}


def _job(args):
    level, maze_id, seed, variant = args
    from core.algorithm_api import Runner
    from core.environment import Maze
    from core.rules import parse_rule
    maze = Maze.from_json(ROOT / "mazes" / "classic" / f"{maze_id}.json")
    algo = VARIANTS[variant]()
    runner = Runner(maze, algo, seed=seed, time_budget=float("inf"), rule=parse_rule(LEVELS[level]))
    runner.run()
    s = runner.summary()
    return {"experiment": level, "maze_id": maze_id, "seed": seed, "algorithm": variant, "status": s["status"],
            "steps": s["steps"], "actions": s.get("actions", ""), "collisions": s.get("collisions", ""),
            "replans": algo.replans, "fallback_plans": algo.fallbacks,
            "fallback_collisions": algo.fallback_collisions, "false_walls": algo.false_walls(maze)}


INT_FIELDS = ("seed", "steps", "actions", "collisions", "replans", "fallback_plans", "fallback_collisions",
              "false_walls")


def _share(rows, part, whole) -> str:
    if any(r[part] is None or r[whole] is None for r in rows):
        return "—"
    return f"{sum(r[part] for r in rows) / max(1, sum(r[whole] for r in rows)):.1%}"


def contact_report(workers: int, variants=None) -> Path:
    """运行 variants（默认全部）并替换 contact_runs.csv 中这些变体的记录，再由整个 CSV 生成报告。"""
    from ext.plan import split
    variants = list(variants or VARIANTS)
    noise = split()["noise"]
    shortest, reference = {}, {}
    for level in LEVELS:
        for r in load(RESULTS / "noise" / level / "runs.csv"):
            shortest[r["maze_id"]] = int(r["shortest"])
            reference[(level, r["maze_id"], int(r["seed"]), r["algorithm"])] = (r["steps"], r["collisions"])
    kept = []
    if (OUT / "contact_runs.csv").exists():
        kept = [r for r in load(OUT / "contact_runs.csv") if r["algorithm"] not in variants]
        for r in kept:
            for k in INT_FIELDS:
                r[k] = int(r[k]) if r[k] != "" else None   # 早期运行没有记录 replans / fallback_plans
    jobs = [(lv, m, s, v) for lv in LEVELS for m in noise for v in variants
            for s in (SEEDS if VARIANTS[v].use_contact else NOCONTACT_SEEDS)]
    jobs.sort(key=lambda j: VARIANTS[j[3]].use_contact)     # 慢的先跑，减少尾部等待
    with ProcessPoolExecutor(workers) as pool:
        rows = []
        for i, row in enumerate(pool.map(_job, jobs, chunksize=1), 1):
            rows.append(row)
            if i % 200 == 0 or i == len(jobs):
                print(f"{i}/{len(jobs)}", flush=True)
    rows = kept + rows
    mismatched = 0
    for r in rows:
        r["ratio"] = r["steps"] / shortest[r["maze_id"]]
        key = (r["experiment"], r["maze_id"], r["seed"], r["algorithm"])
        if key in reference and reference[key] != (str(r["steps"]), str(r["collisions"])):
            mismatched += 1
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "contact_runs.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    n_ref = sum(1 for r in rows if r["algorithm"] in ("belief_astar", "belief_astar_naive"))
    lines = ["# 事后验证：噪声下置信度融合为何没有优势（发现 11）", "", HEADER, "",
             f"与 X2 相同的 200 张地图；有接触反馈的变体用种子 0～4，无接触反馈的变体只用种子 0，不设计算时间上限。复现核对：融合与消融共 {n_ref} 次运行，"
             f"与 X2 的步数、撞墙次数不一致 {mismatched} 次。", "",
             "- `belief_astar` / `belief_astar_naive`：与 X2 相同（撞到的墙记为确定有墙）；",
             "- `belief_nocontact` / `naive_nocontact`：去掉接触反馈——撞墙后原地不动，只得到普通的噪声读数。", "",
             "## 各变体均值", "",
             "| 噪声 | 变体 | 成功率 | 步数 / 最短路 | 撞墙 | 兜底规划 / 重规划 | 兜底路线上的撞墙占比 | 结束时误判为墙的通路 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        for v in VARIANTS:
            sub = [r for r in rows if r["experiment"] == level and r["algorithm"] == v]
            ok = [r for r in sub if r["status"] == "success"]
            coll = sum(r["collisions"] for r in sub)
            lines.append(f"| {level} | {v} | {len(ok) / len(sub):.1%} | "
                         f"{statistics.mean(r['ratio'] for r in ok) if ok else float('nan'):.3f} | {statistics.mean(r['collisions'] for r in sub):.1f} | "
                         f"{_share(sub, 'fallback_plans', 'replans')} | "
                         f"{sum(r['fallback_collisions'] for r in sub) / max(1, coll):.1%} | "
                         f"{statistics.mean(r['false_walls'] for r in sub):.2f} |")
    lines += ["", "## 配对比较（融合 vs 只信最近读数；按（地图, 种子）配对，前者更好记胜）", "",
              "| 噪声 | 接触反馈 | 指标 | 全部 | 外部迷宫库 | 生成图 | 结论 |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        sub = [dict(r, seed=str(r["seed"]), status=r["status"]) for r in rows if r["experiment"] == level]
        for label, a, b in (("有", "belief_astar", "belief_astar_naive"), ("无", "belief_nocontact", "naive_nocontact")):
            for metric, name in (("ratio", "步数比"), ("collisions", "撞墙"), ("false_walls", "误判为墙的通路")):
                res = paired(sub, a, b, metric)
                lines.append(f"| {level} | {label} | {name} | {fmt(res['ALL'])} | {fmt(res['external'])} | "
                             f"{fmt(res['generated'])} | {verdict(res)} |")
        ok_a = sum(r["status"] == "success" for r in sub if r["algorithm"] == "belief_nocontact")
        ok_b = sum(r["status"] == "success" for r in sub if r["algorithm"] == "naive_nocontact")
        n_nc = sum(1 for r in sub if r["algorithm"] == "belief_nocontact")
        lines.append(f"| {level} | 无 | 成功次数 | 融合 {ok_a} / 最近读数 {ok_b}（共 {n_nc}） | | | |")
    lines += ["", "## 撞墙分解（有接触反馈；融合 vs 只信最近读数，按（地图, 种子）配对，前者更小记胜）", "",
              "兜底占比 = 兜底规划次数 / 重规划次数；兜底路线上的撞墙 = 执行“只把确定的墙当墙”的路线时发生的撞墙；"
              "正常路线上的撞墙 = 其余撞墙。", "",
              "| 噪声 | 指标 | 融合均值 | 最近读数均值 | 全部 | 外部迷宫库 | 生成图 | 结论 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        sub = []
        for r in rows:
            if r["experiment"] == level and r["replans"] is not None:
                sub.append(dict(r, seed=str(r["seed"]), fb_share=r["fallback_plans"] / max(1, r["replans"]),
                                normal_collisions=r["collisions"] - r["fallback_collisions"]))
        for metric, name in (("fb_share", "兜底占比"), ("fallback_collisions", "兜底路线上的撞墙"),
                             ("normal_collisions", "正常路线上的撞墙")):
            res = paired(sub, "belief_astar", "belief_astar_naive", metric)
            a = res["ALL"]
            lines.append(f"| {level} | {name} | {a['mean_a']:.2f} | {a['mean_b']:.2f} | {fmt(a)} | "
                         f"{fmt(res['external'])} | {fmt(res['generated'])} | {verdict(res)} |")
    path = OUT / "contact.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- soft
SOFT_CANDIDATES = (0.25, 0.5, 1.0, 2.0, 4.0)


def _soft_job(args):
    level, maze_id, seed, scale = args
    from basic.algorithms.bfs import BfsPlanner
    from core.algorithm_api import Runner, run_episode
    from core.environment import Maze
    from core.rules import parse_rule
    from ext.algorithms.belief_astar import BeliefAStarSoft
    maze = Maze.from_json(ROOT / "mazes" / "classic" / f"{maze_id}.json")
    algo = type("Soft", (BeliefAStarSoft,), {"penalty_scale": scale})()
    runner = Runner(maze, algo, seed=seed, time_budget=float("inf"), rule=parse_rule(LEVELS[level]))
    runner.run()
    s = runner.summary()
    shortest = run_episode(maze, BfsPlanner())["steps"]
    return {"experiment": level, "maze_id": maze_id, "seed": str(seed), "algorithm": f"soft_{scale:g}",
            "status": s["status"], "steps": s["steps"], "shortest": shortest, "ratio": s["steps"] / shortest,
            "collisions": s.get("collisions", 0), "fallback_plans": algo.fallbacks, "replans": algo.replans}


def _run_pool(jobs, workers, fn):
    rows = []
    with ProcessPoolExecutor(workers) as pool:
        for i, row in enumerate(pool.map(fn, jobs, chunksize=4), 1):
            rows.append(row)
            if i % 500 == 0 or i == len(jobs):
                print(f"{i}/{len(jobs)}", flush=True)
    return rows


def soft_report(workers: int) -> Path:
    from ext.algorithms.belief_astar import BeliefAStarSoft
    from ext.plan import split
    parts = split()
    dev_rows = _run_pool([(lv, m, s, k) for lv in LEVELS for m in parts["dev"] for s in SEEDS
                          for k in SOFT_CANDIDATES], workers, _soft_job)
    lines = ["# 改进：按置信度加代价的兜底规划（belief_astar_soft）", "",
             "> **冻结计划之后新增的算法**（报告发现 11 提出的改进），不属于正式结论。K 只在开发集上选定，"
             "测试集只评估一次。由 `python src/ext/posthoc.py soft` 生成。", "",
             f"## 开发集选 K（{len(parts['dev'])} 张地图 × 三档噪声 × 种子 0～4；步数 / 最短路均值，撞墙为每局均值）", "",
             "| K | 成功率 | 步数 / 最短路 | 撞墙 | 高 | 中 | 低 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    scores = []
    for k in SOFT_CANDIDATES:
        sub = [r for r in dev_rows if r["algorithm"] == f"soft_{k:g}"]
        ok = [r for r in sub if r["status"] == "success"]
        mean = statistics.mean(r["ratio"] for r in ok)
        scores.append((round(mean, 3), k))
        per = [statistics.mean(r["ratio"] for r in ok if r["experiment"] == lv) for lv in LEVELS]
        lines.append(f"| {k:g} | {len(ok) / len(sub):.1%} | {mean:.3f} | "
                     f"{statistics.mean(r['collisions'] for r in sub):.1f} | " + " | ".join(f"{x:.3f}" for x in per) + " |")
    chosen = min(scores)[1]
    lines += ["", f"选定 K = {chosen:g}（`BeliefAStarSoft.penalty_scale` = {BeliefAStarSoft.penalty_scale:g}）。", ""]
    if chosen != BeliefAStarSoft.penalty_scale:
        lines += [f"**注意：类属性与开发集选定值不一致，应把 penalty_scale 改为 {chosen:g} 后重跑。**", ""]

    test_rows = _run_pool([(lv, m, s, chosen) for lv in LEVELS for m in parts["noise"] for s in SEEDS],
                          workers, _soft_job)
    for r in test_rows:
        r["algorithm"] = "belief_astar_soft"
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "soft_runs.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(dev_rows[0]) + ["split"])
        writer.writeheader()
        writer.writerows([dict(r, split="dev") for r in dev_rows] + [dict(r, split="test") for r in test_rows])

    lines += ["## 测试集（X2 的噪声子集 200 张 × 种子 0～4）", "",
              "| 噪声 | 算法 | 成功率 | 步数 / 最短路 | 撞墙 |", "| --- | --- | --- | --- | --- |"]
    compare = ["", "### 配对比较（belief_astar_soft vs 对照，按（地图, 种子）配对，前者更小记胜）", "",
               "| 噪声 | 对照 | 指标 | 全部 | 外部迷宫库 | 生成图 | 结论 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for level in LEVELS:
        x2 = [r for r in load(RESULTS / "noise" / level / "runs.csv")]
        mine = [dict(r, steps=str(r["steps"]), ratio=str(r["ratio"]), collisions=str(r["collisions"]))
                for r in test_rows if r["experiment"] == level]
        rows = x2 + mine
        for alg in ("belief_astar", "belief_astar_naive", "belief_astar_soft"):
            sub = [r for r in rows if r["algorithm"] == alg]
            ok = [r for r in sub if r["status"] == "success"]
            lines.append(f"| {level} | {alg} | {len(ok) / len(sub):.1%} | "
                         f"{statistics.mean(float(r['ratio']) for r in ok):.3f} | "
                         f"{statistics.mean(float(r['collisions']) for r in sub):.1f} |")
        for base in ("belief_astar", "belief_astar_naive"):
            for metric, name in (("ratio", "步数比"), ("collisions", "撞墙")):
                res = paired(rows, "belief_astar_soft", base, metric)
                compare.append(f"| {level} | {base} | {name} | {fmt(res['ALL'])} | {fmt(res['external'])} | "
                               f"{fmt(res['generated'])} | {verdict(res)} |")
    path = OUT / "soft.md"
    path.write_text("\n".join(lines + compare) + "\n", encoding="utf-8")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("divisor")
    s = sub.add_parser("soft")
    s.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    c = sub.add_parser("contact")
    c.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    c.add_argument("--variants", nargs="*", choices=list(VARIANTS),
                   help="只重跑这些变体，其余沿用 contact_runs.csv 中已有的记录")
    args = parser.parse_args(argv)
    if args.command == "divisor":
        print(divisor_report())
    elif args.command == "soft":
        print(soft_report(args.workers))
    else:
        print(contact_report(args.workers, args.variants))


if __name__ == "__main__":
    main()
