"""实验命令行入口（薄壳）：实现在 src/core/experiments.py，实验计划在 src/basic/plan.py（扩展：src/ext/plan.py）。

    python src/run_experiments.py --plan basic
    python src/run_experiments.py --maps "mazes/classic/external_*.json" --algorithms dfs flood_fill
    python src/run_experiments.py --plot results/basic/main
"""

from core.experiments import main

if __name__ == "__main__":
    main()
