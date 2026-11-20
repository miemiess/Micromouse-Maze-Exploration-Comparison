"""事后分析（看过测试结果之后做的，不是正式结论）：按地图来源分层的开发集重新调参。

背景：正式流程的开发集只有生成图，选出的 c = 2.5 在外部迷宫库上失效（Docs/Result.md 4.5）。
本脚本检验：若开发集也包含外部迷宫库的地图，调参能否避开这个问题。
外部迷宫库的全部地图此前都已作为测试集使用过，因此这里的“留出集”并非从未见过的数据，
结果只能作为事后分析报告，正式结论仍以实验 1 与冻结的 c = 2.5 为准。

规则（运行前确定）：
    - 划分：外部迷宫库按 maze_id 排序，用 random.Random(2026) 抽取 20% 作为开发集，其余为留出集；
    - 开发集 = 原开发集（种子 101～110 的 120 张生成图）+ 抽出的外部图；
    - 候选 c：0、0.25、0.5、1、1.5、2、2.5、3（c = 0 即不加惩罚）；柱子规则保持开启；
    - 选取标准：开发集全部地图“步数 / 最短路”均值最低，相差不到 0.001 时取较小值（与正式流程相同）；
    - 留出集 = 其余外部图 + 实验 1 的 120 张生成测试图；比较重新选出的 c、原 c = 2.5 与重复 A*。

运行（项目根目录）：python results/standard/dev/posthoc_stratified.py
输出：同目录 posthoc.md。
"""

import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from algorithm_api import run_episode  # noqa: E402
from bfs import BfsPlanner  # noqa: E402
from environment import Maze  # noqa: E402
from prior_astar import FROZEN_SCALE, _PriorAStar  # noqa: E402
from repeated_astar import RepeatedAStarStrategy  # noqa: E402
from run_experiments import DEV_SEEDS, PLAN_SEEDS, _plan_maps, expand_maps  # noqa: E402

SPLIT_SEED = 2026
DEV_FRACTION = 0.2
CANDIDATES = (0, 0.25, 0.5, 1, 1.5, 2, 2.5, 3)


def variant(scale: float):
    """柱子规则开启、自适应惩罚系数为 scale 的先验增强重复 A*。"""
    return type("Variant", (_PriorAStar,), {"name": "variant", "use_post_rule": True,
                                            "penalty_scale": scale})


def ratios(cls, mazes, shortest) -> dict[str, float]:
    """每张地图的“步数 / 最短路”。"""
    out = {}
    for maze in mazes:
        result = run_episode(maze, cls())
        assert result["status"] == "success", (maze.maze_id, result["status"])
        out[maze.maze_id] = result["steps"] / shortest[maze.maze_id]
    return out


def describe(values: dict[str, float], ids) -> str:
    """均值（中位数）。"""
    data = [values[i] for i in ids]
    return f"{statistics.mean(data):.3f}（{statistics.median(data):.3f}）"


def main():
    external = sorted(expand_maps(["mazes/classic/external_*.json"]), key=lambda p: p.stem)
    rng = random.Random(SPLIT_SEED)
    dev_ext = set(rng.sample(external, round(len(external) * DEV_FRACTION)))
    hold_ext = [p for p in external if p not in dev_ext]

    load = lambda paths: [Maze.from_json(p) for p in paths]  # noqa: E731
    dev_gen, dev_ext_m = load(_plan_maps(DEV_SEEDS)), load(sorted(dev_ext, key=lambda p: p.stem))
    test_gen, hold_ext_m = load(_plan_maps(PLAN_SEEDS)), load(hold_ext)
    dev, hold = dev_gen + dev_ext_m, hold_ext_m + test_gen
    shortest = {m.maze_id: run_episode(m, BfsPlanner())["steps"] for m in dev + hold}
    ids = lambda mazes: [m.maze_id for m in mazes]  # noqa: E731

    lines = ["# 事后分析：按地图来源分层的开发集", "",
             "> **看过测试结果之后做的分析，不是正式结论。** 外部迷宫库的全部地图此前都作为测试集使用过，"
             "这里的留出集并非从未见过的数据；正式结论以实验 1 与冻结的 c = 2.5 为准。规则见本目录 "
             "`posthoc_stratified.py` 的说明。", "",
             f"- 开发集：{len(dev_gen)} 张生成图（种子 {DEV_SEEDS[0]}～{DEV_SEEDS[-1]}）+ {len(dev_ext_m)} 张外部迷宫库地图"
             f"（按 maze_id 排序后用 random.Random({SPLIT_SEED}) 抽取 {DEV_FRACTION:.0%}）",
             f"- 留出集：其余 {len(hold_ext_m)} 张外部迷宫库地图 + {len(test_gen)} 张生成测试图（实验 1 的种子 1～10）",
             "", "## 在分层开发集上调参", "",
             "| c | 开发集全部 | 其中生成图 | 其中外部图 |", "| --- | --- | --- | --- |"]
    scores = []
    for c in CANDIDATES:
        r = ratios(variant(c), dev, shortest)
        mean = statistics.mean(r.values())
        scores.append((round(mean, 3), c))
        lines.append(f"| {c} | {describe(r, ids(dev))} | {describe(r, ids(dev_gen))} | {describe(r, ids(dev_ext_m))} |")
    chosen = min(scores)[1]
    lines += ["", f"选定：c = {chosen}（原正式流程只用生成图选出 c = {FROZEN_SCALE}）", ""]

    lines += ["## 在留出集上评估", "",
              "均值（中位数）；+ / − 为与重复 A* 逐张比较步数更少 / 更多的地图数。", "",
              "| 方法 | 留出集全部 | 外部图 | 生成图 | 外部图 + / − |", "| --- | --- | --- | --- | --- |"]
    base = ratios(RepeatedAStarStrategy, hold, shortest)
    rows = [("重复 A*", base)]
    for label, c in ((f"分层调参 c = {chosen}", chosen), (f"原冻结 c = {FROZEN_SCALE}", FROZEN_SCALE)):
        rows.append((label, ratios(variant(c), hold, shortest)))
    for label, r in rows:
        ext_ids = ids(hold_ext_m)
        better = sum(r[i] < base[i] for i in ext_ids)
        worse = sum(r[i] > base[i] for i in ext_ids)
        lines.append(f"| {label} | {describe(r, ids(hold))} | {describe(r, ext_ids)} | "
                     f"{describe(r, ids(test_gen))} | {better} / {worse} |")
    lines += ["", "开发集抽出的外部迷宫库地图：" + "、".join(sorted(m.maze_id for m in dev_ext_m)), ""]

    out = Path(__file__).with_name("posthoc.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out, "chosen c =", chosen)


if __name__ == "__main__":
    main()
