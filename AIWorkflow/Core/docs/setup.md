# AIWorkflow Setup

## 本文职责

本文说明新项目初始化、模板烟测和迁移检查。它回答“把 AIWorkflow 放到新项目后怎么启动”。

## 权限边界

本文只定义初始化顺序和迁移检查，不定义 Core 架构规则、不定义 check / driver / mode 职责、不定义项目专用验收内容。

## 新项目初始化

在一个新项目中接入 AIWorkflow 时，建议按以下顺序初始化：

1. 将开源仓库中的 `AIWorkflow/` 目录复制到目标项目根目录。目标项目最终应存在 `AIWorkflow/README.md`、`AIWorkflow/Core/`、`AIWorkflow/Workspace.Template/` 和 `AIWorkflow/Skill.Template/`。
2. 从 `Workspace.Template/` 创建新的 `Workspace/`，作为当前项目自己的工作区。
3. 如果开源仓库中带有 `.codex/`，可以把 `.codex/` 同时复制到目标项目根目录。也可以在 `Skill.Template/` 运行安装定位脚本找到 Codex 的 `skills` 安装位置：Windows 使用 `find_codex_skills.bat`，Linux / macOS 使用 `sh find_codex_skills.sh`。优先安装到项目 `.codex/skills/aiworkflow-trigger/`，只有多个项目共享同一套触发规则时才安装到用户 skills 目录。
4. 直接运行 `validate-current`、`validate-resolution`、`validate-iteration`、`run --dry-run` 和 `run --template-smoke`，确认模板结构可用。
5. 查看或修改 `Workspace/AITDDPolicy.json`，决定当前项目是否默认启用 AITDD。
6. 编辑 `Workspace/Current.json`，指向项目自己的第一个 `Topic / Issue / Resolution / Iteration`。
7. 修改或替换对应的 `Issue.md`、`Decision.md`、`Resolution/Resolution.json` 和 `Resolution/Iterations/v0.1.0.md`。
8. 如目标项目需要专用执行器、专用 checks 或 Core 外验收配方，再创建 `Adapters/` 或 `Modes/`。

## 最小 Current.json

```json
{
  "schemaVersion": "1.0",
  "topic": "ExampleTopic",
  "topicPath": "Workspace/Topics/ExampleTopic",
  "issue": "ExampleIssue",
  "issuePath": "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Issue.md",
  "decisionPath": "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Decision.md",
  "resolutionPath": "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Resolution.json",
  "currentIteration": "v0.1.0",
  "iterationPath": "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Iterations/v0.1.0.md",
  "updatedAt": "",
  "source": "AI_CONTEXT"
}
```

## AITDDPolicy.json

`Workspace/AITDDPolicy.json` 是项目级 AITDD 开关。AI 必须读取这个文件后执行策略，而不是自行判断是否启用。

核心字段：

- `defaultMode`：`enabled` 表示默认启用 AITDD，`manual` 表示仅在用户明确要求时使用，`off` 表示默认关闭。
- `formalRunPolicy`：`explicit` 表示正式 `run` 需要用户明确要求，`auto` 表示允许按项目规则自动正式运行。
- `templateWorkspacePolicy`：当前固定为 `smoke-only`，表示模板工作区只能用于安装烟测。

查看或切换：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy show
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode off
```

## 模板烟测

`Workspace.Template/` 已内置 `ExampleTopic / ExampleIssue / v0.1.0` 示例，并在 `acceptance.modes` 中使用 `aiworkflow_minimal` mode，可作为新项目首次运行的最小验收链路。

由模板创建的 `Workspace/` 默认 `source` 是 `TEMPLATE`。

普通 `run` 遇到模板工作区会返回 `blocked`。

模板安装烟测应使用：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --template-smoke
```

## 迁移后检查

迁移后优先检查：

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
