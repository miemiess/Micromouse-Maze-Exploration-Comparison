"""扩展实验分析（src/ext/analysis.py）：符号检验、配对胜负与结论规则（计划第 5 节）。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ext.analysis import paired, sign_test, verdict  # noqa: E402


def rows(values: dict) -> list[dict]:
    """{(maze_id, 算法): 指标值} → runs.csv 风格的行。"""
    return [{"maze_id": m, "seed": "0", "algorithm": a, "status": "success", "x": str(v)}
            for (m, a), v in values.items()]


class AnalysisTests(unittest.TestCase):
    def test_sign_test(self):
        self.assertEqual(sign_test(0, 0), 1.0)
        self.assertAlmostEqual(sign_test(10, 0), 2 / 2 ** 10)
        self.assertAlmostEqual(sign_test(5, 5), 1.0)
        self.assertAlmostEqual(sign_test(1, 4), 2 * (1 + 5) / 32)

    def test_paired_counts_ties_and_groups(self):
        data = {}
        for i in range(10):
            data[(f"external_{i}", "a")] = 1.0
            data[(f"external_{i}", "b")] = 2.0
            data[(f"gen_{i}", "a")] = 1.0
            data[(f"gen_{i}", "b")] = 1.0 if i < 3 else 3.0
        result = paired(rows(data), "a", "b", "x")
        self.assertEqual((result["ALL"]["wins"], result["ALL"]["losses"], result["ALL"]["ties"]), (17, 0, 3))
        self.assertEqual(result["external"]["n"], 10)
        self.assertEqual(verdict(result), "更好")
        flipped = paired(rows(data), "a", "b", "x", lower_is_better=False)
        self.assertEqual(verdict(flipped), "更差")

    def test_verdict_requires_consistent_groups(self):
        data = {}
        for i in range(20):
            data[(f"external_{i}", "a")], data[(f"external_{i}", "b")] = 1.0, 2.0
        for i in range(8):
            data[(f"gen_{i}", "a")], data[(f"gen_{i}", "b")] = 2.0, 1.0
        self.assertEqual(verdict(paired(rows(data), "a", "b", "x")), "取决于地图来源")
        few = {("external_0", "a"): 1.0, ("external_0", "b"): 2.0}
        self.assertEqual(verdict(paired(rows(few), "a", "b", "x")), "无显著差异")

    def test_failed_runs_are_excluded(self):
        data = rows({("external_0", "a"): 1.0, ("external_0", "b"): 2.0})
        data[0]["status"] = "budget_exceeded"
        self.assertEqual(paired(data, "a", "b", "x")["ALL"]["n"], 0)


if __name__ == "__main__":
    unittest.main()
