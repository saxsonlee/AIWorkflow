# AIWorkflow

AIWorkflow 是一套可迁移的 AI-TDD 验收工作流，用来让 AI 交付可复验的验收证据，而不只是口头说明“已经完成”。

## 核心理念

AIWorkflow 的核心是让 AI 工作具备两个长期特征：

1. 长期保持

   每次工作都留下可复验的证据、决策、上下文和运行结果。即使换线程、换 AI、换项目，后续协作者也能从仓库里的结构化记录接上。

2. 不断进化

   验收能力会随着项目推进逐步沉淀。事实验证进入 `check`，流程执行进入 `driver`，验收组合进入 `mode`，项目越使用，AI 越知道这个项目应该怎么验收、怎么交付。

## 安装

本文件位于 `AIWorkflow/README.md`。接入其他项目时，目标项目根目录下应存在一个完整的 `AIWorkflow/` 目录：

```text
YourProject/
  .codex/                 # 可选：AI 触发规则
  AIWorkflow/
    README.md
    Core/
    Workspace.Template/
    Skill.Template/
```

如果你是从开源仓库接入，复制仓库中的 `AIWorkflow/` 目录到目标项目根目录。开源仓库同时包含 `.codex/` 触发规则；使用 Codex 时，建议把 `.codex/` 一起复制到目标项目根目录：

```text
AIWorkflow-Repo/
  .codex/
  AIWorkflow/
```

目标项目最终必须存在：

```text
AIWorkflow/Core/Acceptance/acceptance_runner.py
```

使用 Codex 时，建议同时存在：

```text
.codex/skills/aiworkflow-trigger/SKILL.md
```

`.codex/` 只用于让支持 Codex skill 的环境自动识别 AIWorkflow。不使用 Codex 时可以忽略它，也可以手动运行 `AIWorkflow/Core/Acceptance/acceptance_runner.py`。

保持目录名为 `AIWorkflow`。Core 内部路径都以 `AIWorkflow/` 为起点，不依赖当前项目名称。

首次接入新项目时，如果还没有工作区，使用模板创建 `Workspace/`：

Windows：

```bat
xcopy AIWorkflow\Workspace.Template AIWorkflow\Workspace /E /I
```

Linux / macOS：

```sh
cp -R AIWorkflow/Workspace.Template AIWorkflow/Workspace
```

如果目标项目已经有自己的 `AIWorkflow/Workspace/`，不要覆盖它。`Workspace/` 保存当前项目的 `Topic / Issue / Resolution / Iteration / Run`，属于项目过程资产。

`Workspace/AITDDPolicy.json` 保存当前项目的 AITDD 开关。AI 不应凭感觉决定是否启用 AITDD，而应先读取这个文件：

- `defaultMode: "enabled"`：默认启用 AITDD，用户不需要每次显式说明。
- `defaultMode: "manual"`：只有用户明确要求时才使用 AITDD。
- `defaultMode: "off"`：默认不使用 AITDD，除非用户临时要求。
- `formalRunPolicy: "explicit"`：正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。否则只运行 `validate-*` 和 `run --dry-run`。
- `formalRunPolicy: "auto"`：允许 AI 在项目规则、当前 Iteration 和验收配置都明确时自动发起正式 `run`。模板工作区仍只能运行安装烟测。

可以用 Python 命令查看或切换：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy show
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode off
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy explicit
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy auto
```

### 安装 AI 触发规则

当前版本提供 Codex 触发规则模板，用来让 AI 知道什么时候进入 AIWorkflow。以后如果支持其他 IDE 或 AI 助手，也应接入同一套 `Topic / Issue / Resolution / Iteration / Run` 流程。

Windows：

```bat
AIWorkflow\Skill.Template\find_codex_skills.bat
```

Linux / macOS：

```sh
sh AIWorkflow/Skill.Template/find_codex_skills.sh
```

脚本会优先安装到项目 `.codex/skills/aiworkflow-trigger/`。如果找不到项目 `.codex`，会尝试安装到用户级 Codex skills 目录。

安装细节见 `Skill.Template/README.md`。

### 安装后使用

复制出 `Workspace/` 并安装触发规则后，普通使用不需要手动记 runner 命令。直接向 AI 描述任务即可；AI 会读取 `Workspace/AITDDPolicy.json`，按项目策略判断是否进入 AIWorkflow、是否需要创建或切换正式 `Topic / Issue / Iteration`，并在需要验收时展示执行结果。

`run --template-smoke` 只是模板安装烟测，通常只在排查安装问题时使用。runner 命令说明见 `Core/docs/runner.md`。

## 开始真实任务

模板内置的 `ExampleTopic / ExampleIssue` 只是安装示例，不要当作真实任务。

正常使用时，复制出 `Workspace/` 后就可以开始向 AI 描述任务。AI 会根据 `Workspace/AITDDPolicy.json` 和当前请求判断是否需要创建或切换正式 `Topic / Issue / Iteration`，并在需要验收时运行 `validate-*` 和 `run --dry-run`。

常用说法：

```text
请按 AIWorkflow 为这个任务创建或切换到合适的 Topic / Issue / Iteration，并先只运行 validate-* 和 run --dry-run。
```

需要生成正式验收记录时，再明确说：

```text
请执行正式 AIWorkflow run，并把 Report / Result 路径告诉我。
```

如果只是想讨论方案，可以说：

```text
先不用 AITDD，只讨论方案。
```

详细初始化步骤见 `Core/docs/setup.md`。数据结构和扩展规则见 `Core/docs/data-model.md`、`Core/docs/check-driver-mode.md` 和 `Core/docs/extension-boundary.md`。

## 文档

`Core/README.md` 是 Core 文档入口。常用文档：

- `Core/docs/setup.md`：新项目初始化、模板烟测和迁移检查。
- `Core/docs/data-model.md`：`Topic / Issue / Resolution / Iteration / Run` 数据模型。
- `Core/docs/runner.md`：runner 命令、状态和 Run 产物。
- `Core/docs/check-driver-mode.md`：Check / Driver / Mode 职责和证据覆盖规则。
- `Core/docs/extension-boundary.md`：Core、Adapters、Modes 和宿主项目规则的边界。
- `Core/docs/path-rules.md`：AIWorkflow 相对路径规则。
- `Core/docs/architecture.md`：目录职责和架构边界。

## 进一步了解

AITDD 不要求 AI 只是声称“已经完成”。它要求 AI 把一次工作组织为 `Topic / Issue / Resolution / Iteration / Run`，并为每次正式验收生成可长期保存的证据：

- `AcceptanceReport.md`：给人看的验收报告。
- `Result.json`：给机器读取的结构化结果。
- `Run.log`：给排查问题用的执行日志。

AI 写代码很快，但“快”不足以证明一次工作已经可靠完成。没有工作流时，AI 的一次修改经常难以回答：

- 这次变更属于哪个问题？
- 本次目标和决策是什么？
- 哪些检查证明它通过了？
- 另一个 AI 能不能接着做？
- 这次验收能力能不能下次复用？

AIWorkflow 的目标是把这些内容落到仓库里，形成可追踪、可复验、可迁移、可沉淀的工程事实。

1. 让 AI 的工作留下验收证据

   每次工作都有 `Topic / Issue / Resolution / Iteration / Run`，并产出 `AcceptanceReport.md`、`Result.json`、`Run.log`。结果不是靠聊天记录证明“做过了”，而是落到仓库里的验收证据。

2. 让项目逐步沉淀验收能力

   新的验收能力通常从一次任务开始：事实验证写成 `check`，流程执行写成 `driver`，本次组合写成 `temp mode`。长期复用后，稳定的验收配方再沉淀为正式 `mode`。项目越使用，`check / driver / mode` 三层能力越完整，AI 越知道这个项目应该怎么验收、怎么交付。

3. 区分静态契约和真实行为证据

   `contract / behavior / browser` 三类证据用于区分静态结构、行为流程和浏览器/UI 交互，避免 AI 用文本检查、编译检查或文档检查冒充业务闭环。

4. 拆分事实、流程和验收配方

   `check` 只验证一个明确事实，`driver` 执行非原子流程并产出机器结果，`mode` 组合多个验收事实。这样失败原因更容易定位，验收能力也更容易复用。

5. 保持可迁移，不绑定具体项目

   `Core/` 保持技术中立，项目差异进入 `Adapters/`、`Modes/` 或宿主项目规则。它可以从 Unity 项目迁移到 Python、Web、后端或其他项目。

6. 降低 AI 丢上下文的风险

   当前任务指针、决策、迭代目标、验收结果都会落盘。即使换线程、换 AI、换项目，也可以从 `Current.json`、`Resolution.json`、`LatestRun.md` 接上。

7. 支持开源协作和团队协作

   AI 的工作不只是“我跟 AI 聊过”，而是变成仓库里的结构化过程资产。别人能看、能跑、能复验。
