# AIWorkflow Skill Template

`Skill.Template/` 用于把 AIWorkflow 的触发规则安装到新项目的 Codex 环境中。

## 安装

这个 skill 的作用是让 Codex 识别什么时候应该进入 AIWorkflow。它不直接执行验收，验收仍由 `AIWorkflow/Core/Acceptance/acceptance_runner.py` 执行。

是否默认进入 AIWorkflow 由目标项目的 `AIWorkflow/Workspace/AITDDPolicy.json` 决定，不靠 AI 自行判断。

按操作系统选择安装脚本。

Windows 下在当前目录运行：

```bat
find_codex_skills.bat
```

Linux / macOS 下在当前目录运行：

```sh
sh find_codex_skills.sh
```

脚本会从自身所在目录向上查找 `.codex` 目录，并把 `aiworkflow-trigger/` 复制到对应的 `skills` 安装位置。Windows 脚本执行结束会停留在命令行窗口，方便查看成功或错误信息。

## 安装环境

优先使用项目安装：

```text
<项目或父级目录>/.codex/skills/aiworkflow-trigger/
```

项目安装只影响当前项目，适合 AIWorkflow 这类和项目工作区绑定的触发规则。

如果希望所有项目共用同一套触发规则，也可以使用用户安装：

```text
Windows: %USERPROFILE%/.codex/skills/aiworkflow-trigger/
Linux/macOS: ~/.codex/skills/aiworkflow-trigger/
```

用户安装会影响同一用户下的多个项目，只有当这些项目都使用相同的 `AIWorkflow/` 目录约定时才建议使用。

如果需要手动安装，将目录：

```text
AIWorkflow/Skill.Template/aiworkflow-trigger/
```

复制到目标项目：

```text
.codex/skills/aiworkflow-trigger/
```

安装后，新项目中的 skill 文件应位于：

```text
.codex/skills/aiworkflow-trigger/SKILL.md
```

也就是需要把 `aiworkflow-trigger/` 复制到选定安装环境的 `skills` 文件夹中。优先使用脚本安装，避免双击时工作目录不正确导致复制到错误位置。

## 初始化检查

在目标项目中确认以下文件存在：

```text
AIWorkflow/Core/Acceptance/acceptance_runner.py
AIWorkflow/Workspace/Current.json
.codex/skills/aiworkflow-trigger/SKILL.md
```

然后运行：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-current
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-resolution
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-iteration
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --dry-run
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --template-smoke
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy show
```

`run --dry-run` 用于预览当前 Iteration 解析出的验收配置、证据要求和 checks，不生成 `Runs/` 目录，不更新 `LatestRun.md`，也不形成正式 pass/fail 记录。

`run --template-smoke` 只用于确认模板安装可运行。真实任务验收前，应先创建或切换到正式 `Topic / Issue / Iteration`，不能直接把 `ExampleTopic / ExampleIssue` 的 Run 当作任务验收结果。

## AITDD 开关

`AIWorkflow/Workspace/AITDDPolicy.json` 保存项目级策略：

- `defaultMode: "enabled"`：默认启用 AITDD，用户不需要每次显式说明。
- `defaultMode: "manual"`：只有用户明确要求时才使用 AITDD。
- `defaultMode: "off"`：默认不使用 AITDD，除非用户临时要求。
- `formalRunPolicy: "explicit"`：正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。否则只运行 `validate-*` 和 `run --dry-run`。
- `formalRunPolicy: "auto"`：允许 AI 在项目规则、当前 Iteration 和验收配置都明确时自动发起正式 `run`。模板工作区仍只能运行安装烟测。

用 Python 命令查看或切换：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy show
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode off
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy explicit
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy auto
```

## 使用边界

`Skill.Template/` 只负责让 Codex 知道什么时候进入 AIWorkflow。

`Core/` 仍然只保存可迁移的运行时能力。

`Workspace/` 仍然保存当前项目自己的 Topic / Issue / Resolution / Iteration / Run。
