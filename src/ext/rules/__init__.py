"""扩展规则层：每个模块定义若干叠加层（core.rules.RuleLayer 的子类），并在 LAYERS 中列出。

core.rules.available_layers() 自动发现这里的层，界面、命令行（--rule）与实验框架随之可用，
无需修改其他文件。规则的抽象与代价计算在公共接口层 src/core/rules.py。
"""
