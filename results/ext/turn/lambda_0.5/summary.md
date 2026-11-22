# 规则：基础规则 + 转弯代价（λ = 0.5）

## 未知地图探索

| 地图组 | 算法 | 成功率 | 平均步数 | 步数/最短路（均值） | 中位数 | 最大 | 平均转向 | 平均重复访问 | 计算 ms（中位数） | 扩展节点 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 10/10 | 102.8 | 1.188 | 1.0 | 1.7547 | 67.5 | 12.9 | 0.118 |  |
| backtracker_loop0 | dstar_lite | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 4.522 | 272 |
| backtracker_loop0 | flood_fill | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 26.59 |  |
| backtracker_loop0 | frontier | 10/10 | 102.6 | 1.183 | 1.0 | 1.7547 | 67.3 | 12.8 | 0.386 | 107.5 |
| backtracker_loop0 | greedy_dfs | 10/10 | 94.2 | 1.125 | 1.036 | 1.6918 | 62.5 | 8.6 | 0.442 |  |
| backtracker_loop0 | prior_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 7.61 |  |
| backtracker_loop0 | repeated_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 1.964 |  |
| backtracker_loop0 | turn_aware_astar | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 12.833 | 1162.2 |
| backtracker_loop0 | turn_aware_astar_w2 | 10/10 | 77 | 1.0 | 1.0 | 1.0 | 50.5 | 0 | 8.75 | 1015.3 |
| backtracker_loop0 | wall_follower_left | 10/10 | 116.2 | 1.466 | 1.26 | 2.439 | 78.9 | 19.6 | 0.212 |  |
| backtracker_loop10 | dfs | 10/10 | 93.8 | 5.131 | 2.382 | 19.8125 | 64.6 | 20.9 | 0.086 |  |
| backtracker_loop10 | dstar_lite | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 1.584 | 109.3 |
| backtracker_loop10 | flood_fill | 10/10 | 32.3 | 1.703 | 1.257 | 4.5625 | 22.1 | 1.7 | 9.329 |  |
| backtracker_loop10 | frontier | 10/10 | 64.7 | 3.339 | 2.03 | 11.0 | 44.2 | 4.8 | 0.165 | 67.3 |
| backtracker_loop10 | greedy_dfs | 10/10 | 40.7 | 2.12 | 1.692 | 4.6875 | 27.3 | 5.8 | 0.163 |  |
| backtracker_loop10 | prior_astar | 10/10 | 25.8 | 1.298 | 1.177 | 2.04 | 18.3 | 1.3 | 1.913 |  |
| backtracker_loop10 | repeated_astar | 10/10 | 27.5 | 1.412 | 1.177 | 2.9375 | 18.9 | 0.7 | 0.529 |  |
| backtracker_loop10 | turn_aware_astar | 10/10 | 30.9 | 1.616 | 1.257 | 3.6875 | 21.1 | 1.4 | 2.926 | 223.4 |
| backtracker_loop10 | turn_aware_astar_w2 | 10/10 | 30.9 | 1.616 | 1.257 | 3.6875 | 21.1 | 1.4 | 1.702 | 142.4 |
| backtracker_loop10 | wall_follower_left | 3/10 | 87.667 | 5.068 | 1.833 | 11.6875 | 50.667 | 14.333 | 0.313 |  |
| backtracker_loop30 | dfs | 10/10 | 165.4 | 10.264 | 9.783 | 17.8571 | 109.6 | 35.1 | 0.2 |  |
| backtracker_loop30 | dstar_lite | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.288 | 90.3 |
| backtracker_loop30 | flood_fill | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 6.974 |  |
| backtracker_loop30 | frontier | 10/10 | 114.6 | 7.352 | 8.339 | 11.5 | 70.9 | 13.6 | 0.655 | 138.2 |
| backtracker_loop30 | greedy_dfs | 10/10 | 25.2 | 1.619 | 1.355 | 4.1875 | 13.7 | 0.8 | 0.107 |  |
| backtracker_loop30 | prior_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 1.307 |  |
| backtracker_loop30 | repeated_astar | 10/10 | 21.1 | 1.348 | 1.333 | 1.8 | 13.3 | 0.6 | 0.347 |  |
| backtracker_loop30 | turn_aware_astar | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 1.801 | 104.7 |
| backtracker_loop30 | turn_aware_astar_w2 | 10/10 | 20.9 | 1.351 | 1.355 | 1.8571 | 10.8 | 0.7 | 1.169 | 54.8 |
| backtracker_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.168 |  |
| external | dfs | 315/315 | 249.13 | 5.039 | 4.532 | 26.2857 | 139.937 | 81.933 | 0.388 |  |
| external | dstar_lite | 315/315 | 115.99 | 2.269 | 1.81 | 28.1429 | 64.898 | 20.87 | 5.937 | 412.321 |
| external | flood_fill | 315/315 | 120.19 | 2.332 | 1.93 | 29.7143 | 64.965 | 21.476 | 38.645 |  |
| external | frontier | 315/315 | 233.213 | 4.675 | 4.03 | 25.5714 | 130.549 | 64.022 | 1.203 | 329.435 |
| external | greedy_dfs | 315/315 | 164.863 | 3.185 | 2.54 | 31.4286 | 93.492 | 43.575 | 0.771 |  |
| external | prior_astar | 315/315 | 130.108 | 2.409 | 2.167 | 19.4211 | 75.984 | 34.41 | 11.036 |  |
| external | repeated_astar | 315/315 | 114.257 | 2.211 | 1.815 | 28.1429 | 64.441 | 20.063 | 2.687 |  |
| external | turn_aware_astar | 315/315 | 119.924 | 2.331 | 1.912 | 30.1429 | 64.99 | 21.146 | 17.436 | 1891.927 |
| external | turn_aware_astar_w2 | 315/315 | 119.606 | 2.265 | 1.956 | 29.7143 | 65.086 | 22.651 | 14.159 | 1785.022 |
| external | wall_follower_left | 71/315 | 128.366 | 2.665 | 1.717 | 25.4286 | 76.803 | 25.437 | 0.194 |  |
| kruskal_loop0 | dfs | 10/10 | 162.2 | 10.279 | 6.01 | 27.8571 | 138.7 | 71 | 0.185 |  |
| kruskal_loop0 | dstar_lite | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 1.67 | 143.6 |
| kruskal_loop0 | flood_fill | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 7.002 |  |
| kruskal_loop0 | frontier | 10/10 | 88.2 | 5.24 | 2.314 | 18.1765 | 74.7 | 34.1 | 0.217 | 111.3 |
| kruskal_loop0 | greedy_dfs | 10/10 | 35.1 | 1.82 | 1.414 | 3.56 | 24.9 | 8.6 | 0.115 |  |
| kruskal_loop0 | prior_astar | 10/10 | 32.3 | 1.703 | 1.5 | 3.32 | 25.7 | 8.2 | 2.13 |  |
| kruskal_loop0 | repeated_astar | 10/10 | 32.1 | 1.699 | 1.586 | 3.08 | 25.3 | 7.8 | 0.585 |  |
| kruskal_loop0 | turn_aware_astar | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 2.261 | 202.7 |
| kruskal_loop0 | turn_aware_astar_w2 | 10/10 | 29.7 | 1.567 | 1.414 | 3.16 | 21.3 | 6 | 1.172 | 136.6 |
| kruskal_loop0 | wall_follower_left | 10/10 | 254.3 | 15.646 | 17.187 | 27.2857 | 221.7 | 116.1 | 0.49 |  |
| kruskal_loop10 | dfs | 10/10 | 133.8 | 8.626 | 9.875 | 18.0625 | 112.3 | 41.2 | 0.235 |  |
| kruskal_loop10 | dstar_lite | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 1.509 | 107 |
| kruskal_loop10 | flood_fill | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 6.941 |  |
| kruskal_loop10 | frontier | 10/10 | 115.2 | 7.309 | 5.623 | 17.0625 | 95.4 | 34.3 | 0.491 | 137.4 |
| kruskal_loop10 | greedy_dfs | 10/10 | 26.1 | 1.599 | 1.5 | 2.75 | 15.4 | 2.8 | 0.112 |  |
| kruskal_loop10 | prior_astar | 10/10 | 25.4 | 1.577 | 1.5 | 2.8571 | 19.1 | 4.3 | 1.897 |  |
| kruskal_loop10 | repeated_astar | 10/10 | 25.2 | 1.563 | 1.5 | 2.7143 | 18.4 | 3.8 | 0.464 |  |
| kruskal_loop10 | turn_aware_astar | 10/10 | 24.1 | 1.488 | 1.393 | 2.4286 | 13.8 | 2.5 | 2.114 | 140.8 |
| kruskal_loop10 | turn_aware_astar_w2 | 10/10 | 23.4 | 1.452 | 1.389 | 2.4286 | 13.6 | 2.6 | 1.131 | 69 |
| kruskal_loop10 | wall_follower_left | 2/10 | 215 | 14.021 | 14.021 | 15.5714 | 191 | 66 | 0.461 |  |
| kruskal_loop30 | dfs | 10/10 | 166.5 | 11.348 | 11.658 | 19.875 | 128.9 | 47.8 | 0.217 |  |
| kruskal_loop30 | dstar_lite | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.152 | 86.8 |
| kruskal_loop30 | flood_fill | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 6.428 |  |
| kruskal_loop30 | frontier | 10/10 | 84.1 | 5.822 | 5.491 | 13.1429 | 60.4 | 11.7 | 0.39 | 93.4 |
| kruskal_loop30 | greedy_dfs | 10/10 | 19.7 | 1.362 | 1.232 | 1.9286 | 10.2 | 1.6 | 0.101 |  |
| kruskal_loop30 | prior_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 1.188 |  |
| kruskal_loop30 | repeated_astar | 10/10 | 19.4 | 1.335 | 1.25 | 2.0 | 12.3 | 2 | 0.346 |  |
| kruskal_loop30 | turn_aware_astar | 10/10 | 20.4 | 1.409 | 1.232 | 2.2667 | 10.8 | 1.9 | 1.7 | 100.6 |
| kruskal_loop30 | turn_aware_astar_w2 | 10/10 | 20.1 | 1.389 | 1.232 | 2.0667 | 10.4 | 1.8 | 0.905 | 49.8 |
| kruskal_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.241 |  |
| prim_loop0 | dfs | 10/10 | 181.7 | 11.87 | 13.424 | 15.5556 | 148.4 | 82.9 | 0.277 |  |
| prim_loop0 | dstar_lite | 10/10 | 91.6 | 5.997 | 7.078 | 9.0 | 67.1 | 38.7 | 5.986 | 349.4 |
| prim_loop0 | flood_fill | 10/10 | 79.4 | 5.178 | 5.533 | 9.1429 | 52.7 | 32 | 29.035 |  |
| prim_loop0 | frontier | 10/10 | 173.3 | 11.298 | 12.419 | 15.5556 | 140.9 | 78.9 | 0.848 | 221.3 |
| prim_loop0 | greedy_dfs | 10/10 | 148 | 9.612 | 9.744 | 24.0 | 116.7 | 66.3 | 0.794 |  |
| prim_loop0 | prior_astar | 10/10 | 71.6 | 4.664 | 4.756 | 8.4286 | 52.1 | 28.5 | 3.779 |  |
| prim_loop0 | repeated_astar | 10/10 | 88.2 | 5.751 | 6.382 | 8.8571 | 65.3 | 37 | 1.622 |  |
| prim_loop0 | turn_aware_astar | 10/10 | 79.4 | 5.172 | 5.533 | 9.0 | 52.5 | 32 | 8.939 | 860.1 |
| prim_loop0 | turn_aware_astar_w2 | 10/10 | 71.2 | 4.591 | 4.029 | 7.9333 | 47.3 | 27.9 | 3.432 | 777.1 |
| prim_loop0 | wall_follower_left | 10/10 | 209.3 | 13.732 | 13.491 | 18.0714 | 177.5 | 96.7 | 0.342 |  |
| prim_loop10 | dfs | 10/10 | 172.2 | 11.81 | 11.549 | 20.7333 | 137.8 | 64.4 | 0.231 |  |
| prim_loop10 | dstar_lite | 10/10 | 57.8 | 3.953 | 3.4 | 7.6667 | 40 | 17.9 | 2.809 | 225.3 |
| prim_loop10 | flood_fill | 10/10 | 47.9 | 3.257 | 2.938 | 7.8 | 29 | 13.5 | 14.534 |  |
| prim_loop10 | frontier | 10/10 | 148.5 | 10.214 | 10.483 | 13.5714 | 118.7 | 52.2 | 0.775 | 191.5 |
| prim_loop10 | greedy_dfs | 10/10 | 80.7 | 5.531 | 2.929 | 18.4286 | 58.7 | 27.6 | 0.218 |  |
| prim_loop10 | prior_astar | 10/10 | 57.1 | 3.9 | 3.533 | 7.1429 | 40.7 | 17.9 | 2.816 |  |
| prim_loop10 | repeated_astar | 10/10 | 57.8 | 3.952 | 3.4 | 7.5333 | 41 | 17.7 | 0.855 |  |
| prim_loop10 | turn_aware_astar | 10/10 | 51.9 | 3.523 | 3.271 | 7.5333 | 31.4 | 15.4 | 4.644 | 527.3 |
| prim_loop10 | turn_aware_astar_w2 | 10/10 | 47.1 | 3.203 | 2.938 | 7.4 | 28 | 13.5 | 2.971 | 344.2 |
| prim_loop10 | wall_follower_left | 6/10 | 149.5 | 10.429 | 10.607 | 13.1429 | 126.167 | 52.5 | 0.299 |  |
| prim_loop30 | dfs | 10/10 | 132.5 | 9.425 | 10.679 | 14.5714 | 98.7 | 30.7 | 0.187 |  |
| prim_loop30 | dstar_lite | 10/10 | 26.4 | 1.854 | 1.624 | 2.8667 | 15.2 | 3.5 | 1.367 | 110.9 |
| prim_loop30 | flood_fill | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 7.96 |  |
| prim_loop30 | frontier | 10/10 | 125 | 8.89 | 10.036 | 13.4286 | 90.9 | 25.3 | 0.655 | 141.5 |
| prim_loop30 | greedy_dfs | 10/10 | 51 | 3.564 | 2.0 | 11.0714 | 32.2 | 13.4 | 0.148 |  |
| prim_loop30 | prior_astar | 10/10 | 25.8 | 1.819 | 1.624 | 3.3571 | 14.2 | 3.8 | 0.9 |  |
| prim_loop30 | repeated_astar | 10/10 | 25 | 1.761 | 1.624 | 2.6429 | 14 | 2.8 | 0.356 |  |
| prim_loop30 | turn_aware_astar | 10/10 | 26.5 | 1.863 | 1.607 | 2.7333 | 13.4 | 3.7 | 1.687 | 133.9 |
| prim_loop30 | turn_aware_astar_w2 | 10/10 | 26.1 | 1.837 | 1.607 | 2.5 | 13 | 3.5 | 1.194 | 94.1 |
| prim_loop30 | wall_follower_left | 2/10 | 73.5 | 5.11 | 5.11 | 6.2857 | 56.5 | 13.5 | 0.215 |  |
| wilson_loop0 | dfs | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.194 |  |
| wilson_loop0 | dstar_lite | 10/10 | 70.2 | 3.031 | 1.762 | 9.0 | 54.2 | 24.5 | 2.776 | 287.3 |
| wilson_loop0 | flood_fill | 10/10 | 92 | 4.621 | 2.127 | 14.8571 | 68.2 | 33.7 | 30.343 |  |
| wilson_loop0 | frontier | 10/10 | 144.3 | 6.063 | 5.829 | 12.8182 | 118.1 | 59.6 | 0.632 | 182.9 |
| wilson_loop0 | greedy_dfs | 10/10 | 164.9 | 7.764 | 6.292 | 24.7857 | 130.9 | 69.2 | 0.69 |  |
| wilson_loop0 | prior_astar | 10/10 | 68.2 | 2.856 | 1.905 | 5.4167 | 53.8 | 24.3 | 5.031 |  |
| wilson_loop0 | repeated_astar | 10/10 | 66 | 2.935 | 1.762 | 8.9091 | 50.8 | 21.6 | 1.11 |  |
| wilson_loop0 | turn_aware_astar | 10/10 | 93.7 | 4.789 | 2.043 | 17.3571 | 69.3 | 33.8 | 10.333 | 1566.5 |
| wilson_loop0 | turn_aware_astar_w2 | 10/10 | 90 | 4.442 | 2.127 | 12.5714 | 65.8 | 33.2 | 8.863 | 1404.2 |
| wilson_loop0 | wall_follower_left | 10/10 | 149.1 | 6.282 | 5.453 | 13.3333 | 126.5 | 62 | 0.257 |  |
| wilson_loop10 | dfs | 10/10 | 221.5 | 12.638 | 13.026 | 25.4286 | 175.7 | 76.5 | 0.341 |  |
| wilson_loop10 | dstar_lite | 10/10 | 39.5 | 2.102 | 1.771 | 3.4444 | 29.6 | 7 | 1.993 | 161.4 |
| wilson_loop10 | flood_fill | 10/10 | 42.8 | 2.373 | 2.011 | 4.3571 | 29.3 | 7.4 | 12.858 |  |
| wilson_loop10 | frontier | 10/10 | 181.9 | 10.085 | 9.042 | 17.1429 | 141.2 | 55 | 1.002 | 212.6 |
| wilson_loop10 | greedy_dfs | 10/10 | 51.5 | 2.838 | 1.821 | 8.6667 | 35.7 | 11.5 | 0.172 |  |
| wilson_loop10 | prior_astar | 10/10 | 35.4 | 1.845 | 1.804 | 3.1053 | 25.6 | 7 | 2.123 |  |
| wilson_loop10 | repeated_astar | 10/10 | 38.3 | 2.035 | 1.771 | 3.3571 | 28.3 | 7.5 | 0.694 |  |
| wilson_loop10 | turn_aware_astar | 10/10 | 42.6 | 2.358 | 2.011 | 4.2143 | 29.1 | 7.3 | 3.075 | 352.8 |
| wilson_loop10 | turn_aware_astar_w2 | 10/10 | 43.7 | 2.447 | 2.011 | 5.2143 | 30.1 | 9.7 | 2.486 | 350.7 |
| wilson_loop10 | wall_follower_left | 2/10 | 144 | 4.287 | 4.287 | 6.6842 | 112.5 | 44 | 0.431 |  |
| wilson_loop30 | dfs | 10/10 | 204.6 | 14.432 | 14.929 | 17.4286 | 147 | 49.9 | 0.267 |  |
| wilson_loop30 | dstar_lite | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.356 | 89.5 |
| wilson_loop30 | flood_fill | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 7.137 |  |
| wilson_loop30 | frontier | 10/10 | 146.2 | 10.34 | 11.0 | 16.4286 | 102.9 | 27.8 | 0.746 | 174.9 |
| wilson_loop30 | greedy_dfs | 10/10 | 22.4 | 1.585 | 1.464 | 2.8571 | 10.4 | 1.3 | 0.108 |  |
| wilson_loop30 | prior_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 1.099 |  |
| wilson_loop30 | repeated_astar | 10/10 | 19.7 | 1.386 | 1.414 | 1.5714 | 10.8 | 1.1 | 0.345 |  |
| wilson_loop30 | turn_aware_astar | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 1.994 | 100.5 |
| wilson_loop30 | turn_aware_astar_w2 | 10/10 | 21.7 | 1.535 | 1.464 | 2.8571 | 10.2 | 1.3 | 1.145 | 65.3 |
| wilson_loop30 | wall_follower_left | 0/10 |  |  |  |  |  |  | 0.225 |  |
| ALL | dfs | 435/435 | 223.653 | 6.248 | 5.0 | 27.8571 | 134.605 | 72.961 | 0.316 |  |
| ALL | dstar_lite | 435/435 | 95.66 | 2.256 | 1.714 | 28.1429 | 55.17 | 17.586 | 5.232 | 345.308 |
| ALL | flood_fill | 435/435 | 98.867 | 2.317 | 1.851 | 29.7143 | 54.678 | 17.952 | 31.727 |  |
| ALL | frontier | 435/435 | 203.099 | 5.388 | 4.467 | 25.5714 | 120.411 | 55.789 | 0.936 | 279.471 |
| ALL | greedy_dfs | 435/435 | 136.844 | 3.238 | 2.263 | 31.4286 | 80.083 | 36.554 | 0.642 |  |
| ALL | prior_astar | 435/435 | 105.223 | 2.313 | 2.018 | 19.4211 | 62.756 | 27.193 | 8.003 |  |
| ALL | repeated_astar | 435/435 | 94.17 | 2.203 | 1.714 | 28.1429 | 54.685 | 16.887 | 2.117 |  |
| ALL | turn_aware_astar | 435/435 | 98.768 | 2.324 | 1.841 | 30.1429 | 54.745 | 17.749 | 13.673 | 1495.89 |
| ALL | turn_aware_astar_w2 | 435/435 | 98.147 | 2.248 | 1.867 | 29.7143 | 54.536 | 18.738 | 11.486 | 1396.131 |
| ALL | wall_follower_left | 126/435 | 146.254 | 5.437 | 2.246 | 27.2857 | 104.19 | 42.5 | 0.217 |  |

规则代价（成功运行；比值的分母为已知地图上的规则最优代价）：

| 地图组 | 算法 | 平均规则代价 | 代价/最优（均值） | 中位数 | 最大 |
| --- | --- | --- | --- | --- | --- |
| backtracker_loop0 | dfs | 136.55 | 1.189 | 1.0 | 1.7644 |
| backtracker_loop0 | dstar_lite | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | flood_fill | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | frontier | 136.25 | 1.184 | 1.0 | 1.7644 |
| backtracker_loop0 | greedy_dfs | 125.45 | 1.128 | 1.04 | 1.6923 |
| backtracker_loop0 | prior_astar | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | repeated_astar | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | turn_aware_astar_w2 | 102.25 | 1.0 | 1.0 | 1.0 |
| backtracker_loop0 | wall_follower_left | 155.65 | 1.476 | 1.279 | 2.4933 |
| backtracker_loop10 | dfs | 126.1 | 5.163 | 2.512 | 19.7727 |
| backtracker_loop10 | dstar_lite | 36.95 | 1.43 | 1.194 | 2.8182 |
| backtracker_loop10 | flood_fill | 43.35 | 1.72 | 1.259 | 4.4091 |
| backtracker_loop10 | frontier | 86.8 | 3.348 | 2.195 | 10.9091 |
| backtracker_loop10 | greedy_dfs | 54.35 | 2.133 | 1.79 | 4.5 |
| backtracker_loop10 | prior_astar | 34.95 | 1.335 | 1.194 | 2.1343 |
| backtracker_loop10 | repeated_astar | 36.95 | 1.43 | 1.194 | 2.8182 |
| backtracker_loop10 | turn_aware_astar | 41.45 | 1.633 | 1.259 | 3.5455 |
| backtracker_loop10 | turn_aware_astar_w2 | 41.45 | 1.633 | 1.259 | 3.5455 |
| backtracker_loop10 | wall_follower_left | 113.0 | 5.061 | 1.844 | 11.7073 |
| backtracker_loop30 | dfs | 220.2 | 11.063 | 10.383 | 18.9273 |
| backtracker_loop30 | dstar_lite | 27.75 | 1.436 | 1.411 | 1.9444 |
| backtracker_loop30 | flood_fill | 26.3 | 1.38 | 1.349 | 1.8571 |
| backtracker_loop30 | frontier | 150.05 | 7.79 | 9.154 | 11.9143 |
| backtracker_loop30 | greedy_dfs | 32.05 | 1.682 | 1.349 | 4.6579 |
| backtracker_loop30 | prior_astar | 27.75 | 1.436 | 1.411 | 1.9444 |
| backtracker_loop30 | repeated_astar | 27.75 | 1.436 | 1.411 | 1.9444 |
| backtracker_loop30 | turn_aware_astar | 26.3 | 1.38 | 1.349 | 1.8571 |
| backtracker_loop30 | turn_aware_astar_w2 | 26.3 | 1.38 | 1.349 | 1.8571 |
| backtracker_loop30 | wall_follower_left |  |  |  |  |
| external | dfs | 319.098 | 5.262 | 4.78 | 24.6341 |
| external | dstar_lite | 148.44 | 2.373 | 1.886 | 34.0625 |
| external | flood_fill | 152.673 | 2.419 | 1.968 | 34.1875 |
| external | frontier | 298.487 | 4.871 | 4.182 | 24.0 |
| external | greedy_dfs | 211.61 | 3.326 | 2.657 | 29.9024 |
| external | prior_astar | 168.1 | 2.546 | 2.236 | 21.5957 |
| external | repeated_astar | 146.478 | 2.309 | 1.894 | 26.7317 |
| external | turn_aware_astar | 152.419 | 2.419 | 1.965 | 34.1875 |
| external | turn_aware_astar_w2 | 152.149 | 2.348 | 2.012 | 28.1463 |
| external | wall_follower_left | 166.768 | 2.768 | 1.833 | 23.8537 |
| kruskal_loop0 | dfs | 231.55 | 11.713 | 6.179 | 32.9412 |
| kruskal_loop0 | dstar_lite | 44.75 | 1.829 | 1.726 | 3.2121 |
| kruskal_loop0 | flood_fill | 40.35 | 1.634 | 1.443 | 3.303 |
| kruskal_loop0 | frontier | 125.55 | 6.027 | 2.476 | 21.8293 |
| kruskal_loop0 | greedy_dfs | 47.55 | 1.892 | 1.443 | 3.6364 |
| kruskal_loop0 | prior_astar | 45.15 | 1.838 | 1.726 | 3.4545 |
| kruskal_loop0 | repeated_astar | 44.75 | 1.829 | 1.726 | 3.2121 |
| kruskal_loop0 | turn_aware_astar | 40.35 | 1.634 | 1.443 | 3.303 |
| kruskal_loop0 | turn_aware_astar_w2 | 40.35 | 1.634 | 1.443 | 3.303 |
| kruskal_loop0 | wall_follower_left | 365.15 | 17.775 | 19.043 | 31.6471 |
| kruskal_loop10 | dfs | 189.95 | 9.743 | 11.186 | 21.3947 |
| kruskal_loop10 | dstar_lite | 34.4 | 1.67 | 1.655 | 2.6053 |
| kruskal_loop10 | flood_fill | 31.0 | 1.489 | 1.406 | 2.2895 |
| kruskal_loop10 | frontier | 162.9 | 8.224 | 5.982 | 20.2368 |
| kruskal_loop10 | greedy_dfs | 33.8 | 1.61 | 1.5 | 2.8269 |
| kruskal_loop10 | prior_astar | 34.95 | 1.698 | 1.655 | 2.8947 |
| kruskal_loop10 | repeated_astar | 34.4 | 1.67 | 1.655 | 2.6053 |
| kruskal_loop10 | turn_aware_astar | 31.0 | 1.489 | 1.406 | 2.2895 |
| kruskal_loop10 | turn_aware_astar_w2 | 30.2 | 1.458 | 1.364 | 2.2895 |
| kruskal_loop10 | wall_follower_left | 310.5 | 16.703 | 16.703 | 18.2353 |
| kruskal_loop30 | dfs | 230.95 | 13.419 | 13.465 | 24.7742 |
| kruskal_loop30 | dstar_lite | 25.55 | 1.486 | 1.379 | 2.3684 |
| kruskal_loop30 | flood_fill | 25.8 | 1.513 | 1.335 | 2.7576 |
| kruskal_loop30 | frontier | 114.3 | 6.755 | 6.153 | 15.1176 |
| kruskal_loop30 | greedy_dfs | 24.8 | 1.452 | 1.335 | 2.1515 |
| kruskal_loop30 | prior_astar | 25.55 | 1.486 | 1.379 | 2.3684 |
| kruskal_loop30 | repeated_astar | 25.55 | 1.486 | 1.379 | 2.3684 |
| kruskal_loop30 | turn_aware_astar | 25.8 | 1.513 | 1.335 | 2.7576 |
| kruskal_loop30 | turn_aware_astar_w2 | 25.3 | 1.483 | 1.335 | 2.4545 |
| kruskal_loop30 | wall_follower_left |  |  |  |  |
| prim_loop0 | dfs | 255.9 | 13.515 | 15.803 | 18.3953 |
| prim_loop0 | dstar_lite | 125.15 | 6.611 | 7.631 | 9.9412 |
| prim_loop0 | flood_fill | 105.75 | 5.526 | 6.031 | 9.3333 |
| prim_loop0 | frontier | 243.75 | 12.834 | 13.258 | 18.3953 |
| prim_loop0 | greedy_dfs | 206.35 | 10.723 | 10.795 | 25.7568 |
| prim_loop0 | prior_astar | 97.65 | 5.147 | 5.196 | 9.1765 |
| prim_loop0 | repeated_astar | 120.85 | 6.375 | 7.067 | 9.7778 |
| prim_loop0 | turn_aware_astar | 105.65 | 5.517 | 6.031 | 9.3333 |
| prim_loop0 | turn_aware_astar_w2 | 94.85 | 4.935 | 4.036 | 9.3333 |
| prim_loop0 | wall_follower_left | 298.05 | 15.795 | 15.937 | 20.0 |
| prim_loop10 | dfs | 241.1 | 13.679 | 12.892 | 24.4571 |
| prim_loop10 | dstar_lite | 77.8 | 4.356 | 3.859 | 8.7778 |
| prim_loop10 | flood_fill | 62.4 | 3.46 | 3.086 | 8.8889 |
| prim_loop10 | frontier | 207.85 | 11.768 | 11.262 | 16.0556 |
| prim_loop10 | greedy_dfs | 110.05 | 6.16 | 3.225 | 20.9412 |
| prim_loop10 | prior_astar | 77.45 | 4.315 | 3.92 | 7.8824 |
| prim_loop10 | repeated_astar | 78.3 | 4.38 | 3.859 | 8.8333 |
| prim_loop10 | turn_aware_astar | 67.6 | 3.762 | 3.213 | 8.5556 |
| prim_loop10 | turn_aware_astar_w2 | 61.1 | 3.389 | 3.086 | 8.3889 |
| prim_loop10 | wall_follower_left | 212.583 | 12.448 | 13.245 | 15.2941 |
| prim_loop30 | dfs | 181.85 | 11.119 | 12.098 | 18.8 |
| prim_loop30 | dstar_lite | 34.0 | 2.018 | 1.762 | 3.25 |
| prim_loop30 | flood_fill | 33.2 | 1.98 | 1.745 | 3.0278 |
| prim_loop30 | frontier | 170.45 | 10.402 | 11.513 | 17.0667 |
| prim_loop30 | greedy_dfs | 67.1 | 3.946 | 2.191 | 12.2059 |
| prim_loop30 | prior_astar | 32.9 | 1.967 | 1.762 | 3.8125 |
| prim_loop30 | repeated_astar | 32.0 | 1.906 | 1.762 | 2.7941 |
| prim_loop30 | turn_aware_astar | 33.2 | 1.98 | 1.745 | 3.0278 |
| prim_loop30 | turn_aware_astar_w2 | 32.6 | 1.947 | 1.745 | 2.6944 |
| prim_loop30 | wall_follower_left | 101.75 | 5.958 | 5.958 | 7.3333 |
| wilson_loop0 | dfs | 203.35 | 6.704 | 6.427 | 14.2143 |
| wilson_loop0 | dstar_lite | 97.3 | 3.338 | 1.889 | 9.7143 |
| wilson_loop0 | flood_fill | 126.1 | 4.931 | 2.297 | 15.6486 |
| wilson_loop0 | frontier | 203.35 | 6.704 | 6.427 | 14.2143 |
| wilson_loop0 | greedy_dfs | 230.35 | 8.438 | 6.797 | 26.5405 |
| wilson_loop0 | prior_astar | 95.1 | 3.149 | 2.069 | 6.1111 |
| wilson_loop0 | repeated_astar | 91.4 | 3.232 | 1.889 | 9.6786 |
| wilson_loop0 | turn_aware_astar | 128.35 | 5.1 | 2.199 | 18.2703 |
| wilson_loop0 | turn_aware_astar_w2 | 122.9 | 4.721 | 2.297 | 13.0541 |
| wilson_loop0 | wall_follower_left | 212.35 | 7.011 | 6.157 | 14.619 |
| wilson_loop10 | dfs | 309.35 | 13.933 | 13.815 | 29.2286 |
| wilson_loop10 | dstar_lite | 54.3 | 2.269 | 1.911 | 3.7941 |
| wilson_loop10 | flood_fill | 57.45 | 2.523 | 2.161 | 4.6857 |
| wilson_loop10 | frontier | 252.5 | 11.069 | 10.138 | 19.0571 |
| wilson_loop10 | greedy_dfs | 69.35 | 3.003 | 1.962 | 9.234 |
| wilson_loop10 | prior_astar | 48.2 | 1.97 | 1.911 | 3.2353 |
| wilson_loop10 | repeated_astar | 52.45 | 2.19 | 1.911 | 3.7941 |
| wilson_loop10 | turn_aware_astar | 57.15 | 2.506 | 2.161 | 4.5143 |
| wilson_loop10 | turn_aware_astar_w2 | 58.75 | 2.609 | 2.161 | 5.6571 |
| wilson_loop10 | wall_follower_left | 200.25 | 4.793 | 4.793 | 7.5 |
| wilson_loop30 | dfs | 278.1 | 16.588 | 16.429 | 20.6875 |
| wilson_loop30 | dstar_lite | 25.1 | 1.498 | 1.536 | 1.9412 |
| wilson_loop30 | flood_fill | 26.8 | 1.601 | 1.484 | 3.0303 |
| wilson_loop30 | frontier | 197.65 | 11.845 | 12.893 | 17.9714 |
| wilson_loop30 | greedy_dfs | 27.6 | 1.651 | 1.484 | 3.0303 |
| wilson_loop30 | prior_astar | 25.1 | 1.498 | 1.536 | 1.9412 |
| wilson_loop30 | repeated_astar | 25.1 | 1.498 | 1.536 | 1.9412 |
| wilson_loop30 | turn_aware_astar | 26.8 | 1.601 | 1.484 | 3.0303 |
| wilson_loop30 | turn_aware_astar_w2 | 26.8 | 1.601 | 1.484 | 3.0303 |
| wilson_loop30 | wall_follower_left |  |  |  |  |
| ALL | dfs | 290.955 | 6.749 | 5.29 | 32.9412 |
| ALL | dstar_lite | 123.245 | 2.383 | 1.823 | 34.0625 |
| ALL | flood_fill | 126.206 | 2.413 | 1.897 | 34.1875 |
| ALL | frontier | 263.305 | 5.779 | 4.758 | 24.0 |
| ALL | greedy_dfs | 176.885 | 3.416 | 2.348 | 29.9024 |
| ALL | prior_astar | 136.601 | 2.46 | 2.125 | 21.5957 |
| ALL | repeated_astar | 121.513 | 2.326 | 1.835 | 26.7317 |
| ALL | turn_aware_astar | 126.14 | 2.421 | 1.894 | 34.1875 |
| ALL | turn_aware_astar_w2 | 125.415 | 2.339 | 1.923 | 28.1463 |
| ALL | wall_follower_left | 198.349 | 6.047 | 2.22 | 31.6471 |
