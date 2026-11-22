# 规则：基础规则 + 运动时间模型（最高速 = 0.5 m/s，转 90° = 0.3 s）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 10/10 | 102.8 | 1.188 | 1.0 | 1.7547 | 67.5 | 12.9 | 0.119 |  |
| backtracker_loop0 | dstar_lite | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.744 | 272 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 28.831 |  |
| backtracker_loop0 | frontier | 10/10 | 102.6 | 1.183 | 1.0 | 1.7547 | 67.3 | 12.8 | 0.418 | 107.5 |
| backtracker_loop0 | greedy_dfs | 10/10 | 94.2 | 1.125 | 1.036 | 1.6918 | 62.5 | 8.6 | 0.454 |  |
| backtracker_loop0 | prior_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 8.014 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 2.1 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 13.186 | 1112.1 |
| backtracker_loop0 | turn_aware_astar_w2 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 9.587 | 950.2 |
| backtracker_loop0 | wall_follower_left | 10/10 | 116.2 | 1.466 | 1.26 | 2.439 | 78.9 | 19.6 | 0.317 |  |
| backtracker_loop10 | dfs | 10/10 | 93.8 | 5.131 | 2.382 | 19.8125 | 64.6 | 20.9 | 0.107 |  |
| backtracker_loop10 | dstar_lite | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.631 | 109.3 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 9.808 |  |
| backtracker_loop10 | frontier | 10/10 | 64.7 | 3.339 | 2.03 | 11.0 | 44.2 | 4.8 | 0.176 | 67.3 |
| backtracker_loop10 | greedy_dfs | 10/10 | 40.7 | 2.12 | 1.692 | 4.6875 | 27.3 | 5.8 | 0.169 |  |
| backtracker_loop10 | prior_astar | 10/10 | 25.8 | 1.298 | 1.177 | 2.04 | 18.3 | 1.3 | 2.091 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 0.546 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 30.9 | 1.616 | 1.257 | 3.6875 | 21.1 | 1.4 | 2.89 | 207.7 |
| backtracker_loop10 | turn_aware_astar_w2 | 10/10 | 30.9 | 1.616 | 1.257 | 3.6875 | 21.1 | 1.4 | 2.033 | 141.5 |
| backtracker_loop10 | wall_follower_left | 3/10 | 87.667 | 5.068 | 1.833 | 11.6875 | 50.667 | 14.333 | 0.344 |  |
| backtracker_loop30 | dfs | 10/10 | 165.4 | 10.264 | 9.783 | 17.8571 | 109.6 | 35.1 | 0.217 |  |
| backtracker_loop30 | dstar_lite | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.329 | 90.3 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 7.499 |  |
| backtracker_loop30 | frontier | 10/10 | 114.6 | 7.352 | 8.339 | 11.5 | 70.9 | 13.6 | 0.715 | 138.2 |
| backtracker_loop30 | greedy_dfs | 10/10 | 25.2 | 1.619 | 1.355 | 4.1875 | 13.7 | 0.8 | 0.131 |  |
| backtracker_loop30 | prior_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.352 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.378 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 1.856 | 90.8 |
| backtracker_loop30 | turn_aware_astar_w2 | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 1.22 | 54.4 |
| backtracker_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.171 |  |
| external | dfs | 315/315 | 249.13 | 5.039 | 4.532 | 26.2857 | 139.937 | 81.933 | 0.416 |  |
| external | dstar_lite | 315/315 | 115.99 | 2.269 | 1.81 | 28.1429 | 64.898 | 20.87 | 6.237 | 412.321 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 40.059 |  |
| external | frontier | 315/315 | 233.213 | 4.675 | 4.03 | 25.5714 | 130.549 | 64.022 | 1.299 | 329.435 |
| external | greedy_dfs | 315/315 | 164.863 | 3.185 | 2.54 | 31.4286 | 93.492 | 43.575 | 0.827 |  |
| external | prior_astar | 315/315 | 130.108 | 2.409 | 2.167 | 19.4211 | 75.984 | 34.41 | 11.282 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 2.756 |  |
| external | turn_aware_astar | 315/315 | 120.629 | 2.339 | 1.939 | 29.7143 | 64.978 | 21.244 | 19.503 | 1917.273 |
| external | turn_aware_astar_w2 | 315/315 | 119.61 | 2.282 | 1.962 | 29.7143 | 64.775 | 21.81 | 15.663 | 1709.314 |
| external | wall_follower_left | 71/315 | 128.366 | 2.665 | 1.717 | 25.4286 | 76.803 | 25.437 | 0.214 |  |
| kruskal_loop0 | dfs | 10/10 | 162.2 | 10.279 | 6.01 | 27.8571 | 138.7 | 71 | 0.206 |  |
| kruskal_loop0 | dstar_lite | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.888 | 143.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 8.038 |  |
| kruskal_loop0 | frontier | 10/10 | 88.2 | 5.24 | 2.314 | 18.1765 | 74.7 | 34.1 | 0.247 | 111.3 |
| kruskal_loop0 | greedy_dfs | 10/10 | 35.1 | 1.82 | 1.414 | 3.56 | 24.9 | 8.6 | 0.137 |  |
| kruskal_loop0 | prior_astar | 10/10 | 32.3 | 1.703 | 1.5 | 3.32 | 25.7 | 8.2 | 2.474 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 0.6 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 3.068 | 187.5 |
| kruskal_loop0 | turn_aware_astar_w2 | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 1.879 | 132.1 |
| kruskal_loop0 | wall_follower_left | 10/10 | 254.3 | 15.646 | 17.187 | 27.2857 | 221.7 | 116.1 | 0.629 |  |
| kruskal_loop10 | dfs | 10/10 | 133.8 | 8.626 | 9.875 | 18.0625 | 112.3 | 41.2 | 0.26 |  |
| kruskal_loop10 | dstar_lite | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.8 | 107 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 7.454 |  |
| kruskal_loop10 | frontier | 10/10 | 115.2 | 7.309 | 5.623 | 17.0625 | 95.4 | 34.3 | 0.593 | 137.4 |
| kruskal_loop10 | greedy_dfs | 10/10 | 26.1 | 1.599 | 1.5 | 2.75 | 15.4 | 2.8 | 0.141 |  |
| kruskal_loop10 | prior_astar | 10/10 | 25.4 | 1.577 | 1.5 | 2.8571 | 19.1 | 4.3 | 2.093 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 0.518 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 2.455 | 127.2 |
| kruskal_loop10 | turn_aware_astar_w2 | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 1.892 | 78.2 |
| kruskal_loop10 | wall_follower_left | 2/10 | 215 | 14.021 | 14.021 | 15.5714 | 191 | 66 | 0.542 |  |
| kruskal_loop30 | dfs | 10/10 | 166.5 | 11.348 | 11.658 | 19.875 | 128.9 | 47.8 | 0.313 |  |
| kruskal_loop30 | dstar_lite | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.266 | 86.8 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 7.245 |  |
| kruskal_loop30 | frontier | 10/10 | 84.1 | 5.822 | 5.491 | 13.1429 | 60.4 | 11.7 | 0.459 | 93.4 |
| kruskal_loop30 | greedy_dfs | 10/10 | 19.7 | 1.362 | 1.232 | 1.9286 | 10.2 | 1.6 | 0.12 |  |
| kruskal_loop30 | prior_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.353 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.393 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.926 | 88.9 |
| kruskal_loop30 | turn_aware_astar_w2 | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.098 | 51.4 |
| kruskal_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.281 |  |
| prim_loop0 | dfs | 10/10 | 181.7 | 11.87 | 13.424 | 15.5556 | 148.4 | 82.9 | 0.321 |  |
| prim_loop0 | dstar_lite | 10/10 | 91.6 | 5.997 | 7.078 | 9.0 | 67.1 | 38.7 | 6.398 | 349.4 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 33.058 |  |
| prim_loop0 | frontier | 10/10 | 173.3 | 11.298 | 12.419 | 15.5556 | 140.9 | 78.9 | 1.032 | 221.3 |
| prim_loop0 | greedy_dfs | 10/10 | 148 | 9.612 | 9.744 | 24.0 | 116.7 | 66.3 | 0.868 |  |
| prim_loop0 | prior_astar | 10/10 | 71.6 | 4.664 | 4.756 | 8.4286 | 52.1 | 28.5 | 4.446 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 1.78 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 82 | 5.317 | 5.533 | 9.2857 | 54.5 | 33.3 | 9.841 | 1119.4 |
| prim_loop0 | turn_aware_astar_w2 | 10/10 | 74.4 | 4.776 | 4.171 | 8.5556 | 49.5 | 29.5 | 4.936 | 914.2 |
| prim_loop0 | wall_follower_left | 10/10 | 209.3 | 13.732 | 13.491 | 18.0714 | 177.5 | 96.7 | 0.439 |  |
| prim_loop10 | dfs | 10/10 | 172.2 | 11.81 | 11.549 | 20.7333 | 137.8 | 64.4 | 0.306 |  |
| prim_loop10 | dstar_lite | 10/10 | 57.8 | 3.953 | 3.4 | 7.6667 | 40 | 17.9 | 3.554 | 225.3 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 16.398 |  |
| prim_loop10 | frontier | 10/10 | 148.5 | 10.214 | 10.483 | 13.5714 | 118.7 | 52.2 | 0.891 | 191.5 |
| prim_loop10 | greedy_dfs | 10/10 | 80.7 | 5.531 | 2.929 | 18.4286 | 58.7 | 27.6 | 0.295 |  |
| prim_loop10 | prior_astar | 10/10 | 57.1 | 3.9 | 3.533 | 7.1429 | 40.7 | 17.9 | 3.649 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 1.018 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.3 | 3.15 | 2.871 | 7.0 | 27 | 12.6 | 4.465 | 433.7 |
| prim_loop10 | turn_aware_astar_w2 | 10/10 | 46.9 | 3.189 | 2.871 | 7.5333 | 27 | 13.4 | 3.332 | 309.7 |
| prim_loop10 | wall_follower_left | 6/10 | 149.5 | 10.429 | 10.607 | 13.1429 | 126.167 | 52.5 | 0.399 |  |
| prim_loop30 | dfs | 10/10 | 132.5 | 9.425 | 10.679 | 14.5714 | 98.7 | 30.7 | 0.209 |  |
| prim_loop30 | dstar_lite | 10/10 | 26.4 | 1.854 | 1.624 | 2.8667 | 15.2 | 3.5 | 1.568 | 110.9 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 9.398 |  |
| prim_loop30 | frontier | 10/10 | 125 | 8.89 | 10.036 | 13.4286 | 90.9 | 25.3 | 0.734 | 141.5 |
| prim_loop30 | greedy_dfs | 10/10 | 51 | 3.564 | 2.0 | 11.0714 | 32.2 | 13.4 | 0.171 |  |
| prim_loop30 | prior_astar | 10/10 | 25.8 | 1.819 | 1.624 | 3.3571 | 14.2 | 3.8 | 1.088 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.399 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 2.186 | 135 |
| prim_loop30 | turn_aware_astar_w2 | 10/10 | 26.3 | 1.849 | 1.607 | 2.7333 | 13 | 3.6 | 1.428 | 94.6 |
| prim_loop30 | wall_follower_left | 2/10 | 73.5 | 5.11 | 5.11 | 6.2857 | 56.5 | 13.5 | 0.247 |  |
| wilson_loop0 | dfs | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.213 |  |
| wilson_loop0 | dstar_lite | 10/10 | 70.2 | 3.031 | 1.762 | 9.0 | 54.2 | 24.5 | 3.013 | 287.3 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 31.891 |  |
| wilson_loop0 | frontier | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.679 | 182.9 |
| wilson_loop0 | greedy_dfs | 10/10 | 164.9 | 7.764 | 6.292 | 24.7857 | 130.9 | 69.2 | 0.794 |  |
| wilson_loop0 | prior_astar | 10/10 | 68.2 | 2.856 | 1.905 | 5.4167 | 53.8 | 24.3 | 5.646 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 1.315 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 94.3 | 4.803 | 2.043 | 17.0714 | 69.3 | 34.2 | 12.021 | 1533 |
| wilson_loop0 | turn_aware_astar_w2 | 10/10 | 92.6 | 4.646 | 2.127 | 14.8571 | 67.8 | 34.1 | 9.768 | 1398.5 |
| wilson_loop0 | wall_follower_left | 10/10 | 149.1 | 6.282 | 5.453 | 13.3333 | 126.5 | 62 | 0.284 |  |
| wilson_loop10 | dfs | 10/10 | 221.5 | 12.638 | 13.026 | 25.4286 | 175.7 | 76.5 | 0.382 |  |
| wilson_loop10 | dstar_lite | 10/10 | 39.5 | 2.102 | 1.771 | 3.4444 | 29.6 | 7 | 1.952 | 161.4 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 13.074 |  |
| wilson_loop10 | frontier | 10/10 | 181.9 | 10.085 | 9.042 | 17.1429 | 141.2 | 55 | 1.055 | 212.6 |
| wilson_loop10 | greedy_dfs | 10/10 | 51.5 | 2.838 | 1.821 | 8.6667 | 35.7 | 11.5 | 0.188 |  |
| wilson_loop10 | prior_astar | 10/10 | 35.4 | 1.845 | 1.804 | 3.1053 | 25.6 | 7 | 2.145 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 0.776 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 45.5 | 2.524 | 2.011 | 5.2222 | 30.9 | 8.1 | 3.491 | 592.6 |
| wilson_loop10 | turn_aware_astar_w2 | 10/10 | 42.5 | 2.361 | 2.011 | 4.3571 | 28.9 | 8.1 | 2.771 | 275.7 |
| wilson_loop10 | wall_follower_left | 2/10 | 144 | 4.287 | 4.287 | 6.6842 | 112.5 | 44 | 0.468 |  |
| wilson_loop30 | dfs | 10/10 | 204.6 | 14.432 | 14.929 | 17.4286 | 147 | 49.9 | 0.299 |  |
| wilson_loop30 | dstar_lite | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.373 | 89.5 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 7.654 |  |
| wilson_loop30 | frontier | 10/10 | 146.2 | 10.34 | 11.0 | 16.4286 | 102.9 | 27.8 | 0.789 | 174.9 |
| wilson_loop30 | greedy_dfs | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 0.121 |  |
| wilson_loop30 | prior_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.179 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.365 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 2.109 | 91.8 |
| wilson_loop30 | turn_aware_astar_w2 | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 1.3 | 62.4 |
| wilson_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.244 |  |
| ALL | dfs | 435/435 | 223.653 | 6.248 | 5.0 | 27.8571 | 134.605 | 72.961 | 0.362 |  |
| ALL | dstar_lite | 435/435 | 95.66 | 2.256 | 1.714 | 28.1429 | 55.17 | 17.586 | 5.427 | 345.308 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 32.241 |  |
| ALL | frontier | 435/435 | 203.099 | 5.388 | 4.467 | 25.5714 | 120.411 | 55.789 | 1.06 | 279.471 |
| ALL | greedy_dfs | 435/435 | 136.844 | 3.238 | 2.263 | 31.4286 | 80.083 | 36.554 | 0.669 |  |
| ALL | prior_astar | 435/435 | 105.223 | 2.313 | 2.018 | 19.4211 | 62.756 | 27.193 | 8.539 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 2.213 |  |
| ALL | turn_aware_astar | 435/435 | 99.29 | 2.328 | 1.849 | 29.7143 | 54.722 | 17.814 | 15.065 | 1519.857 |
| ALL | turn_aware_astar_w2 | 435/435 | 98.278 | 2.268 | 1.882 | 29.7143 | 54.37 | 18.149 | 12.85 | 1340.375 |
| ALL | wall_follower_left | 126/435 | 146.254 | 5.437 | 2.246 | 27.2857 | 104.19 | 42.5 | 0.243 |  |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 73.293 | 1.18 | 1.0 | 1.7306 |
| backtracker_loop0 | dstar_lite | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | frontier | 73.146 | 1.175 | 1.0 | 1.7306 |
| backtracker_loop0 | greedy_dfs | 67.657 | 1.122 | 1.034 | 1.6582 |
| backtracker_loop0 | prior_astar | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar_w2 | 55.67 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | wall_follower_left | 83.967 | 1.461 | 1.279 | 2.4901 |
| backtracker_loop10 | dfs | 67.898 | 5.035 | 2.603 | 18.8914 |
| backtracker_loop10 | dstar_lite | 20.295 | 1.436 | 1.206 | 2.6423 |
| backtracker_loop10 | flood_fill | 23.573 | 1.704 | 1.243 | 4.1142 |
| backtracker_loop10 | frontier | 47.007 | 3.279 | 2.344 | 10.433 |
| backtracker_loop10 | greedy_dfs | 29.387 | 2.105 | 1.849 | 4.1713 |
| backtracker_loop10 | prior_astar | 19.283 | 1.358 | 1.206 | 2.2294 |
| backtracker_loop10 | repeated_astar | 20.295 | 1.436 | 1.206 | 2.6423 |
| backtracker_loop10 | turn_aware_astar | 22.589 | 1.626 | 1.243 | 3.3339 |
| backtracker_loop10 | turn_aware_astar_w2 | 22.589 | 1.626 | 1.243 | 3.3339 |
| backtracker_loop10 | wall_follower_left | 58.66 | 4.961 | 1.842 | 11.5005 |
| backtracker_loop30 | dfs | 116.524 | 11.639 | 10.916 | 19.3916 |
| backtracker_loop30 | dstar_lite | 14.936 | 1.536 | 1.508 | 2.0581 |
| backtracker_loop30 | flood_fill | 13.524 | 1.414 | 1.36 | 1.8459 |
| backtracker_loop30 | frontier | 78.736 | 8.12 | 9.506 | 12.346 |
| backtracker_loop30 | greedy_dfs | 16.632 | 1.748 | 1.36 | 5.0827 |
| backtracker_loop30 | prior_astar | 14.936 | 1.536 | 1.508 | 2.0581 |
| backtracker_loop30 | repeated_astar | 14.936 | 1.536 | 1.508 | 2.0581 |
| backtracker_loop30 | turn_aware_astar | 13.524 | 1.414 | 1.36 | 1.8459 |
| backtracker_loop30 | turn_aware_astar_w2 | 13.524 | 1.414 | 1.36 | 1.8459 |
| backtracker_loop30 | wall_follower_left |  |  |  |  |
| external | dfs | 160.874 | 5.41 | 4.818 | 21.8834 |
| external | dstar_lite | 75.477 | 2.463 | 1.941 | 42.9185 |
| external | flood_fill | 77.007 | 2.493 | 2.009 | 43.0252 |
| external | frontier | 150.652 | 5.004 | 4.278 | 21.6163 |
| external | greedy_dfs | 107.093 | 3.421 | 2.715 | 26.8127 |
| external | prior_astar | 85.951 | 2.664 | 2.323 | 25.9067 |
| external | repeated_astar | 74.635 | 2.395 | 1.952 | 26.1067 |
| external | turn_aware_astar | 77.189 | 2.496 | 2.004 | 43.0252 |
| external | turn_aware_astar_w2 | 76.652 | 2.426 | 2.042 | 25.1415 |
| external | wall_follower_left | 85.47 | 2.824 | 1.898 | 21.7793 |
| kruskal_loop0 | dfs | 126.697 | 12.492 | 5.968 | 35.8207 |
| kruskal_loop0 | dstar_lite | 24.596 | 1.879 | 1.841 | 3.1812 |
| kruskal_loop0 | flood_fill | 21.742 | 1.638 | 1.416 | 3.2626 |
| kruskal_loop0 | frontier | 69.022 | 6.525 | 2.509 | 24.7884 |
| kruskal_loop0 | greedy_dfs | 25.421 | 1.882 | 1.416 | 3.5036 |
| kruskal_loop0 | prior_astar | 24.853 | 1.892 | 1.841 | 3.4033 |
| kruskal_loop0 | repeated_astar | 24.596 | 1.879 | 1.841 | 3.1812 |
| kruskal_loop0 | turn_aware_astar | 21.742 | 1.638 | 1.416 | 3.2626 |
| kruskal_loop0 | turn_aware_astar_w2 | 21.742 | 1.638 | 1.416 | 3.2626 |
| kruskal_loop0 | wall_follower_left | 200.113 | 18.767 | 19.376 | 34.5041 |
| kruskal_loop10 | dfs | 103.948 | 10.334 | 12.031 | 23.6939 |
| kruskal_loop10 | dstar_lite | 18.632 | 1.723 | 1.743 | 2.6702 |
| kruskal_loop10 | flood_fill | 15.951 | 1.449 | 1.382 | 2.0612 |
| kruskal_loop10 | frontier | 89.147 | 8.708 | 5.997 | 22.4791 |
| kruskal_loop10 | greedy_dfs | 17.516 | 1.58 | 1.481 | 2.8274 |
| kruskal_loop10 | prior_astar | 19.054 | 1.762 | 1.743 | 2.7572 |
| kruskal_loop10 | repeated_astar | 18.632 | 1.723 | 1.743 | 2.6702 |
| kruskal_loop10 | turn_aware_astar | 15.951 | 1.449 | 1.382 | 2.0612 |
| kruskal_loop10 | turn_aware_astar_w2 | 15.951 | 1.449 | 1.382 | 2.0612 |
| kruskal_loop10 | wall_follower_left | 172.775 | 18.709 | 18.709 | 19.9278 |
| kruskal_loop30 | dfs | 125.085 | 15.363 | 15.35 | 30.4409 |
| kruskal_loop30 | dstar_lite | 13.459 | 1.638 | 1.547 | 2.6122 |
| kruskal_loop30 | flood_fill | 13.064 | 1.62 | 1.427 | 3.3674 |
| kruskal_loop30 | frontier | 61.631 | 7.724 | 6.759 | 16.4366 |
| kruskal_loop30 | greedy_dfs | 12.517 | 1.542 | 1.427 | 2.5915 |
| kruskal_loop30 | prior_astar | 13.459 | 1.638 | 1.547 | 2.6122 |
| kruskal_loop30 | repeated_astar | 13.459 | 1.638 | 1.547 | 2.6122 |
| kruskal_loop30 | turn_aware_astar | 13.064 | 1.62 | 1.427 | 3.3674 |
| kruskal_loop30 | turn_aware_astar_w2 | 13.064 | 1.62 | 1.427 | 3.3674 |
| kruskal_loop30 | wall_follower_left |  |  |  |  |
| prim_loop0 | dfs | 137.212 | 14.272 | 16.353 | 20.6583 |
| prim_loop0 | dstar_lite | 65.941 | 6.854 | 7.5 | 10.4592 |
| prim_loop0 | flood_fill | 54.399 | 5.575 | 6.044 | 10.2503 |
| prim_loop0 | frontier | 130.553 | 13.522 | 13.573 | 20.6583 |
| prim_loop0 | greedy_dfs | 109.71 | 11.156 | 10.731 | 25.7217 |
| prim_loop0 | prior_astar | 51.331 | 5.329 | 5.373 | 9.4011 |
| prim_loop0 | repeated_astar | 63.832 | 6.645 | 7.174 | 10.7464 |
| prim_loop0 | turn_aware_astar | 56.185 | 5.739 | 6.044 | 10.6912 |
| prim_loop0 | turn_aware_astar_w2 | 51.119 | 5.241 | 3.924 | 10.6912 |
| prim_loop0 | wall_follower_left | 161.473 | 16.842 | 16.798 | 22.7638 |
| prim_loop10 | dfs | 129.222 | 14.823 | 14.763 | 26.8464 |
| prim_loop10 | dstar_lite | 40.688 | 4.549 | 4.281 | 9.3911 |
| prim_loop10 | flood_fill | 31.599 | 3.487 | 3.133 | 9.5497 |
| prim_loop10 | frontier | 111.48 | 12.707 | 12.113 | 17.8335 |
| prim_loop10 | greedy_dfs | 58.027 | 6.447 | 3.447 | 22.1688 |
| prim_loop10 | prior_astar | 40.646 | 4.508 | 4.158 | 8.1257 |
| prim_loop10 | repeated_astar | 41.133 | 4.592 | 4.281 | 9.6011 |
| prim_loop10 | turn_aware_astar | 30.028 | 3.313 | 2.98 | 8.3687 |
| prim_loop10 | turn_aware_astar_w2 | 30.279 | 3.34 | 2.98 | 8.9363 |
| prim_loop10 | wall_follower_left | 115.762 | 13.935 | 15.04 | 17.7882 |
| prim_loop30 | dfs | 96.89 | 13.009 | 14.064 | 23.6448 |
| prim_loop30 | dstar_lite | 17.529 | 2.21 | 1.921 | 3.6069 |
| prim_loop30 | flood_fill | 16.505 | 2.107 | 1.86 | 3.2713 |
| prim_loop30 | frontier | 90.845 | 12.157 | 13.358 | 21.241 |
| prim_loop30 | greedy_dfs | 34.72 | 4.271 | 2.435 | 12.5553 |
| prim_loop30 | prior_astar | 16.763 | 2.154 | 1.921 | 4.6696 |
| prim_loop30 | repeated_astar | 16.4 | 2.08 | 1.921 | 3.2119 |
| prim_loop30 | turn_aware_astar | 16.505 | 2.107 | 1.86 | 3.2713 |
| prim_loop30 | turn_aware_astar_w2 | 16.248 | 2.077 | 1.86 | 3.2713 |
| prim_loop30 | wall_follower_left | 54.635 | 6.707 | 6.707 | 8.1746 |
| wilson_loop0 | dfs | 110.333 | 6.954 | 6.689 | 14.5579 |
| wilson_loop0 | dstar_lite | 52.397 | 3.476 | 1.945 | 9.7854 |
| wilson_loop0 | flood_fill | 66.965 | 4.985 | 2.356 | 15.7237 |
| wilson_loop0 | frontier | 110.333 | 6.954 | 6.689 | 14.5579 |
| wilson_loop0 | greedy_dfs | 123.599 | 8.608 | 6.826 | 26.7738 |
| wilson_loop0 | prior_astar | 51.317 | 3.276 | 2.129 | 6.8682 |
| wilson_loop0 | repeated_astar | 49.155 | 3.365 | 1.945 | 9.8111 |
| wilson_loop0 | turn_aware_astar | 68.363 | 5.137 | 2.252 | 17.6366 |
| wilson_loop0 | turn_aware_astar_w2 | 66.926 | 4.96 | 2.356 | 15.1732 |
| wilson_loop0 | wall_follower_left | 116.086 | 7.33 | 6.573 | 15.0799 |
| wilson_loop10 | dfs | 166.76 | 14.479 | 13.801 | 31.6378 |
| wilson_loop10 | dstar_lite | 29.25 | 2.338 | 1.978 | 4.0361 |
| wilson_loop10 | flood_fill | 30.098 | 2.558 | 2.212 | 4.8324 |
| wilson_loop10 | frontier | 135.664 | 11.454 | 10.709 | 20.1462 |
| wilson_loop10 | greedy_dfs | 36.435 | 3.032 | 2.038 | 9.3065 |
| wilson_loop10 | prior_astar | 25.749 | 2.011 | 1.978 | 3.1524 |
| wilson_loop10 | repeated_astar | 28.173 | 2.252 | 1.978 | 4.0361 |
| wilson_loop10 | turn_aware_astar | 31.915 | 2.701 | 2.212 | 5.3623 |
| wilson_loop10 | turn_aware_astar_w2 | 29.77 | 2.534 | 2.212 | 4.8324 |
| wilson_loop10 | wall_follower_left | 107.14 | 5.051 | 5.051 | 7.9936 |
| wilson_loop30 | dfs | 147.366 | 18.605 | 17.803 | 23.9006 |
| wilson_loop30 | dstar_lite | 12.892 | 1.634 | 1.64 | 2.3987 |
| wilson_loop30 | flood_fill | 13.282 | 1.667 | 1.538 | 3.0597 |
| wilson_loop30 | frontier | 105.097 | 13.337 | 14.678 | 19.9824 |
| wilson_loop30 | greedy_dfs | 13.644 | 1.717 | 1.538 | 3.0597 |
| wilson_loop30 | prior_astar | 12.892 | 1.634 | 1.64 | 2.3987 |
| wilson_loop30 | repeated_astar | 12.892 | 1.634 | 1.64 | 2.3987 |
| wilson_loop30 | turn_aware_astar | 13.282 | 1.667 | 1.538 | 3.0597 |
| wilson_loop30 | turn_aware_astar_w2 | 13.282 | 1.667 | 1.538 | 3.0597 |
| wilson_loop30 | wall_follower_left |  |  |  |  |
| ALL | dfs | 148.707 | 7.094 | 5.478 | 35.8207 |
| ALL | dstar_lite | 63.076 | 2.48 | 1.913 | 42.9185 |
| ALL | flood_fill | 63.956 | 2.477 | 1.92 | 43.0252 |
| ALL | frontier | 134.441 | 6.053 | 4.938 | 24.7884 |
| ALL | greedy_dfs | 90.085 | 3.516 | 2.399 | 26.8127 |
| ALL | prior_astar | 70.193 | 2.575 | 2.192 | 25.9067 |
| ALL | repeated_astar | 62.303 | 2.419 | 1.92 | 26.1067 |
| ALL | turn_aware_astar | 64.144 | 2.484 | 1.92 | 43.0252 |
| ALL | turn_aware_astar_w2 | 63.556 | 2.413 | 1.964 | 25.1415 |
| ALL | wall_follower_left | 104.955 | 6.38 | 2.226 | 34.5041 |
