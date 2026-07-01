# Workspace Template

`Workspace.Template/` 是 AIWorkflow 的最小可运行工作区模板。

## 使用方式

1. 将 `Workspace.Template/` 复制为 `Workspace/`。
2. 按项目实际情况修改 `Workspace/Current.json`。
3. 按团队习惯修改 `Workspace/AITDDPolicy.json`。
4. 修改或替换 `Workspace/Topics/ExampleTopic/Issues/ExampleIssue/` 下的示例 Issue。
5. 运行：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-current
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-resolution
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py validate-iteration
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy show
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --dry-run
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py run --template-smoke
```

`run --dry-run` 用于预览当前 Iteration 解析出的验收配置、证据要求和 checks，不生成 `Runs/` 目录，不更新 `LatestRun.md`，也不形成正式 pass/fail 记录。

## 默认示例

模板内置 `ExampleTopic / ExampleIssue / v0.1.0`，在 `acceptance.modes` 中使用 Core 内置的 `aiworkflow_minimal` mode。

这个 mode 只检查 AIWorkflow 自身的最小结构，不依赖宿主项目文件、Adapter、外部命令或私有路径。

## AITDD 开关

`AITDDPolicy.json` 是当前项目的 AITDD 策略开关。AI 应读取这个文件，而不是自行判断是否启用 AITDD。

- `defaultMode: "enabled"`：默认启用 AITDD，用户不需要每次显式说明。
- `defaultMode: "manual"`：只有用户明确要求时才使用 AITDD。
- `defaultMode: "off"`：默认不使用 AITDD，除非用户临时要求。
- `formalRunPolicy: "explicit"`：正式 `run` 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。否则只运行 `validate-*` 和 `run --dry-run`。
- `formalRunPolicy: "auto"`：允许 AI 在项目规则、当前 Iteration 和验收配置都明确时自动发起正式 `run`。模板工作区仍只能运行安装烟测。

可以用 runner 查看或切换：

```powershell
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy show
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode enabled
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode manual
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --default-mode off
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy explicit
python <AIWorkflow路径>\Core\Acceptance\acceptance_runner.py policy set --formal-run-policy auto
```

## 目录说明

`Topics/` 保存 Topic / Issue / Resolution / Iteration / Run。

`Temp/` 保存临时交换产物，不应作为长期事实来源。

`Local/` 保存本地机器配置，不应记录密钥、账号或不可公开路径。

`ProjectContext.md` 用于记录宿主项目上下文。

`AITDDPolicy.json` 用于记录是否默认启用 AITDD、正式 run 是否需要显式确认、模板工作区是否只能用于 smoke。

`LatestRun.md` 会在正式 run 后被 runner 更新为最近一次验收入口。
