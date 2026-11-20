"""批量实验（D2）与计时范围（D3）的测试。"""

import csv
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from algorithm_api import Direction, Maze, Runner  # noqa: E402
from run_experiments import (ExperimentRun, main, map_group, plan_generated_names,  # noqa: E402
                             summarize, write_outputs)

CORE = [ROOT / "mazes" / "classic" / f"external_{n}.json" for n in ("1stworld", "uk2011f")]


class SlowDisplay:
    """决策很快、但 debug_view 很慢的策略，模拟“画面绘制 / 动画”耗时。"""
    name = "slow_display"

    def reset(self, **kwargs):
        """无需初始化。"""

    def choose_direction(self, observation):
        """朝第一个无墙方向走。"""
        return next(d for d in Direction if d not in observation.walls)

    def debug_view(self):
        """故意等待，代表绘制耗时。"""
        time.sleep(0.05)
        return {}


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        """每个测试使用独立的临时输出目录。"""
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        """删除临时目录。"""
        self.tmp.cleanup()

    def test_rows_follow_the_plan_rules(self):
        """每个（地图, 算法, 种子）一行；最短路来自 BFS；失败运行的 ratio 留空；重复运行结果一致。"""
        run = ExperimentRun(CORE, ["bfs", "flood_fill", "wall_follower_left"], seeds=[0, 1], repeats=2)
        rows = run.run_all()
        self.assertEqual(len(rows), 2 * 3 * 2)
        for row in rows:
            self.assertTrue(row["consistent"])
            self.assertEqual(row["map_group"], "external")
            if row["status"] == "success":
                self.assertAlmostEqual(row["ratio"], row["steps"] / row["shortest"], places=3)
            else:
                self.assertEqual(row["ratio"], "")
        bfs = [r for r in rows if r["algorithm"] == "bfs"]
        self.assertTrue(all(r["ratio"] == 1.0 and r["expanded_nodes"] for r in bfs))
        self.assertEqual({r["experiment_mode"] for r in bfs}, {"known_map_planning"})

    def test_outputs_and_summary(self):
        """导出 runs.csv、summary.csv、summary.md、metadata.json；汇总含“全部地图”一组。"""
        run = ExperimentRun(CORE, ["dfs", "random_walk"], seeds=[0], max_steps=300)
        run.run_all()
        out = write_outputs(run, self.out / "r")
        for name in ("runs.csv", "summary.csv", "summary.md", "metadata.json"):
            self.assertTrue((out / name).exists(), name)
        with (out / "runs.csv").open(encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 4)
        summary = {(s["map_group"], s["algorithm"]): s for s in summarize(run.rows)}
        self.assertEqual(summary[("ALL", "random_walk")]["success_rate"], 0)
        self.assertEqual(summary[("ALL", "random_walk")]["mean_ratio"], "")
        meta = json.loads((out / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["runs"], meta["repeats"], meta["max_steps"]), (4, 1, 300))
        figure = out / "figures" / "ratio_by_group.png"
        self.assertTrue(figure.exists())
        figure.unlink()
        main(["--plot", str(out)])  # 只从 summary.csv 重画图表
        self.assertTrue(figure.exists())

    def test_plan_map_set_exists(self):
        """实验计划的 120 张生成地图都在地图库中，且分组名称正确。"""
        names = plan_generated_names()
        self.assertEqual(len(names), 120)
        missing = [n for n in names if not (ROOT / "mazes" / "classic" / n).exists()]
        self.assertEqual(missing, [])
        maze = Maze.from_json(ROOT / "mazes" / "classic" / "gen_wilson_16x16_s3_l30.json")
        self.assertEqual(map_group(maze), "wilson_loop30")
        self.assertEqual(map_group(Maze.from_json(ROOT / "mazes" / "classic" / "gen_backtracker_16x16_s1.json")),
                         "backtracker_loop0")

    def test_command_line(self):
        """命令行可以指定地图、算法、种子并导出到指定目录。"""
        main(["--maps", str(CORE[0]), "--algorithms", "dfs", "bfs", "--out", str(self.out / "cli"),
              "--no-plot"])
        with (self.out / "cli" / "runs.csv").open(encoding="utf-8") as f:
            self.assertEqual({r["algorithm"] for r in csv.DictReader(f)}, {"dfs", "bfs"})


class TimingScopeTests(unittest.TestCase):
    def test_display_time_is_not_counted(self):
        """D3：画面相关的 debug_view 耗时不计入算法计算时间。"""
        maze = Maze.from_json(CORE[0])
        runner = Runner(maze, SlowDisplay())
        started = time.perf_counter()
        runner.run(max_decisions=4)
        wall = time.perf_counter() - started
        self.assertGreater(wall, 0.2)                    # 4 次 debug_view 至少 0.2 秒
        self.assertLess(runner.compute_seconds, 0.02)    # 但计入的计算时间几乎为 0


if __name__ == "__main__":
    unittest.main()
