# 规则：基础规则 + 转弯代价（λ = 1）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 10/10 | 102.8 | 1.188 | 1.0 | 1.7547 | 67.5 | 12.9 | 0.107 |  |
| backtracker_loop0 | dstar_lite | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.494 | 272 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 26.738 |  |
| backtracker_loop0 | frontier | 10/10 | 102.6 | 1.183 | 1.0 | 1.7547 | 67.3 | 12.8 | 0.367 | 107.5 |
| backtracker_loop0 | greedy_dfs | 10/10 | 94.2 | 1.125 | 1.036 | 1.6918 | 62.5 | 8.6 | 0.455 |  |
| backtracker_loop0 | prior_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 7.567 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 2.032 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 12.279 | 1088.3 |
| backtracker_loop0 | turn_aware_astar_w2 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 8.212 | 934.6 |
| backtracker_loop0 | wall_follower_left | 10/10 | 116.2 | 1.466 | 1.26 | 2.439 | 78.9 | 19.6 | 0.208 |  |
| backtracker_loop10 | dfs | 10/10 | 93.8 | 5.131 | 2.382 | 19.8125 | 64.6 | 20.9 | 0.079 |  |
| backtracker_loop10 | dstar_lite | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.51 | 109.3 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 9.017 |  |
| backtracker_loop10 | frontier | 10/10 | 64.7 | 3.339 | 2.03 | 11.0 | 44.2 | 4.8 | 0.165 | 67.3 |
| backtracker_loop10 | greedy_dfs | 10/10 | 40.7 | 2.12 | 1.692 | 4.6875 | 27.3 | 5.8 | 0.16 |  |
| backtracker_loop10 | prior_astar | 10/10 | 25.8 | 1.298 | 1.177 | 2.04 | 18.3 | 1.3 | 1.88 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 0.502 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 32.3 | 1.699 | 1.395 | 3.6875 | 21.5 | 2.1 | 3.059 | 237.4 |
| backtracker_loop10 | turn_aware_astar_w2 | 10/10 | 31.7 | 1.662 | 1.395 | 3.6875 | 21.5 | 1.8 | 1.726 | 144.2 |
| backtracker_loop10 | wall_follower_left | 3/10 | 87.667 | 5.068 | 1.833 | 11.6875 | 50.667 | 14.333 | 0.304 |  |
| backtracker_loop30 | dfs | 10/10 | 165.4 | 10.264 | 9.783 | 17.8571 | 109.6 | 35.1 | 0.206 |  |
| backtracker_loop30 | dstar_lite | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.278 | 90.3 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 6.824 |  |
| backtracker_loop30 | frontier | 10/10 | 114.6 | 7.352 | 8.339 | 11.5 | 70.9 | 13.6 | 0.647 | 138.2 |
| backtracker_loop30 | greedy_dfs | 10/10 | 25.2 | 1.619 | 1.355 | 4.1875 | 13.7 | 0.8 | 0.111 |  |
| backtracker_loop30 | prior_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.264 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.353 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 1.786 | 104.1 |
| backtracker_loop30 | turn_aware_astar_w2 | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 0.999 | 54.4 |
| backtracker_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.164 |  |
| external | dfs | 315/315 | 249.13 | 5.039 | 4.532 | 26.2857 | 139.937 | 81.933 | 0.38 |  |
| external | dstar_lite | 315/315 | 115.99 | 2.269 | 1.81 | 28.1429 | 64.898 | 20.87 | 6.008 | 412.321 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 38.273 |  |
| external | frontier | 315/315 | 233.213 | 4.675 | 4.03 | 25.5714 | 130.549 | 64.022 | 1.208 | 329.435 |
| external | greedy_dfs | 315/315 | 164.863 | 3.185 | 2.54 | 31.4286 | 93.492 | 43.575 | 0.779 |  |
| external | prior_astar | 315/315 | 130.108 | 2.409 | 2.167 | 19.4211 | 75.984 | 34.41 | 10.918 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 2.622 |  |
| external | turn_aware_astar | 315/315 | 119.771 | 2.328 | 1.9 | 30.1429 | 64.489 | 20.832 | 16.901 | 1809.346 |
| external | turn_aware_astar_w2 | 315/315 | 119.686 | 2.276 | 1.944 | 29.7143 | 64.679 | 22.01 | 13.097 | 1643.81 |
| external | wall_follower_left | 71/315 | 128.366 | 2.665 | 1.717 | 25.4286 | 76.803 | 25.437 | 0.196 |  |
| kruskal_loop0 | dfs | 10/10 | 162.2 | 10.279 | 6.01 | 27.8571 | 138.7 | 71 | 0.195 |  |
| kruskal_loop0 | dstar_lite | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.647 | 143.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 7.05 |  |
| kruskal_loop0 | frontier | 10/10 | 88.2 | 5.24 | 2.314 | 18.1765 | 74.7 | 34.1 | 0.219 | 111.3 |
| kruskal_loop0 | greedy_dfs | 10/10 | 35.1 | 1.82 | 1.414 | 3.56 | 24.9 | 8.6 | 0.115 |  |
| kruskal_loop0 | prior_astar | 10/10 | 32.3 | 1.703 | 1.5 | 3.32 | 25.7 | 8.2 | 2.177 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 0.538 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 2.258 | 200 |
| kruskal_loop0 | turn_aware_astar_w2 | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 1.157 | 133.2 |
| kruskal_loop0 | wall_follower_left | 10/10 | 254.3 | 15.646 | 17.187 | 27.2857 | 221.7 | 116.1 | 0.501 |  |
| kruskal_loop10 | dfs | 10/10 | 133.8 | 8.626 | 9.875 | 18.0625 | 112.3 | 41.2 | 0.234 |  |
| kruskal_loop10 | dstar_lite | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.429 | 107 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 6.877 |  |
| kruskal_loop10 | frontier | 10/10 | 115.2 | 7.309 | 5.623 | 17.0625 | 95.4 | 34.3 | 0.48 | 137.4 |
| kruskal_loop10 | greedy_dfs | 10/10 | 26.1 | 1.599 | 1.5 | 2.75 | 15.4 | 2.8 | 0.113 |  |
| kruskal_loop10 | prior_astar | 10/10 | 25.4 | 1.577 | 1.5 | 2.8571 | 19.1 | 4.3 | 1.938 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 0.481 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 2.08 | 142.4 |
| kruskal_loop10 | turn_aware_astar_w2 | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 1.138 | 79 |
| kruskal_loop10 | wall_follower_left | 2/10 | 215 | 14.021 | 14.021 | 15.5714 | 191 | 66 | 0.451 |  |
| kruskal_loop30 | dfs | 10/10 | 166.5 | 11.348 | 11.658 | 19.875 | 128.9 | 47.8 | 0.212 |  |
| kruskal_loop30 | dstar_lite | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.183 | 86.8 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 6.345 |  |
| kruskal_loop30 | frontier | 10/10 | 84.1 | 5.822 | 5.491 | 13.1429 | 60.4 | 11.7 | 0.391 | 93.4 |
| kruskal_loop30 | greedy_dfs | 10/10 | 19.7 | 1.362 | 1.232 | 1.9286 | 10.2 | 1.6 | 0.097 |  |
| kruskal_loop30 | prior_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.207 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.344 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.739 | 99.8 |
| kruskal_loop30 | turn_aware_astar_w2 | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 0.897 | 50.9 |
| kruskal_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.243 |  |
| prim_loop0 | dfs | 10/10 | 181.7 | 11.87 | 13.424 | 15.5556 | 148.4 | 82.9 | 0.269 |  |
| prim_loop0 | dstar_lite | 10/10 | 91.6 | 5.997 | 7.078 | 9.0 | 67.1 | 38.7 | 5.877 | 349.4 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 29.208 |  |
| prim_loop0 | frontier | 10/10 | 173.3 | 11.298 | 12.419 | 15.5556 | 140.9 | 78.9 | 0.896 | 221.3 |
| prim_loop0 | greedy_dfs | 10/10 | 148 | 9.612 | 9.744 | 24.0 | 116.7 | 66.3 | 0.84 |  |
| prim_loop0 | prior_astar | 10/10 | 71.6 | 4.664 | 4.756 | 8.4286 | 52.1 | 28.5 | 4.004 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 1.678 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 82.6 | 5.387 | 5.933 | 9.1429 | 55.1 | 33.6 | 10.678 | 937.5 |
| prim_loop0 | turn_aware_astar_w2 | 10/10 | 73.6 | 4.751 | 4.029 | 7.9333 | 48.9 | 29.1 | 3.35 | 758.2 |
| prim_loop0 | wall_follower_left | 10/10 | 209.3 | 13.732 | 13.491 | 18.0714 | 177.5 | 96.7 | 0.353 |  |
| prim_loop10 | dfs | 10/10 | 172.2 | 11.81 | 11.549 | 20.7333 | 137.8 | 64.4 | 0.234 |  |
| prim_loop10 | dstar_lite | 10/10 | 57.8 | 3.953 | 3.4 | 7.6667 | 40 | 17.9 | 2.852 | 225.3 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 14.54 |  |
| prim_loop10 | frontier | 10/10 | 148.5 | 10.214 | 10.483 | 13.5714 | 118.7 | 52.2 | 0.802 | 191.5 |
| prim_loop10 | greedy_dfs | 10/10 | 80.7 | 5.531 | 2.929 | 18.4286 | 58.7 | 27.6 | 0.219 |  |
| prim_loop10 | prior_astar | 10/10 | 57.1 | 3.9 | 3.533 | 7.1429 | 40.7 | 17.9 | 2.785 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 0.891 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.9 | 3.19 | 2.871 | 7.5333 | 27.5 | 12.8 | 3.668 | 426.4 |
| prim_loop10 | turn_aware_astar_w2 | 10/10 | 47.1 | 3.203 | 2.871 | 7.5333 | 27.3 | 13.4 | 2.625 | 311.5 |
| prim_loop10 | wall_follower_left | 6/10 | 149.5 | 10.429 | 10.607 | 13.1429 | 126.167 | 52.5 | 0.298 |  |
| prim_loop30 | dfs | 10/10 | 132.5 | 9.425 | 10.679 | 14.5714 | 98.7 | 30.7 | 0.193 |  |
| prim_loop30 | dstar_lite | 10/10 | 26.4 | 1.854 | 1.624 | 2.8667 | 15.2 | 3.5 | 1.367 | 110.9 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 7.854 |  |
| prim_loop30 | frontier | 10/10 | 125 | 8.89 | 10.036 | 13.4286 | 90.9 | 25.3 | 0.663 | 141.5 |
| prim_loop30 | greedy_dfs | 10/10 | 51 | 3.564 | 2.0 | 11.0714 | 32.2 | 13.4 | 0.155 |  |
| prim_loop30 | prior_astar | 10/10 | 25.8 | 1.819 | 1.624 | 3.3571 | 14.2 | 3.8 | 0.915 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.357 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.3 | 3.6 | 1.619 | 131.4 |
| prim_loop30 | turn_aware_astar_w2 | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.3 | 3.6 | 1.14 | 93.9 |
| prim_loop30 | wall_follower_left | 2/10 | 73.5 | 5.11 | 5.11 | 6.2857 | 56.5 | 13.5 | 0.215 |  |
| wilson_loop0 | dfs | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.18 |  |
| wilson_loop0 | dstar_lite | 10/10 | 70.2 | 3.031 | 1.762 | 9.0 | 54.2 | 24.5 | 2.792 | 287.3 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 30.136 |  |
| wilson_loop0 | frontier | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.629 | 182.9 |
| wilson_loop0 | greedy_dfs | 10/10 | 164.9 | 7.764 | 6.292 | 24.7857 | 130.9 | 69.2 | 0.696 |  |
| wilson_loop0 | prior_astar | 10/10 | 68.2 | 2.856 | 1.905 | 5.4167 | 53.8 | 24.3 | 5.059 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 1.191 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 109.9 | 5.503 | 4.214 | 19.2143 | 81.1 | 42 | 14.364 | 1845.6 |
| wilson_loop0 | turn_aware_astar_w2 | 10/10 | 94.6 | 4.746 | 2.373 | 14.8571 | 69.4 | 35.1 | 8.349 | 1269.1 |
| wilson_loop0 | wall_follower_left | 10/10 | 149.1 | 6.282 | 5.453 | 13.3333 | 126.5 | 62 | 0.254 |  |
| wilson_loop10 | dfs | 10/10 | 221.5 | 12.638 | 13.026 | 25.4286 | 175.7 | 76.5 | 0.337 |  |
| wilson_loop10 | dstar_lite | 10/10 | 39.5 | 2.102 | 1.771 | 3.4444 | 29.6 | 7 | 1.935 | 161.4 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 12.763 |  |
| wilson_loop10 | frontier | 10/10 | 181.9 | 10.085 | 9.042 | 17.1429 | 141.2 | 55 | 1.004 | 212.6 |
| wilson_loop10 | greedy_dfs | 10/10 | 51.5 | 2.838 | 1.821 | 8.6667 | 35.7 | 11.5 | 0.169 |  |
| wilson_loop10 | prior_astar | 10/10 | 35.4 | 1.845 | 1.804 | 3.1053 | 25.6 | 7 | 2.135 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 0.698 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.5 | 2.312 | 1.768 | 5.2222 | 27.8 | 6.7 | 2.794 | 545.2 |
| wilson_loop10 | turn_aware_astar_w2 | 10/10 | 40.3 | 2.202 | 1.976 | 4.3571 | 26.6 | 7.4 | 1.82 | 244.5 |
| wilson_loop10 | wall_follower_left | 2/10 | 144 | 4.287 | 4.287 | 6.6842 | 112.5 | 44 | 0.428 |  |
| wilson_loop30 | dfs | 10/10 | 204.6 | 14.432 | 14.929 | 17.4286 | 147 | 49.9 | 0.261 |  |
| wilson_loop30 | dstar_lite | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.311 | 89.5 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 6.986 |  |
| wilson_loop30 | frontier | 10/10 | 146.2 | 10.34 | 11.0 | 16.4286 | 102.9 | 27.8 | 0.735 | 174.9 |
| wilson_loop30 | greedy_dfs | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 0.11 |  |
| wilson_loop30 | prior_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.098 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.337 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 2.13 | 102.5 |
| wilson_loop30 | turn_aware_astar_w2 | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 1.177 | 62.2 |
| wilson_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.222 |  |
| ALL | dfs | 435/435 | 223.653 | 6.248 | 5.0 | 27.8571 | 134.605 | 72.961 | 0.315 |  |
| ALL | dstar_lite | 435/435 | 95.66 | 2.256 | 1.714 | 28.1429 | 55.17 | 17.586 | 5.208 | 345.308 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 31.254 |  |
| ALL | frontier | 435/435 | 203.099 | 5.388 | 4.467 | 25.5714 | 120.411 | 55.789 | 0.96 | 279.471 |
| ALL | greedy_dfs | 435/435 | 136.844 | 3.238 | 2.263 | 31.4286 | 80.083 | 36.554 | 0.632 |  |
| ALL | prior_astar | 435/435 | 105.223 | 2.313 | 2.018 | 19.4211 | 62.756 | 27.193 | 8.07 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 2.11 |  |
| ALL | turn_aware_astar | 435/435 | 99.055 | 2.339 | 1.841 | 30.1429 | 54.621 | 17.692 | 12.959 | 1444.943 |
| ALL | turn_aware_astar_w2 | 435/435 | 98.375 | 2.266 | 1.885 | 29.7143 | 54.315 | 18.306 | 10.364 | 1285.418 |
| ALL | wall_follower_left | 126/435 | 146.254 | 5.437 | 2.246 | 27.2857 | 104.19 | 42.5 | 0.213 |  |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 170.3 | 1.19 | 1.0 | 1.7704 |
| backtracker_loop0 | dstar_lite | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | frontier | 169.9 | 1.184 | 1.0 | 1.7704 |
| backtracker_loop0 | greedy_dfs | 156.7 | 1.13 | 1.04 | 1.6926 |
| backtracker_loop0 | prior_astar | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar_w2 | 127.5 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | wall_follower_left | 195.1 | 1.482 | 1.291 | 2.5245 |
| backtracker_loop10 | dfs | 158.4 | 5.185 | 2.595 | 19.75 |
| backtracker_loop10 | dstar_lite | 46.4 | 1.442 | 1.195 | 2.75 |
| backtracker_loop10 | flood_fill | 54.4 | 1.731 | 1.26 | 4.3214 |
| backtracker_loop10 | frontier | 108.9 | 3.355 | 2.304 | 10.8571 |
| backtracker_loop10 | greedy_dfs | 68.0 | 2.143 | 1.857 | 4.3929 |
| backtracker_loop10 | prior_astar | 44.1 | 1.36 | 1.195 | 2.1905 |
| backtracker_loop10 | repeated_astar | 46.4 | 1.442 | 1.195 | 2.75 |
| backtracker_loop10 | turn_aware_astar | 53.8 | 1.712 | 1.529 | 3.4643 |
| backtracker_loop10 | turn_aware_astar_w2 | 53.2 | 1.688 | 1.42 | 3.4643 |
| backtracker_loop10 | wall_follower_left | 138.333 | 5.057 | 1.85 | 11.72 |
| backtracker_loop30 | dfs | 275.0 | 11.633 | 11.0 | 19.5882 |
| backtracker_loop30 | dstar_lite | 34.4 | 1.498 | 1.488 | 2.0476 |
| backtracker_loop30 | flood_fill | 31.7 | 1.401 | 1.344 | 1.8571 |
| backtracker_loop30 | frontier | 185.5 | 8.1 | 9.682 | 12.1905 |
| backtracker_loop30 | greedy_dfs | 38.9 | 1.729 | 1.344 | 5.0 |
| backtracker_loop30 | prior_astar | 34.4 | 1.498 | 1.488 | 2.0476 |
| backtracker_loop30 | repeated_astar | 34.4 | 1.498 | 1.488 | 2.0476 |
| backtracker_loop30 | turn_aware_astar | 32.1 | 1.419 | 1.344 | 1.9091 |
| backtracker_loop30 | turn_aware_astar_w2 | 32.1 | 1.419 | 1.344 | 1.9091 |
| backtracker_loop30 | wall_follower_left |  |  |  |  |
| external | dfs | 389.067 | 5.471 | 4.927 | 23.7778 |
| external | dstar_lite | 180.889 | 2.467 | 1.949 | 40.0 |
| external | flood_fill | 185.156 | 2.505 | 2.021 | 40.1176 |
| external | frontier | 363.762 | 5.054 | 4.29 | 23.1852 |
| external | greedy_dfs | 258.356 | 3.455 | 2.722 | 29.1111 |
| external | prior_astar | 206.092 | 2.666 | 2.325 | 23.5882 |
| external | repeated_astar | 178.698 | 2.399 | 1.951 | 26.0 |
| external | turn_aware_astar | 184.26 | 2.498 | 1.986 | 40.1176 |
| external | turn_aware_astar_w2 | 184.365 | 2.434 | 2.048 | 27.3333 |
| external | wall_follower_left | 205.169 | 2.867 | 1.911 | 23.037 |
| kruskal_loop0 | dfs | 300.9 | 12.69 | 6.279 | 36.5 |
| kruskal_loop0 | dstar_lite | 57.4 | 1.912 | 1.85 | 3.2927 |
| kruskal_loop0 | flood_fill | 51.0 | 1.676 | 1.461 | 3.3902 |
| kruskal_loop0 | frontier | 162.9 | 6.573 | 2.571 | 24.4167 |
| kruskal_loop0 | greedy_dfs | 60.0 | 1.938 | 1.461 | 3.6829 |
| kruskal_loop0 | prior_astar | 58.0 | 1.925 | 1.85 | 3.5366 |
| kruskal_loop0 | repeated_astar | 57.4 | 1.912 | 1.85 | 3.2927 |
| kruskal_loop0 | turn_aware_astar | 51.4 | 1.688 | 1.461 | 3.3902 |
| kruskal_loop0 | turn_aware_astar_w2 | 51.4 | 1.688 | 1.461 | 3.3902 |
| kruskal_loop0 | wall_follower_left | 476.0 | 19.201 | 20.193 | 35.1 |
| kruskal_loop10 | dfs | 246.1 | 10.513 | 12.083 | 23.8182 |
| kruskal_loop10 | dstar_lite | 43.6 | 1.743 | 1.73 | 2.6364 |
| kruskal_loop10 | flood_fill | 37.9 | 1.491 | 1.416 | 2.2083 |
| kruskal_loop10 | frontier | 210.6 | 8.857 | 6.199 | 22.5455 |
| kruskal_loop10 | greedy_dfs | 41.5 | 1.619 | 1.503 | 2.875 |
| kruskal_loop10 | prior_astar | 44.5 | 1.781 | 1.73 | 2.9167 |
| kruskal_loop10 | repeated_astar | 43.6 | 1.743 | 1.73 | 2.6364 |
| kruskal_loop10 | turn_aware_astar | 38.7 | 1.521 | 1.503 | 2.2083 |
| kruskal_loop10 | turn_aware_astar_w2 | 38.7 | 1.521 | 1.503 | 2.2083 |
| kruskal_loop10 | wall_follower_left | 406.0 | 18.592 | 18.592 | 20.1 |
| kruskal_loop30 | dfs | 295.4 | 15.009 | 14.869 | 29.2353 |
| kruskal_loop30 | dstar_lite | 31.7 | 1.6 | 1.476 | 2.6364 |
| kruskal_loop30 | flood_fill | 31.2 | 1.595 | 1.417 | 3.1667 |
| kruskal_loop30 | frontier | 144.5 | 7.477 | 6.668 | 16.5 |
| kruskal_loop30 | greedy_dfs | 29.9 | 1.523 | 1.417 | 2.4444 |
| kruskal_loop30 | prior_astar | 31.7 | 1.6 | 1.476 | 2.6364 |
| kruskal_loop30 | repeated_astar | 31.7 | 1.6 | 1.476 | 2.6364 |
| kruskal_loop30 | turn_aware_astar | 31.2 | 1.595 | 1.417 | 3.1667 |
| kruskal_loop30 | turn_aware_astar_w2 | 31.2 | 1.595 | 1.417 | 3.1667 |
| kruskal_loop30 | wall_follower_left |  |  |  |  |
| prim_loop0 | dfs | 330.1 | 14.667 | 17.05 | 20.44 |
| prim_loop0 | dstar_lite | 158.7 | 7.044 | 7.847 | 10.619 |
| prim_loop0 | flood_fill | 132.1 | 5.777 | 6.4 | 10.3333 |
| prim_loop0 | frontier | 314.2 | 13.907 | 13.937 | 20.44 |
| prim_loop0 | greedy_dfs | 264.7 | 11.493 | 11.287 | 26.8261 |
| prim_loop0 | prior_astar | 123.7 | 5.486 | 5.542 | 9.7 |
| prim_loop0 | repeated_astar | 153.5 | 6.818 | 7.491 | 10.9048 |
| prim_loop0 | turn_aware_astar | 137.7 | 6.052 | 6.407 | 10.5238 |
| prim_loop0 | turn_aware_astar_w2 | 122.5 | 5.383 | 4.043 | 10.3333 |
| prim_loop0 | wall_follower_left | 386.8 | 17.236 | 17.275 | 22.4 |
| prim_loop10 | dfs | 310.0 | 15.036 | 14.477 | 27.25 |
| prim_loop10 | dstar_lite | 97.8 | 4.645 | 4.25 | 9.5714 |
| prim_loop10 | flood_fill | 76.9 | 3.609 | 3.2 | 9.6667 |
| prim_loop10 | frontier | 267.2 | 12.893 | 11.941 | 17.9524 |
| prim_loop10 | greedy_dfs | 139.4 | 6.607 | 3.462 | 22.7 |
| prim_loop10 | prior_astar | 97.8 | 4.61 | 4.204 | 8.4 |
| prim_loop10 | repeated_astar | 98.8 | 4.686 | 4.25 | 9.7619 |
| prim_loop10 | turn_aware_astar | 74.4 | 3.492 | 3.025 | 9.2857 |
| prim_loop10 | turn_aware_astar_w2 | 74.4 | 3.491 | 3.025 | 9.0952 |
| prim_loop10 | wall_follower_left | 275.667 | 13.939 | 15.094 | 17.1765 |
| prim_loop30 | dfs | 231.2 | 12.605 | 13.472 | 22.5 |
| prim_loop30 | dstar_lite | 41.6 | 2.16 | 1.857 | 3.5238 |
| prim_loop30 | flood_fill | 39.9 | 2.091 | 1.859 | 3.2381 |
| prim_loop30 | frontier | 215.9 | 11.741 | 12.716 | 20.25 |
| prim_loop30 | greedy_dfs | 83.2 | 4.252 | 2.421 | 13.0 |
| prim_loop30 | prior_astar | 40.0 | 2.108 | 1.857 | 4.4118 |
| prim_loop30 | repeated_astar | 39.0 | 2.036 | 1.857 | 3.0 |
| prim_loop30 | turn_aware_astar | 39.8 | 2.086 | 1.859 | 3.2381 |
| prim_loop30 | turn_aware_astar_w2 | 39.8 | 2.086 | 1.859 | 3.2381 |
| prim_loop30 | wall_follower_left | 130.0 | 6.576 | 6.576 | 8.1053 |
| wilson_loop0 | dfs | 262.4 | 7.124 | 6.819 | 15.1176 |
| wilson_loop0 | dstar_lite | 124.4 | 3.545 | 1.986 | 10.1765 |
| wilson_loop0 | flood_fill | 160.2 | 5.13 | 2.411 | 16.1304 |
| wilson_loop0 | frontier | 262.4 | 7.124 | 6.819 | 15.1176 |
| wilson_loop0 | greedy_dfs | 295.8 | 8.871 | 7.117 | 27.6087 |
| wilson_loop0 | prior_astar | 122.0 | 3.345 | 2.176 | 6.8095 |
| wilson_loop0 | repeated_astar | 116.8 | 3.433 | 1.986 | 10.1765 |
| wilson_loop0 | turn_aware_astar | 191.0 | 6.089 | 4.717 | 20.7391 |
| wilson_loop0 | turn_aware_astar_w2 | 164.0 | 5.241 | 2.729 | 15.7826 |
| wilson_loop0 | wall_follower_left | 275.6 | 7.487 | 6.622 | 15.4103 |
| wilson_loop10 | dfs | 397.2 | 14.796 | 14.296 | 31.7619 |
| wilson_loop10 | dstar_lite | 69.1 | 2.38 | 2.006 | 4.1 |
| wilson_loop10 | flood_fill | 72.1 | 2.626 | 2.262 | 4.9048 |
| wilson_loop10 | frontier | 323.1 | 11.729 | 10.848 | 20.3333 |
| wilson_loop10 | greedy_dfs | 87.2 | 3.112 | 2.059 | 9.5862 |
| wilson_loop10 | prior_astar | 61.0 | 2.053 | 2.006 | 3.3125 |
| wilson_loop10 | repeated_astar | 66.6 | 2.294 | 2.006 | 4.1 |
| wilson_loop10 | turn_aware_astar | 70.3 | 2.472 | 2.024 | 5.5517 |
| wilson_loop10 | turn_aware_astar_w2 | 66.9 | 2.381 | 2.15 | 4.9048 |
| wilson_loop10 | wall_follower_left | 256.5 | 5.134 | 5.134 | 8.0536 |
| wilson_loop30 | dfs | 351.6 | 18.205 | 17.441 | 23.2222 |
| wilson_loop30 | dstar_lite | 30.5 | 1.584 | 1.611 | 2.2632 |
| wilson_loop30 | flood_fill | 31.9 | 1.65 | 1.515 | 3.1579 |
| wilson_loop30 | frontier | 249.1 | 12.974 | 14.469 | 19.0 |
| wilson_loop30 | greedy_dfs | 32.8 | 1.7 | 1.515 | 3.1579 |
| wilson_loop30 | prior_astar | 30.5 | 1.584 | 1.611 | 2.2632 |
| wilson_loop30 | repeated_astar | 30.5 | 1.584 | 1.611 | 2.2632 |
| wilson_loop30 | turn_aware_astar | 32.8 | 1.7 | 1.515 | 3.1579 |
| wilson_loop30 | turn_aware_astar_w2 | 32.8 | 1.7 | 1.515 | 3.1579 |
| wilson_loop30 | wall_follower_left |  |  |  |  |
| ALL | dfs | 358.257 | 7.149 | 5.462 | 36.5 |
| ALL | dstar_lite | 150.83 | 2.489 | 1.913 | 40.0 |
| ALL | flood_fill | 153.545 | 2.498 | 1.942 | 40.1176 |
| ALL | frontier | 323.51 | 6.095 | 5.0 | 24.4167 |
| ALL | greedy_dfs | 216.926 | 3.562 | 2.44 | 29.1111 |
| ALL | prior_astar | 167.979 | 2.582 | 2.192 | 23.5882 |
| ALL | repeated_astar | 148.855 | 2.428 | 1.938 | 26.0 |
| ALL | turn_aware_astar | 153.676 | 2.518 | 1.916 | 40.1176 |
| ALL | turn_aware_astar_w2 | 152.69 | 2.433 | 1.956 | 27.3333 |
| ALL | wall_follower_left | 250.444 | 6.484 | 2.26 | 35.1 |
