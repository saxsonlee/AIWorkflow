# AIWorkflow Setup

## 本文职责

本文说明新项目初始化、模板烟测和迁移检查。它回答“把 AIWorkflow 放到新项目后怎么启动”。

## 权限边界

本文只定义初始化顺序和迁移检查，不定义 Core 架构规则、不定义 check / driver / mode 职责、不定义项目专用验收内容。

## 新项目初始化

在一个新项目中接入 AIWorkflow 时，普通用户只需要完成最小安装：

1. 将开源仓库中的 `AIWorkflow/` 目录复制到目标项目根目录。目标项目最终应存在 `AIWorkflow/README.md`、`AIWorkflow/Core/`、`AIWorkflow/Workspace.Template/` 和 `AIWorkflow/Skill.Template/`。
2. 从 `Workspace.Template/` 创建新的 `Workspace/`，作为当前项目自己的工作区。
3. 开源仓库包含 `.codex/` 触发规则。使用 Codex 时，建议把 `.codex/` 一起复制到目标项目根目录。也可以在 `Skill.Template/` 运行安装定位脚本找到 Codex 的 `skills` 安装位置：Windows 使用 `find_codex_skills.bat`，Linux / macOS 使用 `sh find_codex_skills.sh`。优先安装到项目 `.codex/skills/aiworkflow-trigger/`，只有多个项目共享同一套触发规则时才安装到用户 skills 目录。

完成后即可向 AI 描述真实任务。AI 会读取 `Workspace/AITDDPolicy.json`，按策略创建或切换正式 Topic / Issue / Iteration，并在需要验收时执行对应 runner 命令。

可选维护项：

- 需要调整默认启用策略时，修改 `Workspace/AITDDPolicy.json`。
- 目标项目需要专用执行器、专用 checks 或 Core 外验收配方时，再创建 `Adapters/` 或 `Modes/`。
- 需要排查安装、CI 接入或维护脚本时，再手动运行 `validate-*`、`run --dry-run`、`run --template-smoke`、`list-checks` 或 `list-modes`。

需要手动维护工作区结构时，查看 `Core/docs/data-model.md`。

## AITDDPolicy.json

`Workspace/AITDDPolicy.json` 是项目级 AITDD 开关。AI 必须读取这个文件后执行策略，而不是自行判断是否启用。

核心字段：

- `defaultMode`：`enabled` 表示默认启用 AITDD，`manual` 表示仅在用户明确要求时使用，`off` 表示默认关闭。
- `formalRunPolicy`：`explicit` 表示正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段；`auto` 表示允许 AI 在项目规则、当前 Iteration 和验收配置都明确时自动发起正式 `run`。
- `templateWorkspacePolicy`：当前固定为 `smoke-only`，表示模板工作区只能用于安装烟测。

查看或切换：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy show
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode off
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy explicit
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy auto
```

## 模板烟测

`Workspace.Template/` 已内置 `ExampleTopic / ExampleIssue / v0.1.0` 示例，并在 `acceptance.modes` 中使用 `aiworkflow_minimal` mode，可作为新项目首次运行的最小验收链路。

`run --dry-run` 用于预览当前 Iteration 解析出的 `modes`、证据要求、checks 和 postChecks。它不生成 `Runs/` 目录，不更新 `LatestRun.md`，不回写 Iteration 状态，也不形成正式 pass/fail 记录。

由模板创建的 `Workspace/` 默认 `source` 是 `TEMPLATE`。

普通 `run` 遇到模板工作区会返回 `blocked`。

模板安装烟测应使用：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --template-smoke
```

## 手动检查

普通用户通常不需要手动运行这些命令。排查安装、CI 接入或维护脚本需要时，可从宿主项目根目录运行：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-current
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-resolution
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-iteration
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --dry-run
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --template-smoke
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py list-checks
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py list-modes
```

如果要保留历史工作区，可整体复制 `Workspace/`。如果只复用流程，不需要复制旧 `Workspace/Topics/`。
