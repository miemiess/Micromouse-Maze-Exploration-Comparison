# 直接在 main 上协作

本项目所有组员都在 **main** 上提交。不创建功能分支、不使用 Pull Request。为避免相互覆盖，每次工作前同步、提交前再同步，尽量不要同时编辑同一个文件。

## 1. 第一次准备

仓库所有者先在 GitHub 的 **Settings → Collaborators** 邀请组员，组员接受邀请后才能向私有仓库提交。不要共享账号、密码或令牌。

安装 Git，在 GitHub 仓库页选择 **Code → HTTPS** 复制地址：

```bash
git clone https://github.com/miemiess/Micromouse-Maze-Exploration-Comparison.git
cd Micromouse-Maze-Exploration-Comparison
git branch --show-current
```

最后一条应输出 `main`；若不是，运行 `git switch main`。按 GitHub 提示用你自己的账户登录。

只在尚未配置 Git 身份时设置，替换下面的示例内容：

```bash
git config user.name "你的名字"
git config user.email "你的 GitHub 提交邮箱"
```

## 2. 每次开始工作

```bash
git status
git pull --no-rebase origin main
```

先确保工作区干净；如已有未提交修改，按下一节先检查和提交自己的修改，再拉取。认领 README 任务行，告诉大家自己将修改哪些文件。小步提交，避免数天后才同步。

## 3. 上传本次工作

以完成 DFS 为例，先检查差异，只暂存自己的文件。以下路径按实际修改替换，不要盲目复制尚未存在的文件名。

```bash
git status
git diff
git add src/dfs.py
git diff --cached
git commit -m "实现 DFS 探索与实际移动回溯"
git pull --no-rebase origin main
git push origin main
git status
```

提交前确认没有密码、令牌、缓存、虚拟环境或无关文件。文档放到 `Docs/`；地图放 `mazes/`，数据和图表放 `results/`。README 任务状态更新也需要明确暂存和提交。完成后到 GitHub 页面检查文件和提交记录。

## 4. 推送被拒绝怎么办

通常是其他组员刚更新了 main。**不要强制推送**，先同步再上传：

```bash
git pull --no-rebase origin main
git push origin main
```

出现合并提交编辑器时，保存并退出即可；也可在确认自动合并内容后按提示完成。不要反复执行 push 来跳过冲突。

## 5. 同一文件发生冲突

1. 执行 `git status` 找到冲突文件。
2. 打开文件，寻找 `<<<<<<<`、`=======`、`>>>>>>>` 标记，和相关组员确认要保留的内容，将双方工作合并后删除标记。
3. 本地运行受影响的代码或检查文档，确认没有覆盖别人的功能。
4. 按实际文件路径完成合并：

```bash
git add README.md
git commit -m "合并 main 更新并解决任务表冲突"
git push origin main
```

不会处理时先保留现场并联系组员。不要使用 `git reset --hard`、强制推送或整份覆盖来消除冲突。若想退出本次未完成的合并，可用 `git merge --abort`，再一起处理。

PDF 等二进制文档无法逐行合并：先协调唯一编辑者，再确定保留哪个版本。尽量在 Markdown 中协作写作，最终再导出 PDF。

## 6. 只用 GitHub 网页上传也可以

1. 在页面确认当前分支为 `main`，刷新页面查看组员最新修改。
2. 认领任务。上传前下载/核对最新文件，避免拿旧版本覆盖。
3. 代码进入 `src/`；文档进入 `Docs/`。选择 **Add file → Upload files**，或打开文件后编辑。
4. 填写说明本次工作的中文提交信息，选择 **直接提交到 main**（若界面提供选项），不要新建分支。
5. 提交后检查内容。若页面提示冲突或版本过期，先刷新并重新合并，不直接覆盖。

网页提交后，本地继续工作的人需要重新执行 `git pull --no-rebase origin main`。所有人围绕同一个 main，同一文件尽量按时间错开修改。
