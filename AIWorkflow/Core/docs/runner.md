# AIWorkflow Runner

## 本文职责

本文说明 `acceptance_runner.py` 的命令、状态和输出。它回答“如何验证 Current / Resolution / Iteration，如何生成 Run 产物”。

## 权限边界

本文只定义 runner 使用方式和执行结果，不定义目录架构、不定义数据模型字段、不定义 check / driver / mode 的职责。

## 命令

从宿主项目根目录执行：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-current
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-resolution
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-iteration
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --dry-run
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --template-smoke
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py latest
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py list-modes
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py list-checks
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy show
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode off
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy explicit
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy auto
```

## 验证命令

`validate-current` 验证 `Workspace/Current.json` 结构和路径。

`validate-resolution` 验证当前 `Resolution.json`。

`validate-iteration` 验证当前 Iteration 详情文件和验收配置结构。

`validate-current` 也会验证 `Workspace/AITDDPolicy.json` 存在且结构有效。

## Run 命令

`run --dry-run` 用于预览当前 Iteration 解析出的验收配置和检查清单，不执行正式验收落盘流程。输出包含 `modes`、`requiredEvidence`、`semanticHints`、`modeSnapshots`、`checks`、`postChecks` 和 `semanticGateFindings`。

`run --dry-run` 不生成 `Runs/` 目录，不写入 `AcceptanceReport.md`、`Result.json` 或 `Run.log`，不更新 `Workspace/LatestRun.md`，不回写 Iteration 状态，也不形成正式 pass/fail 记录。

`run` 生成正式验收记录，并写入当前 Issue 的 Run 目录。

Runner 从当前 Iteration 的 `acceptance.modes` 读取一组 mode，并按数组顺序合并 checks 和 postChecks。

Runner 会读取当前 Iteration 的 `acceptance.requiredEvidence`。正式 `run` 必须为每一种声明的证据类型找到至少一个对应 check；缺失时返回 `blocked`。

Runner 会读取可选的 `acceptance.semanticHints`。如果某个 semantic hint 没有同时出现在 `acceptance.requiredEvidence` 中，正式 `run` 会返回 `blocked`。Core 只识别 `contract`、`behavior`、`browser` 这三类技术中立 hint，不按宿主项目文件名或框架自动推断 UI、浏览器或行为语义。

`latest` 打印 `Workspace/LatestRun.md`。

## Policy 命令

`policy show` 打印 `Workspace/AITDDPolicy.json`。

`policy init` 在缺少策略文件时创建默认策略。

`policy set --default-mode enabled|manual|off` 切换当前项目是否默认启用 AITDD：

- `enabled`：默认启用 AITDD，用户不需要每次显式说明。
- `manual`：只有用户明确要求时才使用 AITDD。
- `off`：默认不使用 AITDD，除非用户临时要求。

`policy set --formal-run-policy explicit|auto` 切换正式 `run` 是否需要显式确认：

- `explicit`：正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。否则只运行 `validate-*` 和 `run --dry-run`。
- `auto`：允许 AI 在项目规则、当前 Iteration 和验收配置都明确时自动发起正式 `run`。仍必须遵守 `templateWorkspacePolicy`，模板工作区只能运行安装烟测。

`policy set --template-workspace-policy smoke-only` 保持模板工作区只能用于安装烟测。

## 模板烟测

`run --template-smoke` 只用于模板安装烟测。

若 `Workspace/Current.json` 的 `source` 是 `TEMPLATE`，普通 `run` 会返回 `blocked`，避免把 `ExampleTopic / ExampleIssue` 的示例 Run 误当成真实任务验收。

模板安装烟测只证明 AIWorkflow 安装可运行，不能替代真实任务验收。

真实任务验收前，必须先创建或切换到正式 `Topic / Issue / Iteration`，并在当前 Iteration 中声明验收条件。

## 输出

正式 `run` 会生成：

```text
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/Result.json
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/AcceptanceReport.md
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/Run.log
```

`Workspace/LatestRun.md` 会记录最近一次 Run 的摘要和入口。

当前 Iteration 详情会回写：

```text
- Status：pass / fail / blocked
- 结果：pass / fail / blocked。
- Run：rNNN。
- Report：`Workspace/.../AcceptanceReport.md`。
- Result：`Workspace/.../Result.json`。
```
