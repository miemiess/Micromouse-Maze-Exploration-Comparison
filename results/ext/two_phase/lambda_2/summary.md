# 规则：基础规则 + 转弯代价（λ = 2） + 两阶段比赛（探索折算系数 = 30）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | bounded_explore_e0 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 40.295 | 1725.2 |
| backtracker_loop0 | bounded_explore_e10 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 40.138 | 1725.2 |
| backtracker_loop0 | bounded_explore_e25 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 40.466 | 1725.2 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 51.062 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.332 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 27.255 | 986.7 |
| backtracker_loop10 | bounded_explore_e0 | 10/10 | 80.8 | 4.132 | 4.503 | 6.48 | 52.8 | 16 | 207.084 | 14271.4 |
| backtracker_loop10 | bounded_explore_e10 | 10/10 | 69.2 | 3.666 | 4.477 | 5.7857 | 45.1 | 12.2 | 165.335 | 10138.1 |
| backtracker_loop10 | bounded_explore_e25 | 10/10 | 62 | 3.279 | 3.345 | 5.7857 | 40.1 | 8.7 | 120.284 | 8709.4 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 17.648 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.095 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 32.3 | 1.699 | 1.395 | 3.6875 | 21.5 | 2.1 | 6.716 | 232.1 |
| backtracker_loop30 | bounded_explore_e0 | 10/10 | 52.4 | 3.329 | 2.964 | 5.3571 | 31 | 9.1 | 100.413 | 7099 |
| backtracker_loop30 | bounded_explore_e10 | 10/10 | 44.8 | 2.843 | 2.33 | 5.3571 | 26 | 6.6 | 62.959 | 5355.5 |
| backtracker_loop30 | bounded_explore_e25 | 10/10 | 40.5 | 2.596 | 2.33 | 5.3571 | 23.2 | 5.3 | 53.939 | 4213.8 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 13.465 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.74 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 4.205 | 103.7 |
| external | bounded_explore_e0 | 315/315 | 245.346 | 4.761 | 4.31 | 31.0714 | 127.562 | 81.381 | 1621.016 | 90141.752 |
| external | bounded_explore_e10 | 315/315 | 221.06 | 4.295 | 3.949 | 31.0714 | 116.81 | 65.552 | 1401.372 | 76715.041 |
| external | bounded_explore_e25 | 315/315 | 194.908 | 3.783 | 3.383 | 31.0714 | 104.752 | 51.4 | 968.739 | 58689.06 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 74.134 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 5.57 |  |
| external | turn_aware_astar | 315/315 | 120.87 | 2.339 | 1.931 | 30.1429 | 64.552 | 21.114 | 37.554 | 1716.403 |
| kruskal_loop0 | bounded_explore_e0 | 10/10 | 77.5 | 4.05 | 3.871 | 7.7143 | 56.3 | 34.1 | 158.44 | 7867.9 |
| kruskal_loop0 | bounded_explore_e10 | 10/10 | 70.9 | 3.649 | 3.266 | 7.1429 | 51.2 | 30.1 | 104.258 | 6839.1 |
| kruskal_loop0 | bounded_explore_e25 | 10/10 | 53.5 | 2.794 | 2.063 | 6.8571 | 37.9 | 19.4 | 67.206 | 3929.5 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 14.131 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.263 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 5.181 | 195.5 |
| kruskal_loop10 | bounded_explore_e0 | 10/10 | 70.6 | 4.271 | 4.423 | 6.8889 | 46.7 | 25.1 | 146.923 | 6953.8 |
| kruskal_loop10 | bounded_explore_e10 | 10/10 | 61 | 3.705 | 3.781 | 6.6111 | 39.6 | 20.5 | 102.156 | 5248.3 |
| kruskal_loop10 | bounded_explore_e25 | 10/10 | 48.9 | 2.981 | 2.432 | 6.4286 | 30.4 | 13.4 | 59.928 | 3877 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 14.249 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.079 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 5.043 | 139.3 |
| kruskal_loop30 | bounded_explore_e0 | 10/10 | 42.9 | 2.926 | 2.921 | 4.5625 | 22.5 | 11.6 | 56.569 | 2205 |
| kruskal_loop30 | bounded_explore_e10 | 10/10 | 37.1 | 2.531 | 2.607 | 3.9375 | 18.4 | 8.8 | 46.972 | 1627.1 |
| kruskal_loop30 | bounded_explore_e25 | 10/10 | 30 | 2.032 | 1.786 | 3.9375 | 15.6 | 6 | 29.113 | 1130.9 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 12.444 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.771 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 4.088 | 98.9 |
| prim_loop0 | bounded_explore_e0 | 10/10 | 108.5 | 7.114 | 7.971 | 9.1429 | 73.9 | 47.8 | 100.08 | 5416.8 |
| prim_loop0 | bounded_explore_e10 | 10/10 | 100 | 6.53 | 7.573 | 9.1429 | 67.3 | 42.3 | 68.367 | 4199.1 |
| prim_loop0 | bounded_explore_e25 | 10/10 | 88.5 | 5.756 | 6.381 | 9.1429 | 59.1 | 35.8 | 47.026 | 1966.7 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 56.611 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 3.65 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 86 | 5.582 | 6.215 | 9.1429 | 57.5 | 35.5 | 24.806 | 1163.6 |
| prim_loop10 | bounded_explore_e0 | 10/10 | 88.8 | 6.022 | 5.05 | 13.8 | 55.1 | 30.9 | 109.59 | 9855.1 |
| prim_loop10 | bounded_explore_e10 | 10/10 | 79.7 | 5.386 | 4.143 | 13.6 | 48.5 | 25.9 | 68.362 | 8411.6 |
| prim_loop10 | bounded_explore_e25 | 10/10 | 55.7 | 3.768 | 3.305 | 7.5333 | 33.7 | 15.5 | 27.994 | 2841.8 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 28.598 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 1.894 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.9 | 3.19 | 2.871 | 7.5333 | 27.5 | 12.8 | 7.807 | 413.2 |
| prim_loop30 | bounded_explore_e0 | 10/10 | 55.9 | 3.919 | 3.929 | 6.1333 | 29.7 | 11.3 | 118.025 | 6214.7 |
| prim_loop30 | bounded_explore_e10 | 10/10 | 49 | 3.43 | 3.607 | 6.1333 | 25.7 | 9.7 | 94.974 | 4693.6 |
| prim_loop30 | bounded_explore_e25 | 10/10 | 41 | 2.868 | 2.571 | 5.4667 | 21.5 | 7 | 62.414 | 3306.1 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 15.601 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.846 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.3 | 3.6 | 3.556 | 129.4 |
| wilson_loop0 | bounded_explore_e0 | 10/10 | 147.7 | 6.911 | 5.683 | 19.7857 | 109.1 | 66.8 | 142.382 | 14273.8 |
| wilson_loop0 | bounded_explore_e10 | 10/10 | 140.7 | 6.642 | 5.509 | 19.7857 | 103.6 | 62.8 | 101.445 | 12698.2 |
| wilson_loop0 | bounded_explore_e25 | 10/10 | 119.1 | 5.624 | 4.274 | 19.4286 | 87.5 | 48.7 | 77.25 | 9266.8 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 57.368 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 2.57 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 94.3 | 4.794 | 3.016 | 19.2143 | 69.7 | 34.2 | 21.75 | 1495.9 |
| wilson_loop10 | bounded_explore_e0 | 10/10 | 91.1 | 4.83 | 5.001 | 7.4583 | 59.4 | 26.7 | 158.241 | 14622.2 |
| wilson_loop10 | bounded_explore_e10 | 10/10 | 85 | 4.51 | 4.475 | 6.7083 | 55.8 | 23.4 | 124.496 | 13035.8 |
| wilson_loop10 | bounded_explore_e25 | 10/10 | 70.5 | 3.724 | 3.75 | 6.4583 | 47.2 | 18.1 | 71.965 | 9718.9 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 25.31 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 1.521 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.5 | 2.312 | 1.768 | 5.2222 | 27.8 | 6.7 | 5.838 | 511.2 |
| wilson_loop30 | bounded_explore_e0 | 10/10 | 48 | 3.396 | 3.381 | 5.6429 | 24.1 | 8.1 | 87.014 | 3991.1 |
| wilson_loop30 | bounded_explore_e10 | 10/10 | 39.5 | 2.802 | 2.714 | 5.1429 | 19.5 | 5 | 57.834 | 2882.1 |
| wilson_loop30 | bounded_explore_e25 | 10/10 | 37.5 | 2.663 | 2.607 | 4.7143 | 18.8 | 4.6 | 51.672 | 2592.3 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 13.174 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.776 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 4.705 | 97.9 |
| ALL | bounded_explore_e0 | 435/435 | 199.301 | 4.641 | 4.257 | 31.0714 | 106.421 | 65.54 | 1016.995 | 67447.384 |
| ALL | bounded_explore_e10 | 435/435 | 179.708 | 4.183 | 3.853 | 31.0714 | 97.257 | 53.154 | 801.769 | 57319.023 |
| ALL | bounded_explore_e25 | 435/435 | 157.789 | 3.638 | 3.318 | 31.0714 | 86.556 | 41.416 | 559.348 | 43723.766 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 59.726 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 4.627 |  |
| ALL | turn_aware_astar | 435/435 | 99.57 | 2.335 | 1.842 | 30.1429 | 54.46 | 17.761 | 29.154 | 1370.899 |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | bounded_explore_e0 | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | bounded_explore_e10 | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | bounded_explore_e25 | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop10 | bounded_explore_e0 | 186.4 | 4.282 | 4.865 | 6.75 |
| backtracker_loop10 | bounded_explore_e10 | 159.4 | 3.816 | 4.865 | 6.75 |
| backtracker_loop10 | bounded_explore_e25 | 142.2 | 3.39 | 3.352 | 6.75 |
| backtracker_loop10 | flood_fill | 76.5 | 1.747 | 1.262 | 4.225 |
| backtracker_loop10 | repeated_astar | 65.3 | 1.459 | 1.192 | 2.675 |
| backtracker_loop10 | turn_aware_astar | 75.3 | 1.72 | 1.519 | 3.375 |
| backtracker_loop30 | bounded_explore_e0 | 114.4 | 3.735 | 3.555 | 5.9643 |
| backtracker_loop30 | bounded_explore_e10 | 96.8 | 3.168 | 2.964 | 5.9643 |
| backtracker_loop30 | bounded_explore_e25 | 86.9 | 2.877 | 2.9 | 5.9643 |
| backtracker_loop30 | flood_fill | 42.5 | 1.445 | 1.404 | 1.8571 |
| backtracker_loop30 | repeated_astar | 47.7 | 1.595 | 1.58 | 2.1852 |
| backtracker_loop30 | turn_aware_astar | 43.1 | 1.466 | 1.404 | 2.0714 |
| external | bounded_explore_e0 | 500.47 | 5.24 | 4.79 | 50.8947 |
| external | bounded_explore_e10 | 454.679 | 4.776 | 4.38 | 50.8947 |
| external | bounded_explore_e25 | 404.413 | 4.251 | 3.783 | 50.8947 |
| external | flood_fill | 250.121 | 2.647 | 2.103 | 50.1053 |
| external | repeated_astar | 243.14 | 2.544 | 2.03 | 30.2105 |
| external | turn_aware_astar | 249.975 | 2.64 | 2.092 | 50.1053 |
| kruskal_loop0 | bounded_explore_e0 | 190.1 | 4.457 | 4.293 | 8.2857 |
| kruskal_loop0 | bounded_explore_e10 | 173.3 | 3.975 | 3.616 | 7.6327 |
| kruskal_loop0 | bounded_explore_e25 | 129.3 | 3.033 | 2.187 | 7.3061 |
| kruskal_loop0 | flood_fill | 72.3 | 1.726 | 1.481 | 3.4912 |
| kruskal_loop0 | repeated_astar | 82.7 | 2.014 | 1.987 | 3.386 |
| kruskal_loop0 | turn_aware_astar | 72.9 | 1.74 | 1.481 | 3.4912 |
| kruskal_loop10 | bounded_explore_e0 | 164.0 | 4.645 | 5.102 | 7.5789 |
| kruskal_loop10 | bounded_explore_e10 | 140.2 | 3.982 | 4.183 | 7.2368 |
| kruskal_loop10 | bounded_explore_e25 | 109.7 | 3.084 | 2.438 | 6.3158 |
| kruskal_loop10 | flood_fill | 51.7 | 1.504 | 1.409 | 2.1905 |
| kruskal_loop10 | repeated_astar | 62.0 | 1.849 | 1.857 | 3.0357 |
| kruskal_loop10 | turn_aware_astar | 52.8 | 1.534 | 1.488 | 2.3333 |
| kruskal_loop30 | bounded_explore_e0 | 87.9 | 3.444 | 3.45 | 5.4643 |
| kruskal_loop30 | bounded_explore_e10 | 73.9 | 2.93 | 2.781 | 4.7619 |
| kruskal_loop30 | bounded_explore_e25 | 61.2 | 2.412 | 2.11 | 4.5714 |
| kruskal_loop30 | flood_fill | 42.0 | 1.723 | 1.536 | 3.8095 |
| kruskal_loop30 | repeated_astar | 44.0 | 1.769 | 1.65 | 3.0 |
| kruskal_loop30 | turn_aware_astar | 42.0 | 1.723 | 1.536 | 3.8095 |
| prim_loop0 | bounded_explore_e0 | 256.3 | 8.626 | 8.747 | 13.4444 |
| prim_loop0 | bounded_explore_e10 | 234.6 | 7.848 | 8.428 | 12.3704 |
| prim_loop0 | bounded_explore_e25 | 206.7 | 6.927 | 6.809 | 12.2593 |
| prim_loop0 | flood_fill | 184.8 | 6.136 | 6.6 | 11.6667 |
| prim_loop0 | repeated_astar | 218.8 | 7.429 | 7.893 | 12.4074 |
| prim_loop0 | turn_aware_astar | 201.0 | 6.713 | 6.6 | 12.2593 |
| prim_loop10 | bounded_explore_e0 | 199.0 | 7.373 | 5.712 | 19.16 |
| prim_loop10 | bounded_explore_e10 | 176.7 | 6.517 | 4.944 | 18.8 |
| prim_loop10 | bounded_explore_e25 | 123.1 | 4.43 | 3.31 | 10.2593 |
| prim_loop10 | flood_fill | 105.9 | 3.841 | 3.364 | 10.7037 |
| prim_loop10 | repeated_astar | 139.8 | 5.153 | 4.811 | 11.0 |
| prim_loop10 | turn_aware_astar | 101.9 | 3.697 | 3.124 | 10.2593 |
| prim_loop30 | bounded_explore_e0 | 115.3 | 4.822 | 4.794 | 7.3333 |
| prim_loop30 | bounded_explore_e10 | 100.4 | 4.199 | 4.069 | 7.3333 |
| prim_loop30 | bounded_explore_e25 | 84.0 | 3.535 | 3.204 | 6.2963 |
| prim_loop30 | flood_fill | 53.3 | 2.286 | 2.077 | 3.6316 |
| prim_loop30 | repeated_astar | 53.0 | 2.255 | 2.074 | 3.6316 |
| prim_loop30 | turn_aware_astar | 53.1 | 2.278 | 2.077 | 3.6316 |
| wilson_loop0 | bounded_explore_e0 | 365.9 | 8.111 | 6.675 | 21.9062 |
| wilson_loop0 | bounded_explore_e10 | 347.9 | 7.755 | 6.644 | 21.9062 |
| wilson_loop0 | bounded_explore_e25 | 294.1 | 6.486 | 5.028 | 21.5625 |
| wilson_loop0 | flood_fill | 228.4 | 5.371 | 2.553 | 16.6875 |
| wilson_loop0 | repeated_astar | 167.6 | 3.688 | 2.104 | 10.7826 |
| wilson_loop0 | turn_aware_astar | 233.7 | 5.534 | 3.656 | 21.4062 |
| wilson_loop10 | bounded_explore_e0 | 209.9 | 5.292 | 5.044 | 7.5741 |
| wilson_loop10 | bounded_explore_e10 | 196.6 | 4.941 | 4.862 | 7.3571 |
| wilson_loop10 | bounded_explore_e25 | 164.9 | 4.117 | 3.783 | 6.6111 |
| wilson_loop10 | flood_fill | 101.4 | 2.757 | 2.389 | 5.1786 |
| wilson_loop10 | repeated_astar | 94.9 | 2.425 | 2.125 | 4.5 |
| wilson_loop10 | turn_aware_astar | 98.1 | 2.554 | 2.16 | 5.7 |
| wilson_loop30 | bounded_explore_e0 | 96.2 | 4.068 | 4.14 | 6.4783 |
| wilson_loop30 | bounded_explore_e10 | 78.5 | 3.34 | 3.0 | 6.087 |
| wilson_loop30 | bounded_explore_e25 | 75.1 | 3.193 | 2.942 | 5.5652 |
| wilson_loop30 | flood_fill | 42.1 | 1.758 | 1.541 | 3.4783 |
| wilson_loop30 | repeated_astar | 41.3 | 1.735 | 1.682 | 2.7391 |
| wilson_loop30 | turn_aware_astar | 43.2 | 1.808 | 1.541 | 3.4783 |
| ALL | bounded_explore_e0 | 412.143 | 5.171 | 4.754 | 50.8947 |
| ALL | bounded_explore_e10 | 374.223 | 4.688 | 4.316 | 50.8947 |
| ALL | bounded_explore_e25 | 330.901 | 4.101 | 3.675 | 50.8947 |
| ALL | flood_fill | 208.223 | 2.636 | 2.03 | 50.1053 |
| ALL | repeated_astar | 203.54 | 2.586 | 2.014 | 30.2105 |
| ALL | turn_aware_astar | 208.49 | 2.642 | 2.027 | 50.1053 |

两阶段比赛（成功运行；探索代价含返回起点，冲刺/最优的分母为已知地图上的最优冲刺代价）：

| 地图组 | 算法 | 平均探索代价 | 冲刺/最优（均值） | 平均成绩 |
| --- | --- | --- | --- | --- |
| backtracker_loop0 | bounded_explore_e0 | 359.4 | 1.0 | 189.98 |
| backtracker_loop0 | bounded_explore_e10 | 359.4 | 1.0 | 189.98 |
| backtracker_loop0 | bounded_explore_e25 | 359.4 | 1.0 | 189.98 |
| backtracker_loop0 | flood_fill | 359.4 | 1.0 | 189.98 |
| backtracker_loop0 | repeated_astar | 359.4 | 1.0 | 189.98 |
| backtracker_loop0 | turn_aware_astar | 359.4 | 1.0 | 189.98 |
| backtracker_loop10 | bounded_explore_e0 | 221.8 | 1.0 | 52.293 |
| backtracker_loop10 | bounded_explore_e10 | 199.8 | 1.01 | 51.96 |
| backtracker_loop10 | bounded_explore_e25 | 185.0 | 1.017 | 51.767 |
| backtracker_loop10 | flood_fill | 139.6 | 1.321 | 64.353 |
| backtracker_loop10 | repeated_astar | 128.0 | 1.305 | 63.567 |
| backtracker_loop10 | turn_aware_astar | 142.6 | 1.426 | 68.653 |
| backtracker_loop30 | bounded_explore_e0 | 142.0 | 1.0 | 34.633 |
| backtracker_loop30 | bounded_explore_e10 | 127.6 | 1.015 | 34.553 |
| backtracker_loop30 | bounded_explore_e25 | 111.2 | 1.015 | 34.007 |
| backtracker_loop30 | flood_fill | 82.4 | 1.237 | 39.047 |
| backtracker_loop30 | repeated_astar | 90.4 | 1.322 | 42.113 |
| backtracker_loop30 | turn_aware_astar | 83.0 | 1.237 | 39.067 |
| external | bounded_explore_e0 | 550.762 | 1.0 | 124.616 |
| external | bounded_explore_e10 | 514.622 | 1.017 | 125.341 |
| external | bounded_explore_e25 | 479.137 | 1.054 | 128.047 |
| external | flood_fill | 385.657 | 1.28 | 144.392 |
| external | repeated_astar | 379.67 | 1.292 | 145.186 |
| external | turn_aware_astar | 385.994 | 1.283 | 144.886 |
| kruskal_loop0 | bounded_explore_e0 | 222.8 | 1.0 | 46.327 |
| kruskal_loop0 | bounded_explore_e10 | 208.6 | 1.0 | 45.853 |
| kruskal_loop0 | bounded_explore_e25 | 171.0 | 1.0 | 44.6 |
| kruskal_loop0 | flood_fill | 114.4 | 1.0 | 42.713 |
| kruskal_loop0 | repeated_astar | 124.8 | 1.0 | 43.06 |
| kruskal_loop0 | turn_aware_astar | 115.0 | 1.0 | 42.733 |
| kruskal_loop10 | bounded_explore_e0 | 189.6 | 1.0 | 40.42 |
| kruskal_loop10 | bounded_explore_e10 | 172.0 | 1.008 | 40.133 |
| kruskal_loop10 | bounded_explore_e25 | 143.2 | 1.008 | 39.173 |
| kruskal_loop10 | flood_fill | 92.0 | 1.079 | 40.167 |
| kruskal_loop10 | repeated_astar | 103.2 | 1.126 | 41.44 |
| kruskal_loop10 | turn_aware_astar | 94.2 | 1.114 | 41.34 |
| kruskal_loop30 | bounded_explore_e0 | 108.4 | 1.0 | 28.813 |
| kruskal_loop30 | bounded_explore_e10 | 92.0 | 1.0 | 28.267 |
| kruskal_loop30 | bounded_explore_e25 | 84.6 | 1.034 | 28.72 |
| kruskal_loop30 | flood_fill | 73.8 | 1.141 | 30.86 |
| kruskal_loop30 | repeated_astar | 74.4 | 1.099 | 29.88 |
| kruskal_loop30 | turn_aware_astar | 73.8 | 1.141 | 30.86 |
| prim_loop0 | bounded_explore_e0 | 288.8 | 1.0 | 39.327 |
| prim_loop0 | bounded_explore_e10 | 266.6 | 1.0 | 38.587 |
| prim_loop0 | bounded_explore_e25 | 238.6 | 1.0 | 37.653 |
| prim_loop0 | flood_fill | 218.2 | 1.012 | 37.273 |
| prim_loop0 | repeated_astar | 252.0 | 1.003 | 38.2 |
| prim_loop0 | turn_aware_astar | 234.4 | 1.012 | 37.813 |
| prim_loop10 | bounded_explore_e0 | 226.0 | 1.0 | 34.233 |
| prim_loop10 | bounded_explore_e10 | 206.6 | 1.008 | 33.787 |
| prim_loop10 | bounded_explore_e25 | 150.4 | 1.051 | 32.913 |
| prim_loop10 | flood_fill | 139.6 | 1.109 | 34.553 |
| prim_loop10 | repeated_astar | 179.8 | 1.345 | 42.193 |
| prim_loop10 | turn_aware_astar | 136.0 | 1.125 | 34.833 |
| prim_loop30 | bounded_explore_e0 | 135.2 | 1.0 | 27.807 |
| prim_loop30 | bounded_explore_e10 | 122.0 | 1.008 | 27.567 |
| prim_loop30 | bounded_explore_e25 | 102.0 | 1.03 | 27.5 |
| prim_loop30 | flood_fill | 85.0 | 1.207 | 30.733 |
| prim_loop30 | repeated_astar | 86.6 | 1.297 | 32.687 |
| prim_loop30 | turn_aware_astar | 85.2 | 1.223 | 31.14 |
| wilson_loop0 | bounded_explore_e0 | 400.6 | 1.0 | 62.553 |
| wilson_loop0 | bounded_explore_e10 | 384.0 | 1.0 | 62.0 |
| wilson_loop0 | bounded_explore_e25 | 343.0 | 1.0 | 60.633 |
| wilson_loop0 | flood_fill | 283.8 | 1.038 | 62.06 |
| wilson_loop0 | repeated_astar | 219.6 | 1.0 | 56.52 |
| wilson_loop0 | turn_aware_astar | 292.4 | 1.141 | 65.647 |
| wilson_loop10 | bounded_explore_e0 | 237.6 | 1.0 | 48.72 |
| wilson_loop10 | bounded_explore_e10 | 224.2 | 1.01 | 48.773 |
| wilson_loop10 | bounded_explore_e25 | 197.0 | 1.014 | 48.067 |
| wilson_loop10 | flood_fill | 164.0 | 1.599 | 65.267 |
| wilson_loop10 | repeated_astar | 147.4 | 1.278 | 54.613 |
| wilson_loop10 | turn_aware_astar | 154.8 | 1.426 | 59.06 |
| wilson_loop30 | bounded_explore_e0 | 117.0 | 1.0 | 28.0 |
| wilson_loop30 | bounded_explore_e10 | 99.6 | 1.018 | 27.82 |
| wilson_loop30 | bounded_explore_e25 | 94.8 | 1.045 | 28.26 |
| wilson_loop30 | flood_fill | 77.2 | 1.342 | 34.673 |
| wilson_loop30 | repeated_astar | 74.4 | 1.261 | 32.58 |
| wilson_loop30 | turn_aware_astar | 79.4 | 1.392 | 35.847 |
| ALL | bounded_explore_e0 | 459.729 | 1.0 | 104.793 |
| ALL | bounded_explore_e10 | 429.264 | 1.014 | 105.231 |
| ALL | bounded_explore_e25 | 397.08 | 1.044 | 107.052 |
| ALL | flood_fill | 321.324 | 1.251 | 120.0 |
| ALL | repeated_astar | 317.232 | 1.258 | 120.464 |
| ALL | turn_aware_astar | 322.046 | 1.257 | 120.48 |
