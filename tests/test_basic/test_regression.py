"""基础规则回归测试：公共接口层（src/core/）或任何改动之后，基础规则的结果必须不变。

从已提交的正式结果 results/basic/main/runs.csv 中按固定种子抽取一批运行，重新执行，
要求状态、步数、转向次数与记录完全相同（计时会随机器变化，不比较）。
扩展开发（src/ext/）修改公共接口时，以这条测试作为“没有影响基础规则”的证据。
"""

import csv
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from core.algorithm_api import Maze, discover_algorithms, run_episode  # noqa: E402

RUNS = ROOT / "results" / "basic" / "main" / "runs.csv"
SAMPLE = 120


class BasicRegressionTests(unittest.TestCase):
    def test_recorded_runs_reproduce(self):
        """抽样重跑实验 1 的记录，逐项比较状态、步数与转向次数。"""
        with RUNS.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 6682)
        infos, errors = discover_algorithms()
        self.assertEqual(errors, [])
        for row in random.Random(2026).sample(rows, SAMPLE):
            with self.subTest(maze=row["maze_id"], algorithm=row["algorithm"]):
                maze = Maze.from_json(ROOT / "mazes" / "classic" / f"{row['maze_id']}.json")
                result = run_episode(maze, infos[row["algorithm"]].create(), seed=int(row["seed"]))
                self.assertEqual((result["status"], str(result["steps"]), str(result["turns_90"])),
                                 (row["status"], row["steps"], row["turns_90"]))


if __name__ == "__main__":
    unittest.main()
