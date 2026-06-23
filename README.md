# AIWorkflow

AIWorkflow 是一套可迁移的 AI-TDD 验收工作流，用来让 AI 交付可复验的验收证据，而不只是口头说明“已经完成”。

## 这个仓库怎么放进项目

这个仓库根目录不是目标项目里的 AIWorkflow 根目录。真正要放进目标项目的是仓库中的 `AIWorkflow/` 目录。

推荐结构：

```text
YourProject/
  .codex/       # 可选：让 Codex 自动识别 AIWorkflow
  AIWorkflow/   # 必需：AIWorkflow 主体
```

本仓库结构：

```text
AIWorkflow-Repo/
  README.md
  .codex/
  AIWorkflow/
```

接入一个已有项目时，先把本仓库 clone 到任意临时位置，再复制：

```text
AIWorkflow-Repo/AIWorkflow/ -> YourProject/AIWorkflow/
AIWorkflow-Repo/.codex/     -> YourProject/.codex/
```

如果目标项目本身已经是 Git 仓库，不建议直接在目标项目中 clone 本仓库形成嵌套 Git 仓库。复制目录会更清楚。

## 安装后

进入目标项目根目录，先从模板创建工作区：

```bat
xcopy AIWorkflow\Workspace.Template AIWorkflow\Workspace /E /I
```

Linux / macOS：

```sh
cp -R AIWorkflow/Workspace.Template AIWorkflow/Workspace
```

然后运行自检：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-current
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-resolution
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-iteration
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --dry-run
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --template-smoke
```

`run --template-smoke` 只证明安装可运行。真实任务验收前，需要创建或切换到正式 `Topic / Issue / Iteration`。

更多说明见 `AIWorkflow/README.md`。
