# 规则：基础规则 + 转弯代价（λ = 2）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 10/10 | 102.8 | 1.188 | 1.0 | 1.7547 | 67.5 | 12.9 | 0.114 |  |
| backtracker_loop0 | dstar_lite | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.801 | 272 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 28.599 |  |
| backtracker_loop0 | frontier | 10/10 | 102.6 | 1.183 | 1.0 | 1.7547 | 67.3 | 12.8 | 0.427 | 107.5 |
| backtracker_loop0 | greedy_dfs | 10/10 | 94.2 | 1.125 | 1.036 | 1.6918 | 62.5 | 8.6 | 0.467 |  |
| backtracker_loop0 | prior_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 7.822 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 2.153 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 12.922 | 986.7 |
| backtracker_loop0 | turn_aware_astar_w2 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 8.528 | 828.4 |
| backtracker_loop0 | wall_follower_left | 10/10 | 116.2 | 1.466 | 1.26 | 2.439 | 78.9 | 19.6 | 0.226 |  |
| backtracker_loop10 | dfs | 10/10 | 93.8 | 5.131 | 2.382 | 19.8125 | 64.6 | 20.9 | 0.085 |  |
| backtracker_loop10 | dstar_lite | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.575 | 109.3 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 9.478 |  |
| backtracker_loop10 | frontier | 10/10 | 64.7 | 3.339 | 2.03 | 11.0 | 44.2 | 4.8 | 0.165 | 67.3 |
| backtracker_loop10 | greedy_dfs | 10/10 | 40.7 | 2.12 | 1.692 | 4.6875 | 27.3 | 5.8 | 0.207 |  |
| backtracker_loop10 | prior_astar | 10/10 | 25.8 | 1.298 | 1.177 | 2.04 | 18.3 | 1.3 | 2.038 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 0.528 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 32.3 | 1.699 | 1.395 | 3.6875 | 21.5 | 2.1 | 3.386 | 232.1 |
| backtracker_loop10 | turn_aware_astar_w2 | 10/10 | 32.3 | 1.699 | 1.395 | 3.6875 | 21.5 | 2.1 | 2.015 | 147 |
| backtracker_loop10 | wall_follower_left | 3/10 | 87.667 | 5.068 | 1.833 | 11.6875 | 50.667 | 14.333 | 0.316 |  |
| backtracker_loop30 | dfs | 10/10 | 165.4 | 10.264 | 9.783 | 17.8571 | 109.6 | 35.1 | 0.223 |  |
| backtracker_loop30 | dstar_lite | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.397 | 90.3 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 7.254 |  |
| backtracker_loop30 | frontier | 10/10 | 114.6 | 7.352 | 8.339 | 11.5 | 70.9 | 13.6 | 0.72 | 138.2 |
| backtracker_loop30 | greedy_dfs | 10/10 | 25.2 | 1.619 | 1.355 | 4.1875 | 13.7 | 0.8 | 0.116 |  |
| backtracker_loop30 | prior_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.367 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.355 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 1.997 | 103.7 |
| backtracker_loop30 | turn_aware_astar_w2 | 10/10 | 21.1 | 1.363 | 1.355 | 1.8571 | 11 | 0.8 | 1.052 | 54.5 |
| backtracker_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.173 |  |
| external | dfs | 315/315 | 249.13 | 5.039 | 4.532 | 26.2857 | 139.937 | 81.933 | 0.388 |  |
| external | dstar_lite | 315/315 | 115.99 | 2.269 | 1.81 | 28.1429 | 64.898 | 20.87 | 6.058 | 412.321 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 38.627 |  |
| external | frontier | 315/315 | 233.213 | 4.675 | 4.03 | 25.5714 | 130.549 | 64.022 | 1.208 | 329.435 |
| external | greedy_dfs | 315/315 | 164.863 | 3.185 | 2.54 | 31.4286 | 93.492 | 43.575 | 0.796 |  |
| external | prior_astar | 315/315 | 130.108 | 2.409 | 2.167 | 19.4211 | 75.984 | 34.41 | 10.959 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 2.691 |  |
| external | turn_aware_astar | 315/315 | 120.87 | 2.339 | 1.931 | 30.1429 | 64.552 | 21.114 | 16.666 | 1716.403 |
| external | turn_aware_astar_w2 | 315/315 | 119.114 | 2.27 | 1.941 | 29.7143 | 63.695 | 21.229 | 13.065 | 1504.987 |
| external | wall_follower_left | 71/315 | 128.366 | 2.665 | 1.717 | 25.4286 | 76.803 | 25.437 | 0.201 |  |
| kruskal_loop0 | dfs | 10/10 | 162.2 | 10.279 | 6.01 | 27.8571 | 138.7 | 71 | 0.189 |  |
| kruskal_loop0 | dstar_lite | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.745 | 143.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 7.203 |  |
| kruskal_loop0 | frontier | 10/10 | 88.2 | 5.24 | 2.314 | 18.1765 | 74.7 | 34.1 | 0.217 | 111.3 |
| kruskal_loop0 | greedy_dfs | 10/10 | 35.1 | 1.82 | 1.414 | 3.56 | 24.9 | 8.6 | 0.12 |  |
| kruskal_loop0 | prior_astar | 10/10 | 32.3 | 1.703 | 1.5 | 3.32 | 25.7 | 8.2 | 2.282 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 0.553 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 2.216 | 195.5 |
| kruskal_loop0 | turn_aware_astar_w2 | 10/10 | 29.9 | 1.577 | 1.414 | 3.16 | 21.5 | 6.1 | 1.29 | 127.4 |
| kruskal_loop0 | wall_follower_left | 10/10 | 254.3 | 15.646 | 17.187 | 27.2857 | 221.7 | 116.1 | 0.521 |  |
| kruskal_loop10 | dfs | 10/10 | 133.8 | 8.626 | 9.875 | 18.0625 | 112.3 | 41.2 | 0.255 |  |
| kruskal_loop10 | dstar_lite | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.401 | 107 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 7.164 |  |
| kruskal_loop10 | frontier | 10/10 | 115.2 | 7.309 | 5.623 | 17.0625 | 95.4 | 34.3 | 0.484 | 137.4 |
| kruskal_loop10 | greedy_dfs | 10/10 | 26.1 | 1.599 | 1.5 | 2.75 | 15.4 | 2.8 | 0.127 |  |
| kruskal_loop10 | prior_astar | 10/10 | 25.4 | 1.577 | 1.5 | 2.8571 | 19.1 | 4.3 | 1.97 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 0.484 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 2.178 | 139.3 |
| kruskal_loop10 | turn_aware_astar_w2 | 10/10 | 24.6 | 1.519 | 1.5 | 2.4286 | 14.1 | 2.5 | 1.196 | 75.7 |
| kruskal_loop10 | wall_follower_left | 2/10 | 215 | 14.021 | 14.021 | 15.5714 | 191 | 66 | 0.462 |  |
| kruskal_loop30 | dfs | 10/10 | 166.5 | 11.348 | 11.658 | 19.875 | 128.9 | 47.8 | 0.221 |  |
| kruskal_loop30 | dstar_lite | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.171 | 86.8 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 6.64 |  |
| kruskal_loop30 | frontier | 10/10 | 84.1 | 5.822 | 5.491 | 13.1429 | 60.4 | 11.7 | 0.394 | 93.4 |
| kruskal_loop30 | greedy_dfs | 10/10 | 19.7 | 1.362 | 1.232 | 1.9286 | 10.2 | 1.6 | 0.1 |  |
| kruskal_loop30 | prior_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.226 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.35 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.79 | 98.9 |
| kruskal_loop30 | turn_aware_astar_w2 | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 0.897 | 51.3 |
| kruskal_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.275 |  |
| prim_loop0 | dfs | 10/10 | 181.7 | 11.87 | 13.424 | 15.5556 | 148.4 | 82.9 | 0.287 |  |
| prim_loop0 | dstar_lite | 10/10 | 91.6 | 5.997 | 7.078 | 9.0 | 67.1 | 38.7 | 6.201 | 349.4 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 29.49 |  |
| prim_loop0 | frontier | 10/10 | 173.3 | 11.298 | 12.419 | 15.5556 | 140.9 | 78.9 | 0.856 | 221.3 |
| prim_loop0 | greedy_dfs | 10/10 | 148 | 9.612 | 9.744 | 24.0 | 116.7 | 66.3 | 0.814 |  |
| prim_loop0 | prior_astar | 10/10 | 71.6 | 4.664 | 4.756 | 8.4286 | 52.1 | 28.5 | 3.835 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 1.751 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 86 | 5.582 | 6.215 | 9.1429 | 57.5 | 35.5 | 10.338 | 1163.6 |
| prim_loop0 | turn_aware_astar_w2 | 10/10 | 78.6 | 5.055 | 4.629 | 8.5556 | 51.7 | 32 | 4.713 | 940.9 |
| prim_loop0 | wall_follower_left | 10/10 | 209.3 | 13.732 | 13.491 | 18.0714 | 177.5 | 96.7 | 0.352 |  |
| prim_loop10 | dfs | 10/10 | 172.2 | 11.81 | 11.549 | 20.7333 | 137.8 | 64.4 | 0.273 |  |
| prim_loop10 | dstar_lite | 10/10 | 57.8 | 3.953 | 3.4 | 7.6667 | 40 | 17.9 | 3.099 | 225.3 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 14.636 |  |
| prim_loop10 | frontier | 10/10 | 148.5 | 10.214 | 10.483 | 13.5714 | 118.7 | 52.2 | 0.78 | 191.5 |
| prim_loop10 | greedy_dfs | 10/10 | 80.7 | 5.531 | 2.929 | 18.4286 | 58.7 | 27.6 | 0.215 |  |
| prim_loop10 | prior_astar | 10/10 | 57.1 | 3.9 | 3.533 | 7.1429 | 40.7 | 17.9 | 2.933 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 0.937 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 46.9 | 3.19 | 2.871 | 7.5333 | 27.5 | 12.8 | 3.492 | 413.2 |
| prim_loop10 | turn_aware_astar_w2 | 10/10 | 46.9 | 3.189 | 2.871 | 7.5333 | 26.9 | 13.3 | 2.555 | 281.9 |
| prim_loop10 | wall_follower_left | 6/10 | 149.5 | 10.429 | 10.607 | 13.1429 | 126.167 | 52.5 | 0.3 |  |
| prim_loop30 | dfs | 10/10 | 132.5 | 9.425 | 10.679 | 14.5714 | 98.7 | 30.7 | 0.197 |  |
| prim_loop30 | dstar_lite | 10/10 | 26.4 | 1.854 | 1.624 | 2.8667 | 15.2 | 3.5 | 1.376 | 110.9 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 8.808 |  |
| prim_loop30 | frontier | 10/10 | 125 | 8.89 | 10.036 | 13.4286 | 90.9 | 25.3 | 0.671 | 141.5 |
| prim_loop30 | greedy_dfs | 10/10 | 51 | 3.564 | 2.0 | 11.0714 | 32.2 | 13.4 | 0.165 |  |
| prim_loop30 | prior_astar | 10/10 | 25.8 | 1.819 | 1.624 | 3.3571 | 14.2 | 3.8 | 0.935 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.395 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.3 | 3.6 | 1.586 | 129.4 |
| prim_loop30 | turn_aware_astar_w2 | 10/10 | 26.3 | 1.849 | 1.607 | 2.7333 | 12.9 | 3.5 | 1.116 | 86.4 |
| prim_loop30 | wall_follower_left | 2/10 | 73.5 | 5.11 | 5.11 | 6.2857 | 56.5 | 13.5 | 0.227 |  |
| wilson_loop0 | dfs | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.196 |  |
| wilson_loop0 | dstar_lite | 10/10 | 70.2 | 3.031 | 1.762 | 9.0 | 54.2 | 24.5 | 2.772 | 287.3 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 30.207 |  |
| wilson_loop0 | frontier | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.619 | 182.9 |
| wilson_loop0 | greedy_dfs | 10/10 | 164.9 | 7.764 | 6.292 | 24.7857 | 130.9 | 69.2 | 0.701 |  |
| wilson_loop0 | prior_astar | 10/10 | 68.2 | 2.856 | 1.905 | 5.4167 | 53.8 | 24.3 | 5.098 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 1.103 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 94.3 | 4.794 | 3.016 | 19.2143 | 69.7 | 34.2 | 9.697 | 1495.9 |
| wilson_loop0 | turn_aware_astar_w2 | 10/10 | 99.5 | 5.005 | 2.5 | 16.9286 | 72.7 | 36.8 | 9.847 | 1347.3 |
| wilson_loop0 | wall_follower_left | 10/10 | 149.1 | 6.282 | 5.453 | 13.3333 | 126.5 | 62 | 0.28 |  |
| wilson_loop10 | dfs | 10/10 | 221.5 | 12.638 | 13.026 | 25.4286 | 175.7 | 76.5 | 0.347 |  |
| wilson_loop10 | dstar_lite | 10/10 | 39.5 | 2.102 | 1.771 | 3.4444 | 29.6 | 7 | 1.986 | 161.4 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 13.15 |  |
| wilson_loop10 | frontier | 10/10 | 181.9 | 10.085 | 9.042 | 17.1429 | 141.2 | 55 | 1.012 | 212.6 |
| wilson_loop10 | greedy_dfs | 10/10 | 51.5 | 2.838 | 1.821 | 8.6667 | 35.7 | 11.5 | 0.198 |  |
| wilson_loop10 | prior_astar | 10/10 | 35.4 | 1.845 | 1.804 | 3.1053 | 25.6 | 7 | 2.119 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 0.674 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.5 | 2.312 | 1.768 | 5.2222 | 27.8 | 6.7 | 2.977 | 511.2 |
| wilson_loop10 | turn_aware_astar_w2 | 10/10 | 40.1 | 2.182 | 1.768 | 4.3571 | 26.1 | 5.9 | 1.659 | 257.7 |
| wilson_loop10 | wall_follower_left | 2/10 | 144 | 4.287 | 4.287 | 6.6842 | 112.5 | 44 | 0.44 |  |
| wilson_loop30 | dfs | 10/10 | 204.6 | 14.432 | 14.929 | 17.4286 | 147 | 49.9 | 0.271 |  |
| wilson_loop30 | dstar_lite | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.294 | 89.5 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 7.136 |  |
| wilson_loop30 | frontier | 10/10 | 146.2 | 10.34 | 11.0 | 16.4286 | 102.9 | 27.8 | 0.719 | 174.9 |
| wilson_loop30 | greedy_dfs | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 0.11 |  |
| wilson_loop30 | prior_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.163 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.337 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 2.116 | 97.9 |
| wilson_loop30 | turn_aware_astar_w2 | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 1.181 | 60.6 |
| wilson_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.224 |  |
| ALL | dfs | 435/435 | 223.653 | 6.248 | 5.0 | 27.8571 | 134.605 | 72.961 | 0.324 |  |
| ALL | dstar_lite | 435/435 | 95.66 | 2.256 | 1.714 | 28.1429 | 55.17 | 17.586 | 5.251 | 345.308 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 31.079 |  |
| ALL | frontier | 435/435 | 203.099 | 5.388 | 4.467 | 25.5714 | 120.411 | 55.789 | 0.979 | 279.471 |
| ALL | greedy_dfs | 435/435 | 136.844 | 3.238 | 2.263 | 31.4286 | 80.083 | 36.554 | 0.655 |  |
| ALL | prior_astar | 435/435 | 105.223 | 2.313 | 2.018 | 19.4211 | 62.756 | 27.193 | 8.323 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 2.137 |  |
| ALL | turn_aware_astar | 435/435 | 99.57 | 2.335 | 1.842 | 30.1429 | 54.46 | 17.761 | 13.196 | 1370.899 |
| ALL | turn_aware_astar_w2 | 435/435 | 98.189 | 2.275 | 1.87 | 29.7143 | 53.713 | 17.814 | 10.391 | 1187.729 |
| ALL | wall_follower_left | 126/435 | 146.254 | 5.437 | 2.246 | 27.2857 | 104.19 | 42.5 | 0.223 |  |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 237.8 | 1.191 | 1.0 | 1.7775 |
| backtracker_loop0 | dstar_lite | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | frontier | 237.2 | 1.185 | 1.0 | 1.7775 |
| backtracker_loop0 | greedy_dfs | 219.2 | 1.132 | 1.04 | 1.693 |
| backtracker_loop0 | prior_astar | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar_w2 | 178.0 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | wall_follower_left | 274.0 | 1.488 | 1.305 | 2.5588 |
| backtracker_loop10 | dfs | 223.0 | 5.214 | 2.697 | 19.725 |
| backtracker_loop10 | dstar_lite | 65.3 | 1.459 | 1.192 | 2.675 |
| backtracker_loop10 | flood_fill | 76.5 | 1.747 | 1.262 | 4.225 |
| backtracker_loop10 | frontier | 153.1 | 3.367 | 2.439 | 10.8 |
| backtracker_loop10 | greedy_dfs | 95.3 | 2.156 | 1.942 | 4.275 |
| backtracker_loop10 | prior_astar | 62.4 | 1.391 | 1.192 | 2.3514 |
| backtracker_loop10 | repeated_astar | 65.3 | 1.459 | 1.192 | 2.675 |
| backtracker_loop10 | turn_aware_astar | 75.3 | 1.72 | 1.519 | 3.375 |
| backtracker_loop10 | turn_aware_astar_w2 | 75.3 | 1.72 | 1.519 | 3.375 |
| backtracker_loop10 | wall_follower_left | 189.0 | 5.051 | 1.857 | 11.7353 |
| backtracker_loop30 | dfs | 384.6 | 12.507 | 11.876 | 20.3617 |
| backtracker_loop30 | dstar_lite | 47.7 | 1.595 | 1.58 | 2.1852 |
| backtracker_loop30 | flood_fill | 42.5 | 1.445 | 1.404 | 1.8571 |
| backtracker_loop30 | frontier | 256.4 | 8.624 | 10.095 | 13.0 |
| backtracker_loop30 | greedy_dfs | 52.6 | 1.806 | 1.404 | 5.4643 |
| backtracker_loop30 | prior_astar | 47.7 | 1.595 | 1.58 | 2.1852 |
| backtracker_loop30 | repeated_astar | 47.7 | 1.595 | 1.58 | 2.1852 |
| backtracker_loop30 | turn_aware_astar | 43.1 | 1.466 | 1.404 | 2.0714 |
| backtracker_loop30 | turn_aware_astar_w2 | 43.1 | 1.466 | 1.404 | 2.0714 |
| backtracker_loop30 | wall_follower_left |  |  |  |  |
| external | dfs | 529.003 | 5.806 | 5.111 | 24.8421 |
| external | dstar_lite | 245.787 | 2.621 | 2.022 | 50.0 |
| external | flood_fill | 250.121 | 2.647 | 2.103 | 50.1053 |
| external | frontier | 494.311 | 5.352 | 4.543 | 24.8421 |
| external | greedy_dfs | 351.848 | 3.661 | 2.818 | 30.2105 |
| external | prior_astar | 282.076 | 2.854 | 2.482 | 30.2632 |
| external | repeated_astar | 243.14 | 2.544 | 2.03 | 30.2105 |
| external | turn_aware_astar | 249.975 | 2.64 | 2.092 | 50.1053 |
| external | turn_aware_astar_w2 | 246.505 | 2.544 | 2.103 | 27.1053 |
| external | wall_follower_left | 281.972 | 3.032 | 1.966 | 25.0526 |
| kruskal_loop0 | dfs | 439.6 | 13.941 | 6.392 | 41.1538 |
| kruskal_loop0 | dstar_lite | 82.7 | 2.014 | 1.987 | 3.386 |
| kruskal_loop0 | flood_fill | 72.3 | 1.726 | 1.481 | 3.4912 |
| kruskal_loop0 | frontier | 237.6 | 7.283 | 2.68 | 27.8387 |
| kruskal_loop0 | greedy_dfs | 84.9 | 1.992 | 1.481 | 3.7368 |
| kruskal_loop0 | prior_astar | 83.7 | 2.031 | 1.987 | 3.6316 |
| kruskal_loop0 | repeated_astar | 82.7 | 2.014 | 1.987 | 3.386 |
| kruskal_loop0 | turn_aware_astar | 72.9 | 1.74 | 1.481 | 3.4912 |
| kruskal_loop0 | turn_aware_astar_w2 | 72.9 | 1.74 | 1.481 | 3.4912 |
| kruskal_loop0 | wall_follower_left | 697.7 | 20.996 | 21.544 | 39.6154 |
| kruskal_loop10 | dfs | 358.4 | 11.514 | 13.24 | 27.1071 |
| kruskal_loop10 | dstar_lite | 62.0 | 1.849 | 1.857 | 3.0357 |
| kruskal_loop10 | flood_fill | 51.7 | 1.504 | 1.409 | 2.1905 |
| kruskal_loop10 | frontier | 306.0 | 9.687 | 6.449 | 25.6786 |
| kruskal_loop10 | greedy_dfs | 56.9 | 1.647 | 1.488 | 3.0714 |
| kruskal_loop10 | prior_astar | 63.6 | 1.896 | 1.857 | 3.0357 |
| kruskal_loop10 | repeated_astar | 62.0 | 1.849 | 1.857 | 3.0357 |
| kruskal_loop10 | turn_aware_astar | 52.8 | 1.534 | 1.488 | 2.3333 |
| kruskal_loop10 | turn_aware_astar_w2 | 52.8 | 1.534 | 1.488 | 2.3333 |
| kruskal_loop10 | wall_follower_left | 597.0 | 21.076 | 21.076 | 22.5385 |
| kruskal_loop30 | dfs | 424.3 | 17.365 | 16.954 | 36.15 |
| kruskal_loop30 | dstar_lite | 44.0 | 1.769 | 1.65 | 3.0 |
| kruskal_loop30 | flood_fill | 42.0 | 1.723 | 1.536 | 3.8095 |
| kruskal_loop30 | frontier | 204.9 | 8.539 | 7.431 | 18.3077 |
| kruskal_loop30 | greedy_dfs | 40.1 | 1.632 | 1.536 | 2.9048 |
| kruskal_loop30 | prior_astar | 44.0 | 1.769 | 1.65 | 3.0 |
| kruskal_loop30 | repeated_astar | 44.0 | 1.769 | 1.65 | 3.0 |
| kruskal_loop30 | turn_aware_astar | 42.0 | 1.723 | 1.536 | 3.8095 |
| kruskal_loop30 | turn_aware_astar_w2 | 42.0 | 1.723 | 1.536 | 3.8095 |
| kruskal_loop30 | wall_follower_left |  |  |  |  |
| prim_loop0 | dfs | 478.5 | 16.21 | 18.328 | 23.1875 |
| prim_loop0 | dstar_lite | 225.8 | 7.642 | 8.101 | 12.037 |
| prim_loop0 | flood_fill | 184.8 | 6.136 | 6.6 | 11.6667 |
| prim_loop0 | frontier | 455.1 | 15.342 | 15.277 | 23.1875 |
| prim_loop0 | greedy_dfs | 381.4 | 12.527 | 12.031 | 28.0625 |
| prim_loop0 | prior_astar | 175.8 | 5.953 | 6.008 | 10.8519 |
| prim_loop0 | repeated_astar | 218.8 | 7.429 | 7.893 | 12.4074 |
| prim_loop0 | turn_aware_astar | 201.0 | 6.713 | 6.6 | 12.2593 |
| prim_loop0 | turn_aware_astar_w2 | 182.0 | 6.115 | 4.411 | 11.8889 |
| prim_loop0 | wall_follower_left | 564.3 | 19.17 | 19.47 | 25.625 |
| prim_loop10 | dfs | 447.8 | 17.063 | 17.473 | 31.16 |
| prim_loop10 | dstar_lite | 137.8 | 5.089 | 4.758 | 10.6296 |
| prim_loop10 | flood_fill | 105.9 | 3.841 | 3.364 | 10.7037 |
| prim_loop10 | frontier | 385.9 | 14.584 | 14.24 | 20.4815 |
| prim_loop10 | greedy_dfs | 198.1 | 7.238 | 3.821 | 25.0 |
| prim_loop10 | prior_astar | 138.5 | 5.064 | 4.734 | 9.2222 |
| prim_loop10 | repeated_astar | 139.8 | 5.153 | 4.811 | 11.0 |
| prim_loop10 | turn_aware_astar | 101.9 | 3.697 | 3.124 | 10.2593 |
| prim_loop10 | turn_aware_astar_w2 | 100.7 | 3.649 | 3.124 | 9.963 |
| prim_loop10 | wall_follower_left | 401.833 | 16.278 | 17.537 | 21.2 |
| prim_loop30 | dfs | 329.9 | 15.029 | 15.77 | 28.6667 |
| prim_loop30 | dstar_lite | 56.8 | 2.396 | 2.074 | 3.8889 |
| prim_loop30 | flood_fill | 53.3 | 2.286 | 2.077 | 3.6316 |
| prim_loop30 | frontier | 306.8 | 13.936 | 14.676 | 25.5556 |
| prim_loop30 | greedy_dfs | 115.4 | 4.716 | 2.722 | 14.0385 |
| prim_loop30 | prior_astar | 54.2 | 2.349 | 2.074 | 5.4211 |
| prim_loop30 | repeated_astar | 53.0 | 2.255 | 2.074 | 3.6316 |
| prim_loop30 | turn_aware_astar | 53.1 | 2.278 | 2.077 | 3.6316 |
| prim_loop30 | turn_aware_astar_w2 | 52.1 | 2.24 | 2.077 | 3.6316 |
| prim_loop30 | wall_follower_left | 186.5 | 7.616 | 7.616 | 9.5652 |
| wilson_loop0 | dfs | 380.5 | 7.643 | 7.3 | 16.2174 |
| wilson_loop0 | dstar_lite | 178.6 | 3.808 | 2.104 | 10.7391 |
| wilson_loop0 | flood_fill | 228.4 | 5.371 | 2.553 | 16.6875 |
| wilson_loop0 | frontier | 380.5 | 7.643 | 7.3 | 16.2174 |
| wilson_loop0 | greedy_dfs | 426.7 | 9.396 | 7.5 | 28.8438 |
| wilson_loop0 | prior_astar | 175.8 | 3.592 | 2.304 | 7.7407 |
| wilson_loop0 | repeated_astar | 167.6 | 3.688 | 2.104 | 10.7826 |
| wilson_loop0 | turn_aware_astar | 233.7 | 5.534 | 3.656 | 21.4062 |
| wilson_loop0 | turn_aware_astar_w2 | 244.9 | 5.755 | 2.927 | 18.4062 |
| wilson_loop0 | wall_follower_left | 402.1 | 8.075 | 7.198 | 16.3333 |
| wilson_loop10 | dfs | 572.9 | 15.877 | 14.856 | 34.9286 |
| wilson_loop10 | dstar_lite | 98.7 | 2.52 | 2.125 | 4.5 |
| wilson_loop10 | flood_fill | 101.4 | 2.757 | 2.389 | 5.1786 |
| wilson_loop10 | frontier | 464.3 | 12.564 | 11.714 | 22.1538 |
| wilson_loop10 | greedy_dfs | 122.9 | 3.246 | 2.187 | 10.0 |
| wilson_loop10 | prior_astar | 86.6 | 2.159 | 2.125 | 3.4 |
| wilson_loop10 | repeated_astar | 94.9 | 2.425 | 2.125 | 4.5 |
| wilson_loop10 | turn_aware_astar | 98.1 | 2.554 | 2.16 | 5.7 |
| wilson_loop10 | turn_aware_astar_w2 | 92.3 | 2.415 | 2.16 | 5.1786 |
| wilson_loop10 | wall_follower_left | 369.0 | 5.563 | 5.563 | 8.7568 |
| wilson_loop30 | dfs | 498.6 | 20.852 | 19.978 | 26.9091 |
| wilson_loop30 | dstar_lite | 41.3 | 1.735 | 1.682 | 2.7391 |
| wilson_loop30 | flood_fill | 42.1 | 1.758 | 1.541 | 3.4783 |
| wilson_loop30 | frontier | 352.0 | 14.823 | 16.779 | 21.8462 |
| wilson_loop30 | greedy_dfs | 43.2 | 1.808 | 1.541 | 3.4783 |
| wilson_loop30 | prior_astar | 41.3 | 1.735 | 1.682 | 2.7391 |
| wilson_loop30 | repeated_astar | 41.3 | 1.735 | 1.682 | 2.7391 |
| wilson_loop30 | turn_aware_astar | 43.2 | 1.808 | 1.541 | 3.4783 |
| wilson_loop30 | turn_aware_astar_w2 | 43.2 | 1.808 | 1.541 | 3.4783 |
| wilson_loop30 | wall_follower_left |  |  |  |  |
| ALL | dfs | 492.862 | 7.754 | 5.861 | 41.1538 |
| ALL | dstar_lite | 206.0 | 2.654 | 2.0 | 50.0 |
| ALL | flood_fill | 208.223 | 2.636 | 2.03 | 50.1053 |
| ALL | frontier | 443.922 | 6.579 | 5.244 | 27.8387 |
| ALL | greedy_dfs | 297.009 | 3.785 | 2.515 | 30.2105 |
| ALL | prior_astar | 230.736 | 2.769 | 2.333 | 30.2632 |
| ALL | repeated_astar | 203.54 | 2.586 | 2.014 | 30.2105 |
| ALL | turn_aware_astar | 208.49 | 2.642 | 2.027 | 50.1053 |
| ALL | turn_aware_astar_w2 | 205.614 | 2.559 | 2.043 | 27.1053 |
| ALL | wall_follower_left | 354.635 | 7.094 | 2.415 | 39.6154 |
