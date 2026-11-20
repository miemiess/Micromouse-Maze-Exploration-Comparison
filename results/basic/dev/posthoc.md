# 事后分析：按地图来源分层的开发集

> **看过测试结果之后做的分析，不是正式结论。** 外部迷宫库的全部地图此前都作为测试集使用过，这里的留出集并非从未见过的数据；正式结论以实验 1 与冻结的 c = 2.5 为准。规则见 `src/basic/posthoc_stratified.py` 的说明。

- 开发集：120 张生成图（种子 101～110）+ 79 张外部迷宫库地图（按 maze_id 排序后用 random.Random(2026) 抽取 20%）
- 留出集：其余 315 张外部迷宫库地图 + 120 张生成测试图（实验 1 的种子 1～10）

## 在分层开发集上调参

| c | 开发集全部 | 其中生成图 | 其中外部图 |
| --- | --- | --- | --- |
| 0 | 2.058（1.611） | 2.099（1.571） | 1.996（1.647） |
| 0.25 | 2.060（1.625） | 2.078（1.571） | 2.032（1.718） |
| 0.5 | 2.076（1.643） | 2.070（1.571） | 2.085（1.718） |
| 1 | 2.093（1.686） | 2.058（1.571） | 2.146（1.800） |
| 1.5 | 2.130（1.708） | 2.045（1.580） | 2.259（1.809） |
| 2 | 2.089（1.774） | 1.958（1.612） | 2.288（2.000） |
| 2.5 | 2.113（1.800） | 1.957（1.612） | 2.350（2.118） |
| 3 | 2.133（1.809） | 1.972（1.640） | 2.378（2.029） |

选定：c = 0（原正式流程只用生成图选出 c = 2.5）

## 在留出集上评估

均值（中位数）；+ / − 为与重复 A* 逐张比较步数更少 / 更多的地图数。

| 方法 | 留出集全部 | 外部图 | 生成图 | 外部图 + / − |
| --- | --- | --- | --- | --- |
| 重复 A* | 2.203（1.714） | 2.211（1.815） | 2.181（1.517） | 0 / 0 |
| 分层调参 c = 0 | 2.203（1.714） | 2.211（1.815） | 2.181（1.517） | 1 / 1 |
| 原冻结 c = 2.5 | 2.313（2.018） | 2.409（2.167） | 2.061（1.488） | 62 / 209 |

开发集抽出的外部迷宫库地图：external_111、external_2003kankou、external_86、external_Japan2013eq、external_allamerica2013、external_apec1998、external_apec2013、external_apec2014、external_beam94b、external_boston、external_c00d2f、external_c00d3p、external_c00jcf、external_chubu2017、external_euro-58、external_japan1986、external_japan1991、external_japan1997、external_japan1999f、external_japan2000ef、external_japan2017ef、external_japan4、external_kilkai、external_kilnew、external_koh、external_kwu2、external_long、external_map-1、external_map-5、external_map-e5、external_map-g4、external_map-y4-2、external_map-y4-3、external_maze06、external_maze08、external_mc-meiro-2015、external_minos08f、external_minos14、external_mr6、external_museum、external_opd102、external_quo4、external_robofest-2016-final、external_robotic-2010-finals、external_robotic-2011-follower-finals、external_robotic-2011-solver-heats、external_sd1f04、external_sd1p02、external_sd1p04、external_sd3f01、external_sd3p04、external_seoul2、external_sg87、external_sg88、external_shi2、external_sing89i、external_sizuka、external_solver、external_sq89su、external_sunada、external_sy15、external_taiwan-2013-final、external_test2、external_tricky、external_uk1987f、external_uk1988f、external_uk2003q、external_uk2006f、external_uk2008final、external_uk2012f、external_uk2014f、external_us01、external_us83、external_us86x、external_us91、external_vm1、external_wiggly1、external_zigzag、external_zigzag3
