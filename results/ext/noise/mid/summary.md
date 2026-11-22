# 规则：基础规则 + 噪声观测（前 = 0.9，侧 = 0.8，后 = 0.7）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 50/50 | 174.04 | 2.131 | 2.028 | 3.4615 | 185.26 | 92.76 | 485.367 | 54185.06 |
| backtracker_loop0 | belief_astar_naive | 50/50 | 182.16 | 2.199 | 2.138 | 3.5854 | 196.26 | 102.68 | 358.029 | 46470.28 |
| backtracker_loop10 | belief_astar | 50/50 | 101.9 | 5.216 | 4.105 | 15.9375 | 85.34 | 43.5 | 78.456 | 7820.86 |
| backtracker_loop10 | belief_astar_naive | 50/50 | 90.26 | 4.7 | 3.78 | 13.1875 | 76.5 | 42.62 | 64.397 | 5705.12 |
| backtracker_loop30 | belief_astar | 50/50 | 37.1 | 2.382 | 1.871 | 7.5 | 25.62 | 7.56 | 22.407 | 855.9 |
| backtracker_loop30 | belief_astar_naive | 50/50 | 39.62 | 2.539 | 2.065 | 5.7143 | 28.02 | 9.18 | 27.175 | 1015.32 |
| external | belief_astar | 400/400 | 284.183 | 5.26 | 5.0 | 16.2174 | 237.162 | 155.07 | 783.177 | 71791.178 |
| external | belief_astar_naive | 400/400 | 302.135 | 5.545 | 5.504 | 15.087 | 253.338 | 171.822 | 815.207 | 72925.923 |
| kruskal_loop0 | belief_astar | 50/50 | 112.98 | 6.205 | 5.0 | 23.0 | 107.98 | 64.28 | 71.678 | 23266.4 |
| kruskal_loop0 | belief_astar_naive | 50/50 | 93.5 | 5.328 | 4.217 | 22.7647 | 91.06 | 51.32 | 52.394 | 13838.7 |
| kruskal_loop10 | belief_astar | 50/50 | 64.98 | 4.055 | 3.722 | 14.6471 | 54.82 | 28.52 | 27.32 | 4155.52 |
| kruskal_loop10 | belief_astar_naive | 50/50 | 72.06 | 4.476 | 3.42 | 13.6429 | 62.2 | 33.38 | 35.87 | 4186.4 |
| kruskal_loop30 | belief_astar | 50/50 | 32.92 | 2.267 | 1.964 | 4.8571 | 23.38 | 7.76 | 10.849 | 930 |
| kruskal_loop30 | belief_astar_naive | 50/50 | 32.3 | 2.225 | 1.643 | 5.6429 | 22.78 | 8.1 | 11.221 | 853.08 |
| prim_loop0 | belief_astar | 50/50 | 161.78 | 10.661 | 9.533 | 24.0667 | 144.6 | 96.1 | 161.029 | 29968.2 |
| prim_loop0 | belief_astar_naive | 50/50 | 147.4 | 9.697 | 8.397 | 27.1333 | 132.22 | 88.54 | 91.006 | 24216.94 |
| prim_loop10 | belief_astar | 50/50 | 113.04 | 7.817 | 5.098 | 23.0 | 90.76 | 56.92 | 29.693 | 12621.1 |
| prim_loop10 | belief_astar_naive | 50/50 | 90 | 6.196 | 4.765 | 16.2857 | 67.54 | 46.14 | 26.905 | 6966.74 |
| prim_loop30 | belief_astar | 50/50 | 38.06 | 2.679 | 1.964 | 7.5 | 24.36 | 9.24 | 9.008 | 708.26 |
| prim_loop30 | belief_astar_naive | 50/50 | 37.36 | 2.626 | 2.171 | 8.6429 | 24.96 | 9.84 | 8.189 | 797.36 |
| wilson_loop0 | belief_astar | 50/50 | 139.66 | 6.056 | 5.958 | 17.0 | 132.34 | 79.1 | 104.665 | 22666.04 |
| wilson_loop0 | belief_astar_naive | 50/50 | 139.88 | 6.115 | 5.651 | 25.0 | 137.34 | 79.96 | 82.225 | 26701.08 |
| wilson_loop10 | belief_astar | 50/50 | 91.64 | 4.919 | 3.974 | 20.7333 | 76.96 | 40.26 | 29.363 | 7893.22 |
| wilson_loop10 | belief_astar_naive | 50/50 | 96.1 | 4.881 | 4.254 | 12.5714 | 80.96 | 44.22 | 28.142 | 6958.18 |
| wilson_loop30 | belief_astar | 50/50 | 37.2 | 2.634 | 1.929 | 8.8571 | 24.92 | 8.18 | 9.471 | 836.92 |
| wilson_loop30 | belief_astar_naive | 50/50 | 37.94 | 2.686 | 2.105 | 8.4286 | 26 | 9.7 | 10.561 | 926.26 |
| ALL | belief_astar | 1000/1000 | 168.938 | 4.955 | 4.062 | 24.0667 | 143.682 | 88.737 | 135.213 | 37011.845 |
| ALL | belief_astar_naive | 1000/1000 | 173.783 | 4.901 | 4.0 | 27.1333 | 148.627 | 95.013 | 110.834 | 36102.142 |

动作与碰撞（含成功和失败运行）

| 地图组 | 算法 | 平均动作数 | 平均碰撞数 | 至少撞墙一次的比例 |
| --- | --- | --- | --- | --- |
| backtracker_loop0 | belief_astar | 231.56 | 57.52 | 100.00% |
| backtracker_loop0 | belief_astar_naive | 236.4 | 54.24 | 100.00% |
| backtracker_loop10 | belief_astar | 115.46 | 13.56 | 98.00% |
| backtracker_loop10 | belief_astar_naive | 102.1 | 11.84 | 98.00% |
| backtracker_loop30 | belief_astar | 40.46 | 3.36 | 88.00% |
| backtracker_loop30 | belief_astar_naive | 42.76 | 3.14 | 90.00% |
| external | belief_astar | 344.188 | 60.005 | 99.75% |
| external | belief_astar_naive | 363.03 | 60.895 | 99.75% |
| kruskal_loop0 | belief_astar | 138.2 | 25.22 | 96.00% |
| kruskal_loop0 | belief_astar_naive | 111.78 | 18.28 | 96.00% |
| kruskal_loop10 | belief_astar | 73.66 | 8.68 | 94.00% |
| kruskal_loop10 | belief_astar_naive | 82.06 | 10 | 94.00% |
| kruskal_loop30 | belief_astar | 35.9 | 2.98 | 78.00% |
| kruskal_loop30 | belief_astar_naive | 34.88 | 2.58 | 76.00% |
| prim_loop0 | belief_astar | 195.22 | 33.44 | 100.00% |
| prim_loop0 | belief_astar_naive | 176.74 | 29.34 | 100.00% |
| prim_loop10 | belief_astar | 129.26 | 16.22 | 92.00% |
| prim_loop10 | belief_astar_naive | 100.9 | 10.9 | 90.00% |
| prim_loop30 | belief_astar | 40.16 | 2.1 | 78.00% |
| prim_loop30 | belief_astar_naive | 39.62 | 2.26 | 74.00% |
| wilson_loop0 | belief_astar | 170.42 | 30.76 | 100.00% |
| wilson_loop0 | belief_astar_naive | 172.1 | 32.22 | 100.00% |
| wilson_loop10 | belief_astar | 104.3 | 12.66 | 100.00% |
| wilson_loop10 | belief_astar_naive | 108.86 | 12.76 | 100.00% |
| wilson_loop30 | belief_astar | 40.18 | 2.98 | 90.00% |
| wilson_loop30 | belief_astar_naive | 41.26 | 3.32 | 88.00% |
| ALL | belief_astar | 203.414 | 34.476 | 95.60% |
| ALL | belief_astar_naive | 207.685 | 33.902 | 95.20% |
