"""C2 开发集调参（基础规则）：只在开发集（种子 101～110 生成的 120 张地图）上扫描惩罚参数，结果写入 results/basic/dev/tuning.md。

选取标准（实验计划第 4 节，运行前确定）：开发集“步数 / 最短路”均值最低；相差不到 0.001 时取较小值。
选定的值写入 src/basic/algorithms/prior_astar.py 的 FROZEN_SCALE、FROZEN_FIXED 后冻结。本脚本不读取测试集。

运行（项目根目录）：python src/basic/dev_tuning.py
"""

import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # src/basic/<本文件> → 项目根目录
sys.path.insert(0, str(ROOT / "src"))
OUT_DIR = ROOT / "results" / "basic" / "dev"
from basic.algorithms.bfs import BfsPlanner  # noqa: E402
from core.algorithm_api import run_episode  # noqa: E402
from core.environment import Maze  # noqa: E402
from basic.algorithms.prior_astar import _PriorAStar  # noqa: E402
from basic.plan import DEV_SEEDS, plan_maps  # noqa: E402

SCALES = (0.5, 1, 1.5, 2, 2.5, 3, 4, 5)
FIXED = (0, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3)


def variant(**attrs):
    """临时变体：柱子规则开启（开发集上开关它不影响结果，见 tuning.md），只改惩罚参数。"""
    return type("Variant", (_PriorAStar,), {"name": "variant", "use_post_rule": True, **attrs})


def evaluate(cls, mazes, shortest):
    """返回（全部比值, 按环路比例分组的比值, 每张图的步数）。"""
    ratios, by_loop, steps = [], defaultdict(list), {}
    for maze in mazes:
        result = run_episode(maze, cls())
        assert result["status"] == "success", (maze.maze_id, result["status"])
        ratio = result["steps"] / shortest[maze.maze_id]
        ratios.append(ratio)
        by_loop[round(maze.metadata["loop_fraction"] * 100)].append(ratio)
        steps[maze.maze_id] = result["steps"]
    return ratios, by_loop, steps


def main():
    mazes = [Maze.from_json(path) for path in plan_maps(DEV_SEEDS)]  # 缺失时提示生成命令
    shortest = {m.maze_id: run_episode(m, BfsPlanner())["steps"] for m in mazes}
    _, _, base_steps = evaluate(variant(unknown_penalty=0.0), mazes, shortest)

    lines = ["# C2 开发集调参记录", "",
             f"开发集：种子 {DEV_SEEDS[0]}～{DEV_SEEDS[-1]}，4 种生成器 × 环路 0 / 10 / 30%，共 {len(mazes)} 张。"
             "“更好 / 更差”与 δ = 0（即重复 A*）逐张比较步数。", ""]
    best = {}
    for title, key, values in (("自适应惩罚 δ = c · p / (1 − p)", "penalty_scale", SCALES),
                               ("固定惩罚 δ", "unknown_penalty", FIXED)):
        lines += [f"## {title}", "", "| 参数 | 均值 | 中位数 | 更好 | 更差 | 无环 | 10% 环路 | 30% 环路 |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        scores = []
        for value in values:
            attrs = {key: value} if key == "penalty_scale" else {key: value, "penalty_scale": None}
            ratios, by_loop, steps = evaluate(variant(**attrs), mazes, shortest)
            mean = statistics.mean(ratios)
            scores.append((round(mean, 3), value))
            better = sum(steps[k] < base_steps[k] for k in steps)
            worse = sum(steps[k] > base_steps[k] for k in steps)
            groups = " | ".join(f"{statistics.mean(by_loop[g]):.3f}" for g in (0, 10, 30))
            lines.append(f"| {value} | {mean:.3f} | {statistics.median(ratios):.3f} | {better} | {worse} | {groups} |")
        best[key] = min(scores)[1]
        lines += ["", f"选定：{best[key]}", ""]

    lines += ["## 柱子规则", "",
              "开发集上开、关柱子规则，120 张地图的路线完全相同（规则在 10% / 30% 环路图上常被观测推翻而自动关闭；"
              "在无环图上虽然推断出软墙，但没有改变任何一次决策，原因见 Docs/basic/algorithm-design.md）。", ""]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "tuning.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out, best)


if __name__ == "__main__":
    main()
