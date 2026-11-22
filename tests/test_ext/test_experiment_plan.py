"""扩展实验计划的命令行接入：--dry-run 预览与实际导出一致、正式计划不能被命令行覆盖。

地图划分与计划内容的检查见 test_plan.py；这里把地图换成 4×5 的固定小迷宫，只验证命令行流程。
"""

import csv
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.experiments import main  # noqa: E402
from ext.plan import NOISE_ALGORITHMS, NOISE_RULES, NOISE_SEEDS, TURN_RULES  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "turn_cost_tradeoff.json"


class ExperimentPlanCliTests(unittest.TestCase):
    def test_noise_preview_matches_exports(self):
        with TemporaryDirectory() as tmp, patch("ext.plan._paths", return_value=[FIXTURE]):
            base = Path(tmp) / "preview"
            args = ["--plan", "ext_noise", "--out", str(base), "--no-plot"]
            output = io.StringIO()
            with redirect_stdout(output):
                main([*args, "--dry-run"])
            self.assertFalse(base.exists())                       # 预览不运行、不写文件
            experiments = json.loads(output.getvalue())["experiments"]
            self.assertEqual([item["experiment"] for item in experiments], list(NOISE_RULES))
            main(args)
            for settings, spec in zip(experiments, NOISE_RULES.values()):
                folder = Path(settings.pop("output_dir"))
                metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
                self.assertEqual(settings, {k: metadata[k] for k in settings})
                self.assertEqual(metadata["rule"]["spec"], spec)
                with (folder / "runs.csv").open(encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    self.assertEqual(reader.fieldnames, settings["run_fields"])
                    rows = list(reader)
                self.assertEqual(len(rows), metadata["expected_rows"])
                self.assertEqual({row["algorithm"] for row in rows}, set(NOISE_ALGORITHMS))
                self.assertEqual({int(row["seed"]) for row in rows}, set(NOISE_SEEDS))

    def test_turn_preview_lists_all_rules(self):
        output = io.StringIO()
        with patch("ext.plan._paths", return_value=[FIXTURE]), redirect_stdout(output):
            main(["--plan", "ext_turn", "--dry-run"])
        experiments = json.loads(output.getvalue())["experiments"]
        self.assertEqual([e["rule"]["spec"].split(":")[0] for e in experiments],
                         [spec.split(":")[0] for spec in TURN_RULES.values()])

    def test_plan_rejects_overrides(self):
        for flag, value in (("--maps", str(FIXTURE)), ("--seeds", "7"), ("--repeats", "1"), ("--rule", "basic")):
            with self.subTest(flag=flag), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["--plan", "ext_turn", flag, value, "--dry-run"])


if __name__ == "__main__":
    unittest.main()
