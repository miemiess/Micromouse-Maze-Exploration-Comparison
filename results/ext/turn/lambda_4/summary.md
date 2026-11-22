# 规则：基础规则 + 转弯代价（λ = 4）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 10/10 | 102.8 | 1.188 | 1.0 | 1.7547 | 67.5 | 12.9 | 0.118 |  |
| backtracker_loop0 | dstar_lite | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 5.105 | 272 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 27.453 |  |
| backtracker_loop0 | frontier | 10/10 | 102.6 | 1.183 | 1.0 | 1.7547 | 67.3 | 12.8 | 0.418 | 107.5 |
| backtracker_loop0 | greedy_dfs | 10/10 | 94.2 | 1.125 | 1.036 | 1.6918 | 62.5 | 8.6 | 0.479 |  |
| backtracker_loop0 | prior_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 7.91 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 2.093 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 12.011 | 903.3 |
| backtracker_loop0 | turn_aware_astar_w2 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 8.986 | 758 |
| backtracker_loop0 | wall_follower_left | 10/10 | 116.2 | 1.466 | 1.26 | 2.439 | 78.9 | 19.6 | 0.218 |  |
| backtracker_loop10 | dfs | 10/10 | 93.8 | 5.131 | 2.382 | 19.8125 | 64.6 | 20.9 | 0.098 |  |
| backtracker_loop10 | dstar_lite | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.661 | 109.3 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 9.296 |  |
| backtracker_loop10 | frontier | 10/10 | 64.7 | 3.339 | 2.03 | 11.0 | 44.2 | 4.8 | 0.173 | 67.3 |
| backtracker_loop10 | greedy_dfs | 10/10 | 40.7 | 2.12 | 1.692 | 4.6875 | 27.3 | 5.8 | 0.166 |  |
| backtracker_loop10 | prior_astar | 10/10 | 25.8 | 1.298 | 1.177 | 2.04 | 18.3 | 1.3 | 1.978 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 0.531 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 35.9 | 1.849 | 1.692 | 3.6875 | 23.9 | 2.4 | 3.218 | 288.6 |
| backtracker_loop10 | turn_aware_astar_w2 | 10/10 | 32.3 | 1.699 | 1.395 | 3.6875 | 21.5 | 2.1 | 1.896 | 143.2 |
| backtracker_loop10 | wall_follower_left | 3/10 | 87.667 | 5.068 | 1.833 | 11.6875 | 50.667 | 14.333 | 0.344 |  |
| backtracker_loop30 | dfs | 10/10 | 165.4 | 10.264 | 9.783 | 17.8571 | 109.6 | 35.1 | 0.226 |  |
| backtracker_loop30 | dstar_lite | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.371 | 90.3 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 6.948 |  |
| backtracker_loop30 | frontier | 10/10 | 114.6 | 7.352 | 8.339 | 11.5 | 70.9 | 13.6 | 0.75 | 138.2 |
| backtracker_loop30 | greedy_dfs | 10/10 | 25.2 | 1.619 | 1.355 | 4.1875 | 13.7 | 0.8 | 0.115 |  |
| backtracker_loop30 | prior_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.314 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.369 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 24.7 | 1.588 | 1.355 | 3.875 | 13.4 | 1.1 | 1.871 | 214.9 |
| backtracker_loop30 | turn_aware_astar_w2 | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 1.018 | 53.7 |
| backtracker_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.181 |  |
| external | dfs | 315/315 | 249.13 | 5.039 | 4.532 | 26.2857 | 139.937 | 81.933 | 0.41 |  |
| external | dstar_lite | 315/315 | 115.99 | 2.269 | 1.81 | 28.1429 | 64.898 | 20.87 | 6.334 | 412.321 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 40.531 |  |
| external | frontier | 315/315 | 233.213 | 4.675 | 4.03 | 25.5714 | 130.549 | 64.022 | 1.271 | 329.435 |
| external | greedy_dfs | 315/315 | 164.863 | 3.185 | 2.54 | 31.4286 | 93.492 | 43.575 | 0.825 |  |
| external | prior_astar | 315/315 | 130.108 | 2.409 | 2.167 | 19.4211 | 75.984 | 34.41 | 11.533 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 2.795 |  |
| external | turn_aware_astar | 315/315 | 123.454 | 2.41 | 1.939 | 30.1429 | 65.378 | 22.295 | 16.671 | 1704.124 |
| external | turn_aware_astar_w2 | 315/315 | 120.537 | 2.291 | 1.938 | 29.7143 | 64.006 | 21.594 | 13.102 | 1473.737 |
| external | wall_follower_left | 71/315 | 128.366 | 2.665 | 1.717 | 25.4286 | 76.803 | 25.437 | 0.215 |  |
| kruskal_loop0 | dfs | 10/10 | 162.2 | 10.279 | 6.01 | 27.8571 | 138.7 | 71 | 0.222 |  |
| kruskal_loop0 | dstar_lite | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.656 | 143.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 7.646 |  |
| kruskal_loop0 | frontier | 10/10 | 88.2 | 5.24 | 2.314 | 18.1765 | 74.7 | 34.1 | 0.231 | 111.3 |
| kruskal_loop0 | greedy_dfs | 10/10 | 35.1 | 1.82 | 1.414 | 3.56 | 24.9 | 8.6 | 0.125 |  |
| kruskal_loop0 | prior_astar | 10/10 | 32.3 | 1.703 | 1.5 | 3.32 | 25.7 | 8.2 | 2.141 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 0.577 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 30.5 | 1.607 | 1.414 | 3.16 | 22.1 | 6.4 | 2.351 | 193.2 |
| kruskal_loop0 | turn_aware_astar_w2 | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 1.231 | 125 |
| kruskal_loop0 | wall_follower_left | 10/10 | 254.3 | 15.646 | 17.187 | 27.2857 | 221.7 | 116.1 | 0.543 |  |
| kruskal_loop10 | dfs | 10/10 | 133.8 | 8.626 | 9.875 | 18.0625 | 112.3 | 41.2 | 0.251 |  |
| kruskal_loop10 | dstar_lite | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.453 | 107 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 7.209 |  |
| kruskal_loop10 | frontier | 10/10 | 115.2 | 7.309 | 5.623 | 17.0625 | 95.4 | 34.3 | 0.532 | 137.4 |
| kruskal_loop10 | greedy_dfs | 10/10 | 26.1 | 1.599 | 1.5 | 2.75 | 15.4 | 2.8 | 0.138 |  |
| kruskal_loop10 | prior_astar | 10/10 | 25.4 | 1.577 | 1.5 | 2.8571 | 19.1 | 4.3 | 2.066 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 0.51 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 25.3 | 1.554 | 1.5 | 2.45 | 14.4 | 2.3 | 2.338 | 135.6 |
| kruskal_loop10 | turn_aware_astar_w2 | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 1.196 | 73.2 |
| kruskal_loop10 | wall_follower_left | 2/10 | 215 | 14.021 | 14.021 | 15.5714 | 191 | 66 | 0.528 |  |
| kruskal_loop30 | dfs | 10/10 | 166.5 | 11.348 | 11.658 | 19.875 | 128.9 | 47.8 | 0.229 |  |
| kruskal_loop30 | dstar_lite | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.294 | 86.8 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 6.607 |  |
| kruskal_loop30 | frontier | 10/10 | 84.1 | 5.822 | 5.491 | 13.1429 | 60.4 | 11.7 | 0.434 | 93.4 |
| kruskal_loop30 | greedy_dfs | 10/10 | 19.7 | 1.362 | 1.232 | 1.9286 | 10.2 | 1.6 | 0.103 |  |
| kruskal_loop30 | prior_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.214 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.385 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.949 | 96.5 |
| kruskal_loop30 | turn_aware_astar_w2 | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.12 | 49.4 |
| kruskal_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.268 |  |
| prim_loop0 | dfs | 10/10 | 181.7 | 11.87 | 13.424 | 15.5556 | 148.4 | 82.9 | 0.3 |  |
| prim_loop0 | dstar_lite | 10/10 | 91.6 | 5.997 | 7.078 | 9.0 | 67.1 | 38.7 | 6.195 | 349.4 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 29.245 |  |
| prim_loop0 | frontier | 10/10 | 173.3 | 11.298 | 12.419 | 15.5556 | 140.9 | 78.9 | 0.91 | 221.3 |
| prim_loop0 | greedy_dfs | 10/10 | 148 | 9.612 | 9.744 | 24.0 | 116.7 | 66.3 | 0.825 |  |
| prim_loop0 | prior_astar | 10/10 | 71.6 | 4.664 | 4.756 | 8.4286 | 52.1 | 28.5 | 3.901 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 1.764 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 86 | 5.583 | 6.215 | 9.1429 | 57.5 | 35.5 | 9.849 | 1121.8 |
| prim_loop0 | turn_aware_astar_w2 | 10/10 | 79.2 | 5.095 | 4.629 | 8.5556 | 51.9 | 32.5 | 4.561 | 962.8 |
| prim_loop0 | wall_follower_left | 10/10 | 209.3 | 13.732 | 13.491 | 18.0714 | 177.5 | 96.7 | 0.351 |  |
| prim_loop10 | dfs | 10/10 | 172.2 | 11.81 | 11.549 | 20.7333 | 137.8 | 64.4 | 0.266 |  |
| prim_loop10 | dstar_lite | 10/10 | 57.8 | 3.953 | 3.4 | 7.6667 | 40 | 17.9 | 2.787 | 225.3 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 15.299 |  |
| prim_loop10 | frontier | 10/10 | 148.5 | 10.214 | 10.483 | 13.5714 | 118.7 | 52.2 | 0.816 | 191.5 |
| prim_loop10 | greedy_dfs | 10/10 | 80.7 | 5.531 | 2.929 | 18.4286 | 58.7 | 27.6 | 0.256 |  |
| prim_loop10 | prior_astar | 10/10 | 57.1 | 3.9 | 3.533 | 7.1429 | 40.7 | 17.9 | 2.938 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 0.909 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.7 | 3.176 | 2.871 | 7.5333 | 27.1 | 12.7 | 3.346 | 392.6 |
| prim_loop10 | turn_aware_astar_w2 | 10/10 | 47.1 | 3.202 | 2.871 | 7.6667 | 26.9 | 13.1 | 2.545 | 260 |
| prim_loop10 | wall_follower_left | 6/10 | 149.5 | 10.429 | 10.607 | 13.1429 | 126.167 | 52.5 | 0.329 |  |
| prim_loop30 | dfs | 10/10 | 132.5 | 9.425 | 10.679 | 14.5714 | 98.7 | 30.7 | 0.206 |  |
| prim_loop30 | dstar_lite | 10/10 | 26.4 | 1.854 | 1.624 | 2.8667 | 15.2 | 3.5 | 1.426 | 110.9 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 8.447 |  |
| prim_loop30 | frontier | 10/10 | 125 | 8.89 | 10.036 | 13.4286 | 90.9 | 25.3 | 0.672 | 141.5 |
| prim_loop30 | greedy_dfs | 10/10 | 51 | 3.564 | 2.0 | 11.0714 | 32.2 | 13.4 | 0.157 |  |
| prim_loop30 | prior_astar | 10/10 | 25.8 | 1.819 | 1.624 | 3.3571 | 14.2 | 3.8 | 0.959 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.372 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.3 | 1.849 | 1.607 | 2.7333 | 12.9 | 3.5 | 1.57 | 118.7 |
| prim_loop30 | turn_aware_astar_w2 | 10/10 | 26.5 | 1.862 | 1.607 | 2.8667 | 12.9 | 3.3 | 1.123 | 84.8 |
| prim_loop30 | wall_follower_left | 2/10 | 73.5 | 5.11 | 5.11 | 6.2857 | 56.5 | 13.5 | 0.227 |  |
| wilson_loop0 | dfs | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.223 |  |
| wilson_loop0 | dstar_lite | 10/10 | 70.2 | 3.031 | 1.762 | 9.0 | 54.2 | 24.5 | 2.868 | 287.3 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 30.303 |  |
| wilson_loop0 | frontier | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.617 | 182.9 |
| wilson_loop0 | greedy_dfs | 10/10 | 164.9 | 7.764 | 6.292 | 24.7857 | 130.9 | 69.2 | 0.804 |  |
| wilson_loop0 | prior_astar | 10/10 | 68.2 | 2.856 | 1.905 | 5.4167 | 53.8 | 24.3 | 5.585 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 1.161 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 93.5 | 4.756 | 3.037 | 19.2143 | 68.9 | 33.7 | 8.733 | 1363 |
| wilson_loop0 | turn_aware_astar_w2 | 10/10 | 92.5 | 4.629 | 3.016 | 16.9286 | 67.7 | 33.3 | 7.162 | 1155.8 |
| wilson_loop0 | wall_follower_left | 10/10 | 149.1 | 6.282 | 5.453 | 13.3333 | 126.5 | 62 | 0.271 |  |
| wilson_loop10 | dfs | 10/10 | 221.5 | 12.638 | 13.026 | 25.4286 | 175.7 | 76.5 | 0.346 |  |
| wilson_loop10 | dstar_lite | 10/10 | 39.5 | 2.102 | 1.771 | 3.4444 | 29.6 | 7 | 2.144 | 161.4 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 12.916 |  |
| wilson_loop10 | frontier | 10/10 | 181.9 | 10.085 | 9.042 | 17.1429 | 141.2 | 55 | 1.222 | 212.6 |
| wilson_loop10 | greedy_dfs | 10/10 | 51.5 | 2.838 | 1.821 | 8.6667 | 35.7 | 11.5 | 0.194 |  |
| wilson_loop10 | prior_astar | 10/10 | 35.4 | 1.845 | 1.804 | 3.1053 | 25.6 | 7 | 2.281 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 0.681 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.5 | 2.312 | 1.768 | 5.2222 | 27.8 | 6.7 | 2.779 | 471.3 |
| wilson_loop10 | turn_aware_astar_w2 | 10/10 | 42.7 | 2.326 | 1.768 | 5.2222 | 28 | 6.8 | 1.844 | 381.2 |
| wilson_loop10 | wall_follower_left | 2/10 | 144 | 4.287 | 4.287 | 6.6842 | 112.5 | 44 | 0.445 |  |
| wilson_loop30 | dfs | 10/10 | 204.6 | 14.432 | 14.929 | 17.4286 | 147 | 49.9 | 0.295 |  |
| wilson_loop30 | dstar_lite | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.389 | 89.5 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 7.355 |  |
| wilson_loop30 | frontier | 10/10 | 146.2 | 10.34 | 11.0 | 16.4286 | 102.9 | 27.8 | 0.786 | 174.9 |
| wilson_loop30 | greedy_dfs | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 0.113 |  |
| wilson_loop30 | prior_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.126 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.36 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 2.131 | 94.8 |
| wilson_loop30 | turn_aware_astar_w2 | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 1.326 | 58.6 |
| wilson_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.242 |  |
| ALL | dfs | 435/435 | 223.653 | 6.248 | 5.0 | 27.8571 | 134.605 | 72.961 | 0.348 |  |
| ALL | dstar_lite | 435/435 | 95.66 | 2.256 | 1.714 | 28.1429 | 55.17 | 17.586 | 5.505 | 345.308 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 32.825 |  |
| ALL | frontier | 435/435 | 203.099 | 5.388 | 4.467 | 25.5714 | 120.411 | 55.789 | 1.033 | 279.471 |
| ALL | greedy_dfs | 435/435 | 136.844 | 3.238 | 2.263 | 31.4286 | 80.083 | 36.554 | 0.669 |  |
| ALL | prior_astar | 435/435 | 105.223 | 2.313 | 2.018 | 19.4211 | 62.756 | 27.193 | 8.692 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 2.259 |  |
| ALL | turn_aware_astar | 435/435 | 101.609 | 2.395 | 1.857 | 30.1429 | 55.152 | 18.616 | 13.047 | 1358.028 |
| ALL | turn_aware_astar_w2 | 435/435 | 99.14 | 2.286 | 1.857 | 29.7143 | 53.871 | 18.021 | 10.294 | 1161.572 |
| ALL | wall_follower_left | 126/435 | 146.254 | 5.437 | 2.246 | 27.2857 | 104.19 | 42.5 | 0.233 |  |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 372.8 | 1.192 | 1.0 | 1.784 |
| backtracker_loop0 | dstar_lite | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | frontier | 371.8 | 1.185 | 1.0 | 1.784 |
| backtracker_loop0 | greedy_dfs | 344.2 | 1.134 | 1.04 | 1.6933 |
| backtracker_loop0 | prior_astar | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar_w2 | 279.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | wall_follower_left | 431.8 | 1.494 | 1.319 | 2.589 |
| backtracker_loop10 | dfs | 352.2 | 5.25 | 2.795 | 19.7031 |
| backtracker_loop10 | dstar_lite | 103.1 | 1.484 | 1.229 | 2.6094 |
| backtracker_loop10 | flood_fill | 120.7 | 1.771 | 1.302 | 4.1406 |
| backtracker_loop10 | frontier | 241.5 | 3.387 | 2.572 | 10.75 |
| backtracker_loop10 | greedy_dfs | 149.9 | 2.178 | 2.029 | 4.1719 |
| backtracker_loop10 | prior_astar | 99.0 | 1.43 | 1.229 | 2.5636 |
| backtracker_loop10 | repeated_astar | 103.1 | 1.484 | 1.229 | 2.6094 |
| backtracker_loop10 | turn_aware_astar | 131.5 | 1.887 | 1.813 | 3.2969 |
| backtracker_loop10 | turn_aware_astar_w2 | 118.3 | 1.737 | 1.498 | 3.2969 |
| backtracker_loop10 | wall_follower_left | 290.333 | 5.08 | 1.864 | 11.75 |
| backtracker_loop30 | dfs | 603.8 | 13.53 | 12.838 | 21.6761 |
| backtracker_loop30 | dstar_lite | 74.3 | 1.706 | 1.7 | 2.3333 |
| backtracker_loop30 | flood_fill | 64.1 | 1.498 | 1.463 | 2.0 |
| backtracker_loop30 | frontier | 398.2 | 9.22 | 10.546 | 13.8718 |
| backtracker_loop30 | greedy_dfs | 80.0 | 1.895 | 1.463 | 5.975 |
| backtracker_loop30 | prior_astar | 74.3 | 1.706 | 1.7 | 2.3333 |
| backtracker_loop30 | repeated_astar | 74.3 | 1.706 | 1.7 | 2.3333 |
| backtracker_loop30 | turn_aware_astar | 78.3 | 1.853 | 1.463 | 5.55 |
| backtracker_loop30 | turn_aware_astar_w2 | 65.1 | 1.523 | 1.463 | 2.25 |
| backtracker_loop30 | wall_follower_left |  |  |  |  |
| external | dfs | 808.876 | 6.257 | 5.528 | 30.7826 |
| external | dstar_lite | 375.584 | 2.829 | 2.154 | 64.7826 |
| external | flood_fill | 380.051 | 2.845 | 2.196 | 64.8696 |
| external | frontier | 755.41 | 5.754 | 4.92 | 30.7826 |
| external | greedy_dfs | 538.832 | 3.94 | 3.0 | 39.3913 |
| external | prior_astar | 434.044 | 3.103 | 2.661 | 40.1304 |
| external | repeated_astar | 372.022 | 2.738 | 2.195 | 39.3913 |
| external | turn_aware_astar | 384.965 | 2.899 | 2.196 | 64.8696 |
| external | turn_aware_astar_w2 | 376.562 | 2.728 | 2.209 | 35.7826 |
| external | wall_follower_left | 435.577 | 3.246 | 2.061 | 31.1304 |
| kruskal_loop0 | dfs | 717.0 | 15.228 | 6.494 | 46.0526 |
| kruskal_loop0 | dstar_lite | 133.3 | 2.113 | 2.121 | 3.4719 |
| kruskal_loop0 | flood_fill | 114.9 | 1.774 | 1.5 | 3.5843 |
| kruskal_loop0 | frontier | 387.0 | 8.027 | 2.778 | 31.4889 |
| kruskal_loop0 | greedy_dfs | 134.7 | 2.043 | 1.5 | 3.7865 |
| kruskal_loop0 | prior_astar | 135.1 | 2.133 | 2.121 | 3.7191 |
| kruskal_loop0 | repeated_astar | 133.3 | 2.113 | 2.121 | 3.4719 |
| kruskal_loop0 | turn_aware_astar | 118.9 | 1.833 | 1.5 | 3.5843 |
| kruskal_loop0 | turn_aware_astar_w2 | 115.9 | 1.789 | 1.5 | 3.5843 |
| kruskal_loop0 | wall_follower_left | 1141.1 | 22.814 | 22.806 | 44.3684 |
| kruskal_loop10 | dfs | 583.0 | 12.569 | 14.443 | 30.725 |
| kruskal_loop10 | dstar_lite | 98.8 | 1.964 | 2.006 | 3.475 |
| kruskal_loop10 | flood_fill | 79.3 | 1.523 | 1.414 | 2.3226 |
| kruskal_loop10 | frontier | 496.8 | 10.565 | 6.678 | 29.125 |
| kruskal_loop10 | greedy_dfs | 87.7 | 1.679 | 1.476 | 3.2742 |
| kruskal_loop10 | prior_astar | 101.8 | 2.019 | 2.006 | 3.475 |
| kruskal_loop10 | repeated_astar | 98.8 | 1.964 | 2.006 | 3.475 |
| kruskal_loop10 | turn_aware_astar | 82.9 | 1.584 | 1.476 | 2.7903 |
| kruskal_loop10 | turn_aware_astar_w2 | 81.0 | 1.553 | 1.476 | 2.4839 |
| kruskal_loop10 | wall_follower_left | 979.0 | 23.708 | 23.708 | 25.1053 |
| kruskal_loop30 | dfs | 682.1 | 20.225 | 20.105 | 45.1923 |
| kruskal_loop30 | dstar_lite | 68.6 | 1.968 | 1.86 | 3.4 |
| kruskal_loop30 | flood_fill | 63.6 | 1.883 | 1.607 | 4.6667 |
| kruskal_loop30 | frontier | 325.7 | 9.841 | 8.385 | 20.2105 |
| kruskal_loop30 | greedy_dfs | 60.5 | 1.768 | 1.607 | 3.5185 |
| kruskal_loop30 | prior_astar | 68.6 | 1.968 | 1.86 | 3.4 |
| kruskal_loop30 | repeated_astar | 68.6 | 1.968 | 1.86 | 3.4 |
| kruskal_loop30 | turn_aware_astar | 63.6 | 1.883 | 1.607 | 4.6667 |
| kruskal_loop30 | turn_aware_astar_w2 | 63.6 | 1.883 | 1.607 | 4.6667 |
| kruskal_loop30 | wall_follower_left |  |  |  |  |
| prim_loop0 | dfs | 775.3 | 17.851 | 19.405 | 26.1739 |
| prim_loop0 | dstar_lite | 360.0 | 8.282 | 8.341 | 13.5641 |
| prim_loop0 | flood_fill | 290.2 | 6.525 | 6.783 | 13.1026 |
| prim_loop0 | frontier | 736.9 | 16.863 | 16.731 | 26.1739 |
| prim_loop0 | greedy_dfs | 614.8 | 13.621 | 12.76 | 29.2 |
| prim_loop0 | prior_astar | 280.0 | 6.45 | 6.519 | 12.2308 |
| prim_loop0 | repeated_astar | 349.4 | 8.085 | 8.282 | 14.0256 |
| prim_loop0 | turn_aware_astar | 316.0 | 7.19 | 6.783 | 13.7179 |
| prim_loop0 | turn_aware_astar_w2 | 286.8 | 6.591 | 4.349 | 13.7179 |
| prim_loop0 | wall_follower_left | 919.3 | 21.225 | 21.882 | 29.1304 |
| prim_loop10 | dfs | 723.4 | 19.381 | 20.433 | 35.6286 |
| prim_loop10 | dstar_lite | 217.8 | 5.589 | 5.285 | 11.7692 |
| prim_loop10 | flood_fill | 163.9 | 4.103 | 3.639 | 11.8205 |
| prim_loop10 | frontier | 623.3 | 16.515 | 17.091 | 23.2051 |
| prim_loop10 | greedy_dfs | 315.5 | 7.924 | 4.28 | 27.4211 |
| prim_loop10 | prior_astar | 219.9 | 5.572 | 5.311 | 10.2821 |
| prim_loop10 | repeated_astar | 221.8 | 5.677 | 5.364 | 12.3333 |
| prim_loop10 | turn_aware_astar | 155.1 | 3.882 | 3.341 | 11.3077 |
| prim_loop10 | turn_aware_astar_w2 | 154.7 | 3.867 | 3.448 | 10.9487 |
| prim_loop10 | wall_follower_left | 654.167 | 19.066 | 20.308 | 26.4615 |
| prim_loop30 | dfs | 527.3 | 18.269 | 18.539 | 37.6364 |
| prim_loop30 | dstar_lite | 87.2 | 2.714 | 2.361 | 4.5652 |
| prim_loop30 | flood_fill | 80.1 | 2.56 | 2.372 | 4.5652 |
| prim_loop30 | frontier | 488.6 | 16.875 | 16.953 | 33.2727 |
| prim_loop30 | greedy_dfs | 179.8 | 5.359 | 3.045 | 15.7027 |
| prim_loop30 | prior_astar | 82.6 | 2.678 | 2.361 | 6.913 |
| prim_loop30 | repeated_astar | 81.0 | 2.546 | 2.361 | 4.5652 |
| prim_loop30 | turn_aware_astar | 77.9 | 2.501 | 2.222 | 4.5652 |
| prim_loop30 | turn_aware_astar_w2 | 78.1 | 2.506 | 2.222 | 4.5652 |
| prim_loop30 | wall_follower_left | 299.5 | 9.015 | 9.015 | 11.3548 |
| wilson_loop0 | dfs | 616.7 | 8.158 | 7.774 | 17.2857 |
| wilson_loop0 | dstar_lite | 287.0 | 4.077 | 2.219 | 11.2857 |
| wilson_loop0 | flood_fill | 364.8 | 5.606 | 2.696 | 17.2 |
| wilson_loop0 | frontier | 616.7 | 8.158 | 7.774 | 17.2857 |
| wilson_loop0 | greedy_dfs | 688.5 | 9.904 | 7.865 | 29.98 |
| wilson_loop0 | prior_astar | 283.4 | 3.843 | 2.429 | 8.7436 |
| wilson_loop0 | repeated_astar | 269.2 | 3.948 | 2.219 | 11.3714 |
| wilson_loop0 | turn_aware_astar | 369.1 | 5.714 | 3.899 | 22.02 |
| wilson_loop0 | turn_aware_astar_w2 | 363.3 | 5.534 | 3.862 | 18.82 |
| wilson_loop0 | wall_follower_left | 655.1 | 8.657 | 7.768 | 17.1905 |
| wilson_loop10 | dfs | 924.3 | 17.012 | 15.754 | 38.0952 |
| wilson_loop10 | dstar_lite | 157.9 | 2.667 | 2.246 | 4.9211 |
| wilson_loop10 | flood_fill | 160.0 | 2.9 | 2.517 | 5.4524 |
| wilson_loop10 | frontier | 746.7 | 13.454 | 12.559 | 24.1053 |
| wilson_loop10 | greedy_dfs | 194.3 | 3.388 | 2.321 | 10.3871 |
| wilson_loop10 | prior_astar | 137.8 | 2.271 | 2.216 | 3.4789 |
| wilson_loop10 | repeated_astar | 151.5 | 2.564 | 2.246 | 4.9211 |
| wilson_loop10 | turn_aware_astar | 153.7 | 2.644 | 2.303 | 5.8387 |
| wilson_loop10 | turn_aware_astar_w2 | 154.7 | 2.668 | 2.303 | 5.8387 |
| wilson_loop10 | wall_follower_left | 594.0 | 5.995 | 5.995 | 9.4727 |
| wilson_loop30 | dfs | 792.6 | 24.336 | 23.25 | 31.7742 |
| wilson_loop30 | dstar_lite | 62.9 | 1.935 | 1.767 | 3.3226 |
| wilson_loop30 | flood_fill | 62.5 | 1.945 | 1.567 | 4.4444 |
| wilson_loop30 | frontier | 557.8 | 17.267 | 19.931 | 25.1667 |
| wilson_loop30 | greedy_dfs | 64.0 | 1.995 | 1.567 | 4.4444 |
| wilson_loop30 | prior_astar | 62.9 | 1.935 | 1.767 | 3.3226 |
| wilson_loop30 | repeated_astar | 62.9 | 1.935 | 1.767 | 3.3226 |
| wilson_loop30 | turn_aware_astar | 64.0 | 1.995 | 1.567 | 4.4444 |
| wilson_loop30 | turn_aware_astar_w2 | 64.0 | 1.995 | 1.567 | 4.4444 |
| wilson_loop30 | wall_follower_left |  |  |  |  |
| ALL | dfs | 762.071 | 8.508 | 6.228 | 46.0526 |
| ALL | dstar_lite | 316.34 | 2.865 | 2.147 | 64.7826 |
| ALL | flood_fill | 317.579 | 2.821 | 2.12 | 64.8696 |
| ALL | frontier | 684.745 | 7.186 | 5.515 | 33.2727 |
| ALL | greedy_dfs | 457.175 | 4.069 | 2.694 | 39.3913 |
| ALL | prior_astar | 356.248 | 3.006 | 2.482 | 40.1304 |
| ALL | repeated_astar | 312.91 | 2.787 | 2.15 | 39.3913 |
| ALL | turn_aware_astar | 322.216 | 2.88 | 2.125 | 64.8696 |
| ALL | turn_aware_astar_w2 | 314.625 | 2.726 | 2.124 | 35.7826 |
| ALL | wall_follower_left | 563.016 | 7.773 | 2.558 | 44.3684 |
