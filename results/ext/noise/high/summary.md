# 规则：基础规则 + 噪声观测（前 = 0.95，侧 = 0.9，后 = 0.85）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 50/50 | 160.6 | 1.956 | 1.789 | 4.25 | 155.7 | 80.44 | 136.014 | 53040.82 |
| backtracker_loop0 | belief_astar_naive | 50/50 | 166.36 | 1.921 | 1.818 | 4.2201 | 164.66 | 85.74 | 102.896 | 55198.66 |
| backtracker_loop10 | belief_astar | 50/50 | 49.64 | 2.602 | 1.789 | 10.5 | 38.02 | 13.36 | 12.912 | 1879.72 |
| backtracker_loop10 | belief_astar_naive | 50/50 | 49.18 | 2.636 | 1.702 | 11.25 | 38.7 | 14.68 | 13.14 | 1824.06 |
| backtracker_loop30 | belief_astar | 50/50 | 30 | 1.935 | 1.464 | 6.2 | 19.1 | 4.24 | 9.325 | 642.96 |
| backtracker_loop30 | belief_astar_naive | 50/50 | 28.42 | 1.827 | 1.464 | 5.0 | 18.08 | 3.54 | 9.607 | 613.32 |
| external | belief_astar | 400/400 | 245.847 | 4.38 | 4.266 | 12.4444 | 186.265 | 120.692 | 239.729 | 60540.37 |
| external | belief_astar_naive | 400/400 | 251.627 | 4.488 | 4.157 | 13.2778 | 188.333 | 126.665 | 209.621 | 57284.6 |
| kruskal_loop0 | belief_astar | 50/50 | 81.66 | 4.508 | 2.96 | 21.7059 | 72.14 | 41.86 | 31.377 | 14212.06 |
| kruskal_loop0 | belief_astar_naive | 50/50 | 80.22 | 4.458 | 2.655 | 23.5882 | 71.06 | 41.64 | 22.102 | 16926.82 |
| kruskal_loop10 | belief_astar | 50/50 | 47.34 | 2.99 | 2.029 | 11.0 | 35.9 | 15.72 | 13.88 | 1995.3 |
| kruskal_loop10 | belief_astar_naive | 50/50 | 41.44 | 2.612 | 2.0 | 8.7857 | 30.64 | 11.98 | 12.425 | 1292.44 |
| kruskal_loop30 | belief_astar | 50/50 | 21.36 | 1.479 | 1.321 | 3.0 | 11.98 | 2.38 | 7.342 | 395.06 |
| kruskal_loop30 | belief_astar_naive | 50/50 | 21.84 | 1.51 | 1.375 | 3.3333 | 12.64 | 2.86 | 7.278 | 430.3 |
| prim_loop0 | belief_astar | 50/50 | 123.88 | 8.16 | 6.165 | 25.5 | 98.26 | 66.42 | 22.566 | 17473.96 |
| prim_loop0 | belief_astar_naive | 50/50 | 123.48 | 8.138 | 6.515 | 23.8 | 98.14 | 67.26 | 25.822 | 16326.82 |
| prim_loop10 | belief_astar | 50/50 | 65.98 | 4.513 | 2.867 | 14.8 | 44.98 | 23.5 | 12.517 | 2766.34 |
| prim_loop10 | belief_astar_naive | 50/50 | 71.62 | 4.93 | 3.691 | 19.5714 | 48.6 | 28.4 | 16.431 | 2272.72 |
| prim_loop30 | belief_astar | 50/50 | 31.92 | 2.246 | 1.967 | 5.8571 | 18.72 | 5.82 | 7.536 | 463.48 |
| prim_loop30 | belief_astar_naive | 50/50 | 33.78 | 2.378 | 1.967 | 6.1429 | 20.04 | 6.66 | 7.917 | 541.38 |
| wilson_loop0 | belief_astar | 50/50 | 104.1 | 4.565 | 3.357 | 13.0 | 90.62 | 49.52 | 39.85 | 11587.62 |
| wilson_loop0 | belief_astar_naive | 50/50 | 122.58 | 5.483 | 4.262 | 19.9286 | 110.02 | 65.26 | 66.419 | 16586.22 |
| wilson_loop10 | belief_astar | 50/50 | 62.88 | 3.326 | 2.528 | 8.5556 | 48.24 | 20.38 | 16.761 | 2711.46 |
| wilson_loop10 | belief_astar_naive | 50/50 | 60.48 | 3.258 | 2.515 | 13.2667 | 46.46 | 19.48 | 15.813 | 2430.54 |
| wilson_loop30 | belief_astar | 50/50 | 27.68 | 1.958 | 1.691 | 5.0714 | 15.74 | 3.82 | 7.238 | 475.56 |
| wilson_loop30 | belief_astar_naive | 50/50 | 26.7 | 1.888 | 1.679 | 3.8571 | 15.28 | 3.78 | 7.854 | 461.5 |
| ALL | belief_astar | 1000/1000 | 138.691 | 3.764 | 2.919 | 25.5 | 106.976 | 64.65 | 35.501 | 29598.365 |
| ALL | belief_astar_naive | 1000/1000 | 141.956 | 3.847 | 2.958 | 23.8 | 109.049 | 68.23 | 34.177 | 28659.079 |

动作与碰撞（含成功和失败运行）

| 地图组 | 算法 | 平均动作数 | 平均碰撞数 | 至少撞墙一次的比例 |
| --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 203.64 | 43.04 | 96.00% |
| backtracker_loop0 | belief_astar_naive | 209.62 | 43.26 | 96.00% |
| backtracker_loop10 | belief_astar | 53.24 | 3.6 | 86.00% |
| backtracker_loop10 | belief_astar_naive | 52.62 | 3.44 | 84.00% |
| backtracker_loop30 | belief_astar | 31.4 | 1.4 | 78.00% |
| backtracker_loop30 | belief_astar_naive | 29.72 | 1.3 | 76.00% |
| external | belief_astar | 285.175 | 39.328 | 99.00% |
| external | belief_astar_naive | 288.632 | 37.005 | 98.25% |
| kruskal_loop0 | belief_astar | 95.36 | 13.7 | 92.00% |
| kruskal_loop0 | belief_astar_naive | 92.46 | 12.24 | 90.00% |
| kruskal_loop10 | belief_astar | 50.54 | 3.2 | 72.00% |
| kruskal_loop10 | belief_astar_naive | 43.92 | 2.48 | 70.00% |
| kruskal_loop30 | belief_astar | 22.02 | 0.66 | 48.00% |
| kruskal_loop30 | belief_astar_naive | 22.52 | 0.68 | 48.00% |
| prim_loop0 | belief_astar | 139.36 | 15.48 | 94.00% |
| prim_loop0 | belief_astar_naive | 138.96 | 15.48 | 92.00% |
| prim_loop10 | belief_astar | 69.9 | 3.92 | 84.00% |
| prim_loop10 | belief_astar_naive | 75.62 | 4 | 82.00% |
| prim_loop30 | belief_astar | 32.94 | 1.02 | 64.00% |
| prim_loop30 | belief_astar_naive | 34.94 | 1.16 | 66.00% |
| wilson_loop0 | belief_astar | 118.26 | 14.16 | 94.00% |
| wilson_loop0 | belief_astar_naive | 142.02 | 19.44 | 94.00% |
| wilson_loop10 | belief_astar | 67.8 | 4.92 | 88.00% |
| wilson_loop10 | belief_astar_naive | 64.64 | 4.16 | 86.00% |
| wilson_loop30 | belief_astar | 28.88 | 1.2 | 66.00% |
| wilson_loop30 | belief_astar_naive | 27.82 | 1.12 | 60.00% |
| ALL | belief_astar | 159.737 | 21.046 | 87.70% |
| ALL | belief_astar_naive | 162.196 | 20.24 | 86.50% |
