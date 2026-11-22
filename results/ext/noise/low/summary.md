# 规则：基础规则 + 噪声观测（前 = 0.8，侧 = 0.7，后 = 0.6）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 50/50 | 173.52 | 2.179 | 2.138 | 4.2195 | 197.22 | 95.44 | 548.506 | 48166.38 |
| backtracker_loop0 | belief_astar_naive | 50/50 | 171.32 | 2.154 | 2.195 | 3.7317 | 200.66 | 92.5 | 457.849 | 44459.36 |
| backtracker_loop10 | belief_astar | 50/50 | 99.14 | 5.394 | 3.61 | 17.8571 | 98.26 | 46.26 | 110.819 | 11331.08 |
| backtracker_loop10 | belief_astar_naive | 50/50 | 86.84 | 4.571 | 3.54 | 16.9375 | 84.26 | 42.06 | 88.806 | 6341.04 |
| backtracker_loop30 | belief_astar | 50/50 | 67.92 | 4.341 | 3.143 | 16.1875 | 55.88 | 26.12 | 56.26 | 3271.82 |
| backtracker_loop30 | belief_astar_naive | 50/50 | 66.2 | 4.305 | 2.886 | 22.2857 | 55.7 | 26.3 | 44.87 | 2975.3 |
| external | belief_astar | 400/400 | 295.812 | 5.587 | 5.376 | 13.1429 | 273.82 | 165.907 | 937.59 | 76105.643 |
| external | belief_astar_naive | 400/400 | 298.058 | 5.612 | 5.322 | 18.0435 | 282.07 | 171.952 | 842.841 | 71388.867 |
| kruskal_loop0 | belief_astar | 50/50 | 107.34 | 6.041 | 5.198 | 25.7059 | 108.98 | 60.84 | 170.253 | 16058.84 |
| kruskal_loop0 | belief_astar_naive | 50/50 | 96.78 | 5.377 | 4.95 | 14.4118 | 100.62 | 55.98 | 146.908 | 9390.76 |
| kruskal_loop10 | belief_astar | 50/50 | 82.24 | 5.176 | 4.518 | 14.3571 | 75.08 | 39.9 | 105.001 | 5737.62 |
| kruskal_loop10 | belief_astar_naive | 50/50 | 84.08 | 5.279 | 4.589 | 13.6429 | 80.54 | 41.98 | 102.37 | 6034.82 |
| kruskal_loop30 | belief_astar | 50/50 | 73.54 | 5.092 | 3.911 | 16.5714 | 60.66 | 30.86 | 69.713 | 3684.32 |
| kruskal_loop30 | belief_astar_naive | 50/50 | 54.44 | 3.767 | 2.67 | 14.8667 | 44.76 | 22.2 | 43.095 | 2257.12 |
| prim_loop0 | belief_astar | 50/50 | 178.68 | 11.732 | 11.281 | 27.375 | 172.08 | 108.24 | 464.729 | 33602.52 |
| prim_loop0 | belief_astar_naive | 50/50 | 166.32 | 10.795 | 9.267 | 22.7333 | 162.38 | 102.8 | 339.803 | 27797.12 |
| prim_loop10 | belief_astar | 50/50 | 114.52 | 7.853 | 7.071 | 18.6 | 100.54 | 60.7 | 158.507 | 12004.66 |
| prim_loop10 | belief_astar_naive | 50/50 | 115 | 7.908 | 7.763 | 16.1429 | 103.08 | 63.12 | 144.939 | 11416.02 |
| prim_loop30 | belief_astar | 50/50 | 69.74 | 4.882 | 3.714 | 18.8571 | 53.68 | 27.96 | 45.055 | 3410.08 |
| prim_loop30 | belief_astar_naive | 50/50 | 82.14 | 5.757 | 3.857 | 21.9286 | 65.1 | 39.16 | 47.641 | 4070.54 |
| wilson_loop0 | belief_astar | 50/50 | 170.68 | 7.778 | 6.469 | 27.7143 | 175.32 | 100.24 | 414.554 | 41274.86 |
| wilson_loop0 | belief_astar_naive | 50/50 | 141.32 | 6.506 | 4.957 | 18.3571 | 148.22 | 81.52 | 236.802 | 22780.98 |
| wilson_loop10 | belief_astar | 50/50 | 111.36 | 5.928 | 5.386 | 21.2667 | 104.86 | 56.78 | 199.313 | 12010.08 |
| wilson_loop10 | belief_astar_naive | 50/50 | 107.48 | 5.784 | 4.703 | 21.8 | 104.18 | 55.26 | 140.996 | 10325.86 |
| wilson_loop30 | belief_astar | 50/50 | 66.82 | 4.738 | 3.931 | 13.7143 | 52.52 | 25.7 | 57.382 | 3069.3 |
| wilson_loop30 | belief_astar_naive | 50/50 | 49.4 | 3.484 | 3.0 | 11.6667 | 38.74 | 16.28 | 43.974 | 1431.68 |
| ALL | belief_astar | 1000/1000 | 184.1 | 5.791 | 5.0 | 27.7143 | 172.282 | 100.315 | 294.2 | 40123.335 |
| ALL | belief_astar_naive | 1000/1000 | 180.289 | 5.529 | 4.75 | 22.7333 | 172.24 | 100.739 | 261.785 | 36019.577 |

动作与碰撞（含成功和失败运行）

| 地图组 | 算法 | 平均动作数 | 平均碰撞数 | 至少撞墙一次的比例 |
| --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 238.1 | 64.58 | 100.00% |
| backtracker_loop0 | belief_astar_naive | 236.14 | 64.82 | 100.00% |
| backtracker_loop10 | belief_astar | 123.82 | 24.68 | 100.00% |
| backtracker_loop10 | belief_astar_naive | 105.84 | 19 | 100.00% |
| backtracker_loop30 | belief_astar | 77.78 | 9.86 | 94.00% |
| backtracker_loop30 | belief_astar_naive | 76.02 | 9.82 | 96.00% |
| external | belief_astar | 376.647 | 80.835 | 100.00% |
| external | belief_astar_naive | 376.945 | 78.888 | 100.00% |
| kruskal_loop0 | belief_astar | 136.38 | 29.04 | 98.00% |
| kruskal_loop0 | belief_astar_naive | 122.1 | 25.32 | 98.00% |
| kruskal_loop10 | belief_astar | 98.16 | 15.92 | 100.00% |
| kruskal_loop10 | belief_astar_naive | 101.48 | 17.4 | 100.00% |
| kruskal_loop30 | belief_astar | 83.28 | 9.74 | 96.00% |
| kruskal_loop30 | belief_astar_naive | 61.62 | 7.18 | 92.00% |
| prim_loop0 | belief_astar | 225.9 | 47.22 | 100.00% |
| prim_loop0 | belief_astar_naive | 209.82 | 43.5 | 100.00% |
| prim_loop10 | belief_astar | 136.62 | 22.1 | 100.00% |
| prim_loop10 | belief_astar_naive | 138.5 | 23.5 | 100.00% |
| prim_loop30 | belief_astar | 78.34 | 8.6 | 98.00% |
| prim_loop30 | belief_astar_naive | 91.54 | 9.4 | 100.00% |
| wilson_loop0 | belief_astar | 218.96 | 48.28 | 100.00% |
| wilson_loop0 | belief_astar_naive | 180.2 | 38.88 | 100.00% |
| wilson_loop10 | belief_astar | 135.76 | 24.4 | 100.00% |
| wilson_loop10 | belief_astar_naive | 130.3 | 22.82 | 100.00% |
| wilson_loop30 | belief_astar | 75 | 8.18 | 96.00% |
| wilson_loop30 | belief_astar_naive | 55.5 | 6.1 | 96.00% |
| ALL | belief_astar | 232.064 | 47.964 | 99.10% |
| ALL | belief_astar_naive | 226.231 | 45.942 | 99.10% |
