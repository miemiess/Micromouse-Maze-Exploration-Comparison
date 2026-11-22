"""扩展计划的地图划分以及通过命令行导出的三套条件。"""

import csv
import io
from contextlib import redirect_stdout, redirect_stderr
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.experiments import main
from ext.plan import ALGORITHMS, CONDITIONS, NOISE_ALGORITHMS, NOISE_CONDITIONS, build_plan, map_splits

FIXTURE = Path(__file__).parent / "fixtures" / "turn_cost_tradeoff.json"


class ExperimentPlanTests(unittest.TestCase):
    def test_fixed_splits_and_conditions(self):
        development, test = map_splits()
        self.assertEqual((len(development), len(test)), (199, 435))
        self.assertFalse(set(development) & set(test))
        self.assertEqual(sum(path.name.startswith("external_") for path in development), 79)
        self.assertEqual(sum(path.name.startswith("external_") for path in test), 315)
        for run in build_plan():
            self.assertEqual(run.maze_paths, test)
            self.assertEqual(run.algorithms, list(ALGORITHMS))
            self.assertEqual((run.seeds, run.repeats), ([0], 3))
            self.assertEqual((run.rule.collision_limit, len(run.tasks())), (1, 3045))

    def test_cli_exports_all_conditions(self):
        with TemporaryDirectory() as tmp, patch("ext.plan.map_splits", return_value=([], [FIXTURE])):
            main(["--plan", "ext", "--out", tmp])
            for name, spec in CONDITIONS:
                folder = Path(tmp) / name
                with (folder / "runs.csv").open(encoding="utf-8") as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual([row["algorithm"] for row in rows], list(ALGORITHMS))
                self.assertTrue(all(row["consistent"] == "True" and row["status"] == "success"
                                    for row in rows))
                self.assertTrue(all(row["collisions"] == "0" and row["actions"] == row["steps"]
                                    for row in rows))
                metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
                self.assertEqual(metadata["rule"]["spec"], spec)
                self.assertEqual("rule_cost_ratio" in rows[0], name != "baseline")
                self.assertTrue((folder / "figures" / "success_by_group.png").exists())

    def test_noise_preview_matches_exports(self):
        with TemporaryDirectory() as tmp, patch("ext.plan.map_splits", return_value=([], [FIXTURE])):
            base = Path(tmp) / "preview"
            args = ["--plan", "ext-noise", "--out", str(base), "--no-plot"]
            output = io.StringIO()
            with redirect_stdout(output):
                main([*args, "--dry-run"])
            self.assertFalse(base.exists())
            experiments = json.loads(output.getvalue())["experiments"]
            self.assertEqual([item["experiment"] for item in experiments],
                             [name for name, _ in NOISE_CONDITIONS])
            main(args)
            for settings, (_, spec) in zip(experiments, NOISE_CONDITIONS):
                folder = Path(settings.pop("output_dir"))
                metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
                self.assertEqual(settings, {k: metadata[k] for k in settings})
                self.assertEqual(metadata["rule"]["spec"], spec)
                self.assertIsNone(metadata["rule"]["collision_limit"])
                with (folder / "runs.csv").open(encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    self.assertEqual(reader.fieldnames, settings["run_fields"])
                    rows = list(reader)
                self.assertEqual(len(rows), metadata["expected_rows"])
                self.assertEqual({row["algorithm"] for row in rows}, set(NOISE_ALGORITHMS))
                self.assertEqual({int(row["seed"]) for row in rows}, set(range(5)))

    def test_plan_rejects_map_seed_and_repeat_overrides(self):
        for flag, value in (("--maps", str(FIXTURE)), ("--seeds", "7"), ("--repeats", "0")):
            with self.subTest(flag=flag), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["--plan", "ext", flag, value, "--dry-run"])
