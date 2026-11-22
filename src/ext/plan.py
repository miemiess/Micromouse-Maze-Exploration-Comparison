"""扩展阶段的实验计划（规则见 Docs/ext/experiment-plan.md，运行前确定、之后冻结）。

地图划分（按地图来源分层，固定种子，写入 mazes/splits/ext_dev.json）：
    - 开发集 = 120 张开发生成图（种子 101～110，基础阶段已作开发集）+ 外部迷宫库按 maze_id 排序后
      用 random.Random(2026) 抽取的 20%；只用于调试和观察，不进入任何正式实验；
    - 测试集 = 其余外部迷宫库地图 + 120 张测试生成图（种子 1～10）；
    - 噪声子集 = 测试集中全部 120 张生成图 + 外部测试图按 maze_id 排序后用 random.Random(2027) 抽取的 80 张
      （噪声实验每局较慢，且要多种子重复）。
实验：
    X1 turn：转弯代价 λ = 0.5、1、2、4 与运动时间模型，各一个子实验，10 个探索算法；
    X2 noise：噪声观测三档准确率 + 理想观测对照，置信度重规划及其消融，5 个种子。
运行：
    python src/run_experiments.py --plan ext_turn    → results/ext/turn/<子实验>/（约 15 分钟）
    python src/run_experiments.py --plan ext_noise   → results/ext/noise/<子实验>/（约 30 分钟）
"""

import json
import random
from pathlib import Path

from basic.plan import DEV_SEEDS, PLAN_SEEDS, plan_maps
from core.experiments import ExperimentRun, expand_maps
from core.rules import BASIC, parse_rule

ROOT = Path(__file__).resolve().parents[2]
SPLIT_FILE = ROOT / "mazes" / "splits" / "ext_dev.json"
SPLIT_SEED, DEV_FRACTION = 2026, 0.2
NOISE_SEED, NOISE_EXTERNAL = 2027, 80

# X1：基础算法（“不懂规则”的对照，按基础阶段实验 1 选取，去掉对称的右手沿墙、随机游走与消融变体）+ E3 扩展算法
TURN_ALGORITHMS = ["dfs", "flood_fill", "greedy_dfs", "repeated_astar", "wall_follower_left", "prior_astar",
                   "turn_aware_astar", "turn_aware_astar_w2", "dstar_lite", "frontier"]
TURN_RULES = {"lambda_0.5": "turn_cost:weight=0.5", "lambda_1": "turn_cost:weight=1",
              "lambda_2": "turn_cost:weight=2", "lambda_4": "turn_cost:weight=4", "motion_time": "motion_time"}
# X2：唯一支持噪声的探索算法及其消融；ideal 为理想观测（基础规则）下的同一算法，作为上限对照
NOISE_ALGORITHMS = ["belief_astar", "belief_astar_naive"]
NOISE_RULES = {"ideal": "basic",
               "high": "noisy_sensor:p_front=0.95,p_side=0.9,p_back=0.85",
               "mid": "noisy_sensor:p_front=0.9,p_side=0.8,p_back=0.7",
               "low": "noisy_sensor:p_front=0.8,p_side=0.7,p_back=0.6"}
NOISE_SEEDS = list(range(5))


def split() -> dict[str, list[str]]:
    """按计划规则计算地图划分：{"dev": [...], "test": [...], "noise": [...]}（maze_id，已排序）。"""
    external = sorted(p.stem for p in expand_maps(["mazes/classic/external_*.json"]))
    dev_ext = set(random.Random(SPLIT_SEED).sample(external, round(len(external) * DEV_FRACTION)))
    test_ext = [m for m in external if m not in dev_ext]
    gen_test = sorted(p.stem for p in plan_maps(PLAN_SEEDS))
    noise_ext = random.Random(NOISE_SEED).sample(test_ext, NOISE_EXTERNAL)
    return {"dev": sorted([p.stem for p in plan_maps(DEV_SEEDS)] + list(dev_ext)),
            "test": sorted(test_ext + gen_test),
            "noise": sorted(gen_test + noise_ext)}


def write_split() -> Path:
    """把划分写入 mazes/splits/ext_dev.json（供人查看；正式实验以 split() 的计算为准，测试检查两者一致）。"""
    SPLIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"rule": "见 src/ext/plan.py 与 Docs/ext/experiment-plan.md", **split()}
    SPLIT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return SPLIT_FILE


def _paths(ids: list[str]) -> list[Path]:
    return [ROOT / "mazes" / "classic" / f"{maze_id}.json" for maze_id in ids]


def build_turn() -> list[ExperimentRun]:
    """X1：转弯代价各档 λ 与运动时间模型，测试集，计时重复 3 次取中位数。"""
    maps = _paths(split()["test"])
    return [ExperimentRun(maps, TURN_ALGORITHMS, seeds=[0], repeats=3, experiment=name, rule=parse_rule(spec))
            for name, spec in TURN_RULES.items()]


def build_noise() -> list[ExperimentRun]:
    """X2：噪声观测三档准确率 + 理想观测对照，噪声子集，5 个种子。"""
    maps = _paths(split()["noise"])
    return [ExperimentRun(maps, NOISE_ALGORITHMS, seeds=NOISE_SEEDS, experiment=name,
                          rule=BASIC if spec == "basic" else parse_rule(spec))
            for name, spec in NOISE_RULES.items()]


# 计划注册：core.experiments 通过它找到 --plan，结果写到 results/ext/<目录>/<子实验>/。
PLANS = {"ext_turn": (build_turn, "ext/turn"), "ext_noise": (build_noise, "ext/noise")}

if __name__ == "__main__":
    print(write_split())
