# 规则：基础规则 + 两阶段比赛（探索折算系数 = 30）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | bounded_explore_e0 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 71.046 | 2837.4 |
| backtracker_loop0 | bounded_explore_e10 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 70.614 | 2837.4 |
| backtracker_loop0 | bounded_explore_e25 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 70.799 | 2837.4 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 51.962 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.38 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 58.483 | 2097.8 |
| backtracker_loop10 | bounded_explore_e0 | 10/10 | 65.5 | 3.54 | 2.64 | 9.9286 | 45 | 10.8 | 121.928 | 10687.9 |
| backtracker_loop10 | bounded_explore_e10 | 10/10 | 59.8 | 3.27 | 2.283 | 9.9286 | 41.1 | 7.9 | 97.297 | 9724.8 |
| backtracker_loop10 | bounded_explore_e25 | 10/10 | 53.8 | 2.96 | 1.414 | 9.9286 | 37.1 | 6.7 | 34.348 | 8084.6 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 16.928 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.153 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 30.9 | 1.616 | 1.257 | 3.6875 | 21.1 | 1.4 | 18.274 | 615.4 |
| backtracker_loop30 | bounded_explore_e0 | 10/10 | 33.3 | 2.127 | 2.08 | 3.3571 | 19.3 | 4 | 56.868 | 3870.9 |
| backtracker_loop30 | bounded_explore_e10 | 10/10 | 32.6 | 2.08 | 2.08 | 3.3571 | 18.8 | 4 | 55.619 | 3694.6 |
| backtracker_loop30 | bounded_explore_e25 | 10/10 | 28.8 | 1.874 | 1.5 | 3.3571 | 16.5 | 3.1 | 35.854 | 2371.7 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 12.884 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.863 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 13.0 | 336.7 |
| external | bounded_explore_e0 | 315/315 | 218.622 | 4.108 | 3.913 | 31.0714 | 120.787 | 68.676 | 1170.975 | 72523.203 |
| external | bounded_explore_e10 | 315/315 | 197.375 | 3.756 | 3.513 | 31.0714 | 109.905 | 55.765 | 909.419 | 59581.063 |
| external | bounded_explore_e25 | 315/315 | 175.314 | 3.337 | 3.074 | 31.0714 | 97.927 | 44.873 | 588.331 | 43698.733 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 72.976 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 5.467 |  |
| external | turn_aware_astar | 315/315 | 119.619 | 2.293 | 1.912 | 30.1429 | 64.987 | 21.59 | 70.929 | 2906.213 |
| kruskal_loop0 | bounded_explore_e0 | 10/10 | 48 | 2.514 | 2.225 | 4.9048 | 36.1 | 17.4 | 71.614 | 3132.7 |
| kruskal_loop0 | bounded_explore_e10 | 10/10 | 42.7 | 2.253 | 1.794 | 4.5714 | 31.8 | 13.5 | 54.295 | 2583.7 |
| kruskal_loop0 | bounded_explore_e25 | 10/10 | 32 | 1.69 | 1.429 | 3.24 | 23.3 | 7.3 | 24.995 | 1018.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 14.059 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.108 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 31.3 | 1.657 | 1.429 | 3.24 | 22.9 | 7.1 | 20.739 | 578.1 |
| kruskal_loop10 | bounded_explore_e0 | 10/10 | 45.7 | 2.742 | 2.358 | 6.2222 | 30.6 | 14.5 | 76.359 | 3471.9 |
| kruskal_loop10 | bounded_explore_e10 | 10/10 | 44.1 | 2.65 | 2.179 | 6.2222 | 29.3 | 13.8 | 62.596 | 3254.2 |
| kruskal_loop10 | bounded_explore_e25 | 10/10 | 31.7 | 1.921 | 1.718 | 4.2222 | 19.3 | 7.4 | 25.569 | 1525 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 13.819 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.117 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.2 | 1.491 | 1.496 | 2.0 | 15.2 | 3 | 17.417 | 457.5 |
| kruskal_loop30 | bounded_explore_e0 | 10/10 | 31.9 | 2.161 | 2.138 | 4.75 | 17.4 | 6.4 | 61.034 | 2601.6 |
| kruskal_loop30 | bounded_explore_e10 | 10/10 | 29 | 1.959 | 1.746 | 4.75 | 16.2 | 5.9 | 26.529 | 1911.6 |
| kruskal_loop30 | bounded_explore_e25 | 10/10 | 20.5 | 1.417 | 1.232 | 2.4286 | 10.8 | 2 | 18.328 | 773 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 12.472 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.726 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 19.8 | 1.367 | 1.232 | 2.1333 | 10.6 | 2 | 14.418 | 344.7 |
| prim_loop0 | bounded_explore_e0 | 10/10 | 77.7 | 5.058 | 4.533 | 9.0 | 51.9 | 30.3 | 65.219 | 2491.6 |
| prim_loop0 | bounded_explore_e10 | 10/10 | 76 | 4.941 | 4.467 | 9.0 | 50.7 | 30.2 | 38.448 | 1914.9 |
| prim_loop0 | bounded_explore_e25 | 10/10 | 75.6 | 4.919 | 4.467 | 9.0 | 50.3 | 30.2 | 39.464 | 1700 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 57.969 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 3.672 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 75.6 | 4.919 | 4.467 | 9.0 | 50.3 | 30.2 | 33.793 | 1335.5 |
| prim_loop10 | bounded_explore_e0 | 10/10 | 53.1 | 3.604 | 2.971 | 7.0667 | 32.5 | 14.7 | 48.413 | 3180.2 |
| prim_loop10 | bounded_explore_e10 | 10/10 | 51.8 | 3.512 | 2.938 | 7.0 | 31.7 | 14.6 | 30.983 | 2760.9 |
| prim_loop10 | bounded_explore_e25 | 10/10 | 49.8 | 3.37 | 2.938 | 7.0 | 30.3 | 13.6 | 25.601 | 2434.8 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 27.727 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 1.932 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.5 | 3.163 | 2.938 | 7.0 | 27.6 | 12.8 | 19.752 | 785 |
| prim_loop30 | bounded_explore_e0 | 10/10 | 40.2 | 2.82 | 2.786 | 3.9286 | 21.4 | 6.3 | 101.118 | 4618.4 |
| prim_loop30 | bounded_explore_e10 | 10/10 | 36 | 2.52 | 2.321 | 3.9286 | 18.7 | 5.8 | 45.355 | 3478.7 |
| prim_loop30 | bounded_explore_e25 | 10/10 | 29.7 | 2.077 | 2.0 | 3.5333 | 15.3 | 4.9 | 19.189 | 1456.3 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 15.053 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.871 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.6 | 4 | 11.307 | 329 |
| wilson_loop0 | bounded_explore_e0 | 10/10 | 108.3 | 5.049 | 3.894 | 13.5714 | 79.1 | 45.7 | 86.308 | 7056.7 |
| wilson_loop0 | bounded_explore_e10 | 10/10 | 98.9 | 4.766 | 3.427 | 13.5714 | 73.4 | 38.8 | 65.542 | 5119.2 |
| wilson_loop0 | bounded_explore_e25 | 10/10 | 96 | 4.628 | 2.76 | 13.5714 | 71.2 | 36.3 | 65.666 | 4943.1 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 58.16 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 2.368 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 88.8 | 4.428 | 2.043 | 13.5714 | 65.8 | 32.2 | 50.492 | 2212.8 |
| wilson_loop10 | bounded_explore_e0 | 10/10 | 59 | 3.233 | 3.513 | 4.6429 | 40.6 | 14.3 | 87.071 | 5167.3 |
| wilson_loop10 | bounded_explore_e10 | 10/10 | 57.4 | 3.158 | 3.513 | 4.6429 | 39.2 | 13.8 | 72.603 | 4637.5 |
| wilson_loop10 | bounded_explore_e25 | 10/10 | 53 | 2.948 | 2.774 | 4.6429 | 35.9 | 10.6 | 67.668 | 3939 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 25.036 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 1.38 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.6 | 2.358 | 2.011 | 4.2143 | 29.1 | 7.3 | 18.817 | 723.2 |
| wilson_loop30 | bounded_explore_e0 | 10/10 | 32.1 | 2.277 | 2.25 | 4.4286 | 16.7 | 3.2 | 79.106 | 3097.6 |
| wilson_loop30 | bounded_explore_e10 | 10/10 | 31.9 | 2.263 | 2.25 | 4.4286 | 16.6 | 3.2 | 77.22 | 3054.9 |
| wilson_loop30 | bounded_explore_e25 | 10/10 | 26.2 | 1.856 | 1.5 | 4.4286 | 12.6 | 1.5 | 21.426 | 1999 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 13.655 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.716 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 12.894 | 312.1 |
| ALL | bounded_explore_e0 | 435/435 | 173.756 | 3.805 | 3.689 | 31.0714 | 97.607 | 53.584 | 654.96 | 53717.129 |
| ALL | bounded_explore_e10 | 435/435 | 157.575 | 3.51 | 3.357 | 31.0714 | 89.195 | 43.864 | 533.178 | 44178.756 |
| ALL | bounded_explore_e25 | 435/435 | 140.149 | 3.121 | 2.844 | 31.0714 | 79.49 | 35.336 | 313.551 | 32404.428 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 59.552 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 4.518 |  |
| ALL | turn_aware_astar | 435/435 | 98.248 | 2.276 | 1.852 | 30.1429 | 54.593 | 17.979 | 58.262 | 2337.322 |

两阶段比赛（成功运行；探索代价含返回起点，冲刺/最优的分母为已知地图上的最优冲刺代价）：

| 地图组 | 算法 | 平均探索代价 | 冲刺/最优（均值） | 平均成绩 |
| --- | --- | --- | --- | --- |
| backtracker_loop0 | bounded_explore_e0 | 154.0 | 1.0 | 82.133 |
| backtracker_loop0 | bounded_explore_e10 | 154.0 | 1.0 | 82.133 |
| backtracker_loop0 | bounded_explore_e25 | 154.0 | 1.0 | 82.133 |
| backtracker_loop0 | flood_fill | 154.0 | 1.0 | 82.133 |
| backtracker_loop0 | repeated_astar | 154.0 | 1.0 | 82.133 |
| backtracker_loop0 | turn_aware_astar | 154.0 | 1.0 | 82.133 |
| backtracker_loop10 | bounded_explore_e0 | 80.2 | 1.0 | 22.373 |
| backtracker_loop10 | bounded_explore_e10 | 75.8 | 1.005 | 22.327 |
| backtracker_loop10 | bounded_explore_e25 | 69.4 | 1.016 | 22.313 |
| backtracker_loop10 | flood_fill | 58.2 | 1.326 | 27.84 |
| backtracker_loop10 | repeated_astar | 53.0 | 1.297 | 27.267 |
| backtracker_loop10 | turn_aware_astar | 58.2 | 1.413 | 29.24 |
| backtracker_loop30 | bounded_explore_e0 | 44.6 | 1.0 | 17.087 |
| backtracker_loop30 | bounded_explore_e10 | 43.4 | 1.007 | 17.147 |
| backtracker_loop30 | bounded_explore_e25 | 43.2 | 1.043 | 17.74 |
| backtracker_loop30 | flood_fill | 39.2 | 1.18 | 19.607 |
| backtracker_loop30 | repeated_astar | 39.2 | 1.162 | 19.407 |
| backtracker_loop30 | turn_aware_astar | 39.2 | 1.18 | 19.607 |
| external | bounded_explore_e0 | 243.917 | 1.0 | 65.334 |
| external | bounded_explore_e10 | 231.124 | 1.016 | 65.837 |
| external | bounded_explore_e25 | 219.765 | 1.051 | 67.275 |
| external | flood_fill | 188.533 | 1.243 | 74.627 |
| external | repeated_astar | 182.394 | 1.238 | 74.216 |
| external | turn_aware_astar | 187.486 | 1.24 | 74.116 |
| kruskal_loop0 | bounded_explore_e0 | 63.6 | 1.0 | 20.02 |
| kruskal_loop0 | bounded_explore_e10 | 59.2 | 1.0 | 19.873 |
| kruskal_loop0 | bounded_explore_e25 | 50.2 | 1.0 | 19.573 |
| kruskal_loop0 | flood_fill | 47.6 | 1.0 | 19.487 |
| kruskal_loop0 | repeated_astar | 50.0 | 1.0 | 19.567 |
| kruskal_loop0 | turn_aware_astar | 49.2 | 1.0 | 19.54 |
| kruskal_loop10 | bounded_explore_e0 | 57.4 | 1.0 | 18.213 |
| kruskal_loop10 | bounded_explore_e10 | 55.4 | 1.0 | 18.147 |
| kruskal_loop10 | bounded_explore_e25 | 48.4 | 1.037 | 18.513 |
| kruskal_loop10 | flood_fill | 42.0 | 1.109 | 19.3 |
| kruskal_loop10 | repeated_astar | 43.2 | 1.119 | 19.44 |
| kruskal_loop10 | turn_aware_astar | 41.4 | 1.056 | 18.58 |
| kruskal_loop30 | bounded_explore_e0 | 42.0 | 1.0 | 15.9 |
| kruskal_loop30 | bounded_explore_e10 | 41.0 | 1.021 | 16.167 |
| kruskal_loop30 | bounded_explore_e25 | 35.0 | 1.042 | 16.267 |
| kruskal_loop30 | flood_fill | 36.0 | 1.078 | 16.8 |
| kruskal_loop30 | repeated_astar | 34.2 | 1.021 | 15.94 |
| kruskal_loop30 | turn_aware_astar | 35.4 | 1.078 | 16.78 |
| prim_loop0 | bounded_explore_e0 | 92.4 | 1.0 | 18.28 |
| prim_loop0 | bounded_explore_e10 | 91.2 | 1.013 | 18.44 |
| prim_loop0 | bounded_explore_e25 | 91.0 | 1.013 | 18.433 |
| prim_loop0 | flood_fill | 94.8 | 1.013 | 18.56 |
| prim_loop0 | repeated_astar | 103.4 | 1.0 | 18.647 |
| prim_loop0 | turn_aware_astar | 91.0 | 1.013 | 18.433 |
| prim_loop10 | bounded_explore_e0 | 64.2 | 1.0 | 16.64 |
| prim_loop10 | bounded_explore_e10 | 63.4 | 1.007 | 16.713 |
| prim_loop10 | bounded_explore_e25 | 63.4 | 1.036 | 17.113 |
| prim_loop10 | flood_fill | 64.6 | 1.142 | 18.853 |
| prim_loop10 | repeated_astar | 77.2 | 1.333 | 21.973 |
| prim_loop10 | turn_aware_astar | 63.2 | 1.142 | 18.807 |
| prim_loop30 | bounded_explore_e0 | 47.2 | 1.0 | 15.773 |
| prim_loop30 | bounded_explore_e10 | 45.2 | 1.029 | 16.107 |
| prim_loop30 | bounded_explore_e25 | 44.0 | 1.092 | 16.967 |
| prim_loop30 | flood_fill | 42.8 | 1.147 | 17.727 |
| prim_loop30 | repeated_astar | 41.6 | 1.169 | 17.987 |
| prim_loop30 | turn_aware_astar | 42.4 | 1.119 | 17.313 |
| wilson_loop0 | bounded_explore_e0 | 126.0 | 1.0 | 27.8 |
| wilson_loop0 | bounded_explore_e10 | 121.2 | 1.0 | 27.64 |
| wilson_loop0 | bounded_explore_e25 | 119.6 | 1.0 | 27.587 |
| wilson_loop0 | flood_fill | 117.0 | 1.03 | 28.9 |
| wilson_loop0 | repeated_astar | 89.6 | 1.0 | 26.587 |
| wilson_loop0 | turn_aware_astar | 113.8 | 1.03 | 28.793 |
| wilson_loop10 | bounded_explore_e0 | 73.8 | 1.0 | 21.86 |
| wilson_loop10 | bounded_explore_e10 | 72.6 | 1.005 | 22.02 |
| wilson_loop10 | bounded_explore_e25 | 70.8 | 1.022 | 22.36 |
| wilson_loop10 | flood_fill | 70.8 | 1.543 | 30.36 |
| wilson_loop10 | repeated_astar | 61.4 | 1.221 | 25.147 |
| wilson_loop10 | turn_aware_astar | 70.6 | 1.543 | 30.353 |
| wilson_loop30 | bounded_explore_e0 | 42.6 | 1.0 | 15.62 |
| wilson_loop30 | bounded_explore_e10 | 42.2 | 1.0 | 15.607 |
| wilson_loop30 | bounded_explore_e25 | 39.0 | 1.071 | 16.5 |
| wilson_loop30 | flood_fill | 39.8 | 1.279 | 19.427 |
| wilson_loop30 | repeated_astar | 36.6 | 1.192 | 18.12 |
| wilson_loop30 | turn_aware_astar | 39.8 | 1.279 | 19.427 |
| ALL | bounded_explore_e0 | 197.044 | 1.0 | 54.016 |
| ALL | bounded_explore_e10 | 187.241 | 1.013 | 54.395 |
| ALL | bounded_explore_e25 | 178.175 | 1.046 | 55.509 |
| ALL | flood_fill | 155.071 | 1.218 | 61.374 |
| ALL | repeated_astar | 150.087 | 1.207 | 60.92 |
| ALL | turn_aware_astar | 154.115 | 1.216 | 61.004 |
