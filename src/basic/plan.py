"""基础规则的实验计划（规则见 Docs/basic/experiment-plan.md，运行前确定、之后冻结）。

实验 1（main）：外部迷宫库全部地图（external_*）+ 120 张测试集生成地图，13 个算法
    （9 个已有算法 + C2 新方案 prior_astar 及其 3 个消融变体）；
实验 2（randomness）：3 张核心地图，随机游走 10 个种子。
开发集（种子 101～110 的 120 张生成地图）只用于 C2 调参（src/basic/dev_tuning.py），不进入任何实验。

运行：python src/run_experiments.py --plan basic   → results/basic/main、results/basic/randomness
"""

from pathlib import Path

from core.experiments import MAZE_DIR, ExperimentRun, expand_maps

PLAN_GENERATORS = ("backtracker", "wilson", "prim", "kruskal")
PLAN_LOOPS = (0, 10, 30)
PLAN_SEEDS = range(1, 11)    # 测试集
DEV_SEEDS = range(101, 111)  # 开发集：只用于调参，不进入任何实验
CORE_MAPS = ("1stworld", "japan2017ef", "uk2011f")
# 实验 1 的 13 个算法（固定列出，新增算法文件不会改变实验 1）。
MAIN_ALGORITHMS = ["astar", "bfs", "dfs", "flood_fill", "greedy_dfs", "random_walk",
                   "repeated_astar", "wall_follower_left", "wall_follower_right",
                   "prior_astar", "prior_astar_no_penalty", "prior_astar_no_post", "prior_astar_fixed"]


def plan_generated_names(seeds=PLAN_SEEDS) -> list[str]:
    """计划规定的生成地图文件名（默认为测试集 120 张；命名规则见 mazes/README.md）。"""
    return [f"gen_{generator}_16x16_s{seed}" + (f"_l{loop}" if loop else "") + ".json"
            for generator in PLAN_GENERATORS for loop in PLAN_LOOPS for seed in seeds]


def plan_maps(seeds=PLAN_SEEDS) -> list[Path]:
    """计划规定的生成地图路径；缺失时给出生成命令。"""
    generated = [MAZE_DIR / name for name in plan_generated_names(seeds)]
    missing = [p.name for p in generated if not p.exists()]
    if missing:
        raise SystemExit(f"缺少 {len(missing)} 张计划地图（如 {missing[0]}），请先运行：\n"
                         "python tools/MazesTest/maze_app.py --generate backtracker wilson prim kruskal "
                         f"--loops 0 10 30 --seeds {seeds[0]} {seeds[-1]}")
    return generated


def test_maps() -> list[Path]:
    """测试集：外部迷宫库全部地图 + 120 张测试集生成地图。"""
    return expand_maps(["mazes/classic/external_*.json"]) + plan_maps(PLAN_SEEDS)


def build_plan() -> list[ExperimentRun]:
    """基础规则的全部正式实验。"""
    core = expand_maps([f"mazes/classic/external_{n}.json" for n in CORE_MAPS])
    return [
        ExperimentRun(test_maps(), MAIN_ALGORITHMS, seeds=[0], repeats=3, experiment="main"),
        ExperimentRun(core, ["random_walk"], seeds=list(range(10)), experiment="randomness"),
    ]


# 计划注册：core.experiments 通过它找到 --plan basic，结果写到 results/basic/。
PLANS = {"basic": (build_plan, "basic")}
