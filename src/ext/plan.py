"""E1/E3 代价对照与 E2 噪声实验，口径见 Docs/ext/experiment-plan.md。"""

import json

from basic.plan import DEV_SEEDS, PLAN_SEEDS, plan_maps
from core.experiments import MAZE_DIR, ROOT, ExperimentRun
from core.rules import parse_rule

SPLIT = ROOT / "mazes" / "splits" / "ext_dev.json"
ALGORITHMS = ("dfs", "flood_fill", "repeated_astar", "turn_aware_astar",
              "turn_aware_astar_w2", "dstar_lite", "frontier")
CONDITIONS = (
    ("baseline", "basic"),
    ("turn_cost", "turn_cost:weight=2"),
    ("motion_time", "motion_time:cell=0.18,v_max=0.5,accel=2,turn90=0.3,turn180=0.5"),
)


NOISE_ALGORITHMS = ("belief_astar", "belief_astar_naive")
NOISE_CONDITIONS = (
    ("perfect_sensor", "noisy_sensor:p_front=1,p_side=1,p_back=1"),
    ("default_sensor", "noisy_sensor:p_front=0.95,p_side=0.9,p_back=0.85"),
    ("stress_sensor", "noisy_sensor:p_front=0.9,p_side=0.8,p_back=0.7"),
)
NOISE_SEEDS = (0, 1, 2, 3, 4)


def map_splits():
    """按固定清单和生成种子返回彼此独立的开发与测试地图。"""
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    development = [MAZE_DIR / name for name in split["development_external"]] + plan_maps(DEV_SEEDS)
    test = [MAZE_DIR / name for name in split["test_external"]] + plan_maps(PLAN_SEEDS)
    all_maps = development + test
    if len(set(all_maps)) != len(all_maps):
        raise ValueError(f"扩展地图划分包含重复地图：{SPLIT}")
    missing = [path.name for path in all_maps if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"缺少扩展计划地图：{', '.join(missing)}")
    return development, test


def build_plan() -> list[ExperimentRun]:
    """三套代价条件使用相同的测试地图、算法、种子与运行预算。"""
    _, test_maps = map_splits()
    return [
        ExperimentRun(test_maps, list(ALGORITHMS), seeds=[0], repeats=3, experiment=name,
                      rule=parse_rule(spec), include_collision_stats=True)
        for name, spec in CONDITIONS
    ]


def build_noise_plan() -> list[ExperimentRun]:
    """在同一批地图和种子上比较置信度融合与只信最近读数。"""
    _, test_maps = map_splits()
    return [
        ExperimentRun(test_maps, list(NOISE_ALGORITHMS), seeds=NOISE_SEEDS, repeats=1,
                      experiment=name, rule=parse_rule(spec), include_collision_stats=True)
        for name, spec in NOISE_CONDITIONS
    ]


PLANS = {"ext": (build_plan, "ext"), "ext-noise": (build_noise_plan, "ext/noise")}
