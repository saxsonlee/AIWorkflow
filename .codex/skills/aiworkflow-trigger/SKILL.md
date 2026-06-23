---
name: aiworkflow-trigger
description: 当目标项目安装了 AIWorkflow，且 Workspace/AITDDPolicy.json 启用或用户明确要求 AIWorkflow、AI-TDD、验收流程、Topic / Issue / Resolution / Iteration 判断、AcceptanceRunner、运行验收，或要求为当前产出定义可运行验收条件、脚本、报告、归档时使用。当前请求需要创建、切换、拆分或实质修改 AIWorkflow Issue / Resolution / Iteration 时也使用。
---

# AIWorkflow 触发规则

本 skill 用于让 Codex 在目标项目中识别并使用 AIWorkflow。

## 核心规则

不要让 AI 自行猜测是否启用 AIWorkflow。是否默认启用由项目内的 `Workspace/AITDDPolicy.json` 决定。

AI 必须读取本文件后执行策略；聊天上下文、任务措辞和模型偏好都不能替代该开关。

如果 `Workspace/AITDDPolicy.json` 不存在，只在用户明确要求 AIWorkflow、AI-TDD、验收流程或正式验收时使用 AIWorkflow，并提示先运行 `policy init` 或从 `Workspace.Template/` 创建工作区。

AIWorkflow 默认安装在目标项目的：

```text
AIWorkflow/
```

如果目标项目使用了其他目录，应优先按实际目录读取 `Workspace/Current.json` 和执行 `Core/Acceptance/acceptance_runner.py`。

## 应使用 AIWorkflow 的情况

- `Workspace/AITDDPolicy.json` 的 `defaultMode` 是 `enabled`，且当前请求涉及实现、修复、重构、测试、验证、验收、提交或发布等真实交付。
- 用户明确要求使用 AIWorkflow、AI-TDD、验收流程、Topic / Issue / Resolution / Iteration、AcceptanceRunner 或运行验收。
- 当前任务需要创建、切换、拆分或实质修改 AIWorkflow Issue / Resolution / Iteration。
- 当前任务需要判断一个请求属于当前 Issue / Resolution / Iteration，还是应该成为新的 Issue 或新的 Iteration。
- 当前任务需要定义可运行的验收条件、验收脚本、报告、结果文件、日志或归档。
- 用户要求检查某个阶段产物是否满足已定义目标。

## 默认不使用 AIWorkflow 的情况

- `Workspace/AITDDPolicy.json` 的 `defaultMode` 是 `off`，且用户没有临时要求使用 AIWorkflow。
- `Workspace/AITDDPolicy.json` 的 `defaultMode` 是 `manual`，且用户没有明确要求使用 AIWorkflow、AI-TDD、验收流程或正式验收。
- 用户明确说“先不用 AITDD”“只讨论”或“不需要验收”。
- 普通代码修改、文件查看、概念解释、目录检查。
- 不需要 Issue / Resolution / Iteration 判断的局部实现。
- 不需要验收结果、报告、日志或归档的临时问答。

## 使用前置步骤

当 AIWorkflow 被触发时，先读取：

```text
AIWorkflow/Workspace/AITDDPolicy.json
AIWorkflow/Workspace/Current.json
AIWorkflow/Core/README.md
```

然后按 `AITDDPolicy.json` 决定默认行为，并遵守 Topic / Issue / Resolution / Iteration 边界规则，再修改任何 AIWorkflow 文件。

策略含义：

- `defaultMode: "enabled"`：当前项目默认启用 AITDD。用户不需要每次显式说明；AI 应在真实交付类任务中进入 AIWorkflow 判断链路。
- `defaultMode: "manual"`：只有用户明确要求 AIWorkflow、AI-TDD、验收流程或正式验收时才进入 AIWorkflow。
- `defaultMode: "off"`：默认不使用 AIWorkflow；只有用户临时要求时才进入。
- `formalRunPolicy: "explicit"`：正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。否则只运行 `validate-*` 和 `run --dry-run`。
- `templateWorkspacePolicy: "smoke-only"`：模板工作区只能用于安装烟测，不能作为真实任务验收入口。

可用以下命令查看或切换策略：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy show
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python AIWorkflow\Core\Acceptance\acceptance_runner.py policy set --default-mode off
```

`AIWorkflow/Core/README.md` 是入口页。根据任务继续读取对应 Core docs：

- 涉及目录职责或架构边界，读取 `AIWorkflow/Core/docs/architecture.md`。
- 涉及路径、报告入口或可迁移路径，读取 `AIWorkflow/Core/docs/path-rules.md`。
- 涉及 Topic / Issue / Resolution / Iteration / Run，读取 `AIWorkflow/Core/docs/data-model.md`。
- 涉及 runner 命令、Run 产物或模板烟测，读取 `AIWorkflow/Core/docs/runner.md`。
- 涉及 check、driver、mode 或验收拆分，读取 `AIWorkflow/Core/docs/check-driver-mode.md`。
- 涉及 Core、Adapters、Modes 的扩展归属，读取 `AIWorkflow/Core/docs/extension-boundary.md`。
- 涉及新项目初始化、迁移检查或安装烟测，读取 `AIWorkflow/Core/docs/setup.md`。

如果 `AIWorkflow/Workspace/Current.json` 的 `source` 是 `TEMPLATE`，或当前指向 `ExampleTopic / ExampleIssue`，该工作区只能用于安装烟测，不能作为真实任务验收入口。

真实任务验收前，必须先创建或切换到正式 `Topic / Issue / Iteration`，并在当前 Iteration 中声明验收条件。外部脚本、HTTP、WebSocket、构建或运行时验证可以作为 check / driver 的实现细节，但验收结果必须进入当前 Issue 的 Run 目录。

## Check 原子性规则

Check 是可复用的事实验证单元。一个 check 只能验证一种事实。

不得把契约检查、环境准备和行为验收塞进同一个 check。

跨环境准备、服务启动、登录、数据注入、连续请求等流程必须放入 driver。

Driver 可以准备环境、执行流程并产出机器结果；check 只验证一个明确结果。Mode 负责组合多个原子 check。

如果一个验收目标需要同时证明契约、准备过程和行为结果，应拆成多个 check，并在 mode 中组合。当前 Iteration 需要同时运行多个 mode 时，写入 `Resolution.json` 的 `acceptance.modes`。

## Driver 职责规则

Driver 是流程执行和环境适配单元。

跨环境准备、服务启动、登录、数据注入、临时数据库构造、连续请求和多阶段业务流程必须放入 driver。

Driver 可以执行流程并产出 JSON、日志、状态文件或 Run 产物。Driver 不直接代表最终验收结论；check 必须读取输入或 driver 产物，只验证一个明确事实。

如果 driver 产出多个事实，必须拆成多个 check 分别验证，不要把多个验收目标压成一个 driver 布尔结果。

## 证据覆盖规则

创建或修改 Iteration acceptance 时，必须判断本次验收需要哪些证据类型，并写入 `acceptance.requiredEvidence`。

允许的证据类型：

- `contract`：静态结构、接口契约、文件、文本、JSON 字段、命名、编译或解析等事实。
- `behavior`：由 driver 执行非原子流程后产出的机器事实。
- `browser`：由浏览器、UI 或端到端交互 driver 产出的机器事实。

正式 `run` 必须覆盖 `requiredEvidence` 中声明的每一种证据类型。`behavior` 和 `browser` 类型的 check 必须引用 driver、driver 产物或显式 driver evidence；不能只用静态 contract check 代替。

Core runner 不根据自然语言关键词判断需求应该需要哪种证据。这个判断必须在当前 Iteration、mode 或宿主项目规则中显式完成。

报告中应区分 contract acceptance、behavior acceptance 和 browser/UI acceptance。

## Mode 职责规则

Mode 是验收配方，负责组合多个原子 check。

Mode 可以选择 check、提供参数、声明名称和 required / optional 严重级别，并组合 Core、Adapters 或项目自定义 check。

长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode。当前 Iteration 的一次性检查集合应沉淀为 `temp.*` mode。Iteration 的 `extraChecks` 只保存无法形成 mode 的极少数临时补充事实。

如果某个 `extraChecks` 在多个 Iteration 中反复出现，或已经成为发布门禁、项目惯例、技术栈惯例，应迁移到对应 mode。

Mode 文件本身不引用其他 mode。多个 mode 的组合关系只写在 `Resolution.json` 的 `acceptance.modes` 中。

Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求。这类流程必须放入 driver，mode 只引用读取 driver 产物的 check。

Mode 不承担 check 的判断逻辑，也不承担 driver 的执行流程；它只回答“本次验收由哪些事实组成”。

## 验收命令

修改 AIWorkflow 的 Issue / Resolution / Iteration 或验收配置后，至少运行：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-current
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-resolution
python AIWorkflow\Core\Acceptance\acceptance_runner.py validate-iteration
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --dry-run
```

模板安装烟测可以运行：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py run --template-smoke
```

模板安装烟测只证明 AIWorkflow 安装可运行，不能替代真实任务验收。

当需要形成正式验收记录时，运行：

```powershell
python AIWorkflow\Core\Acceptance\acceptance_runner.py run
python AIWorkflow\Core\Acceptance\acceptance_runner.py latest
```

正式验收报告会写入当前 Issue 的：

```text
AIWorkflow/Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/
```

## 最终回复要求

只要本轮触发了 AIWorkflow，最终回复必须包含验收结果。

推荐格式：

```text
验收结果：
- validate-current：pass / fail / blocked / 未运行
- validate-resolution：pass / fail / blocked / 未运行
- validate-iteration：pass / fail / blocked / 未运行
- run --dry-run：pass / fail / blocked / 未运行
- run：pass / fail / blocked / 未运行
- Report：<AIWorkflow 相对路径或未生成>
- Result：<AIWorkflow 相对路径或未生成>
- 说明：<未运行或 blocked 原因>
```
