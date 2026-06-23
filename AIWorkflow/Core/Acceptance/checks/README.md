# Core Checks README

## 定位

`Core/Acceptance/checks` 只保存 AIWorkflow Core 可迁移的检查能力。

Core checks 不应绑定某个宿主项目、业务目录、编辑器、引擎、平台或私有流水线。项目或技术栈专用检查应放在 `Adapters/checks/`，并由 `Adapters/acceptance_registry.py` 注册。

## 路径规则

Core check 的输入路径遵守 AIWorkflow 路径规则：

- `Core/...`、`Workspace/...`、`Adapters/...`、`Modes/...` 按 AIWorkflow 根解析。
- 其他路径按宿主项目相对路径解析。
- 不在 check 代码中写死宿主项目路径。

## 当前 Core Check 分类

### common

`common.*` 只处理跨项目基础事实：

- 文件或目录存在性。
- 文本包含、排除和正则匹配。
- JSON 字段匹配。
- 命名规则。
- 变更边界。

### aiworkflow

`aiworkflow.*` 只检查 AIWorkflow 自身结构，例如 `Workspace/Current.json` 的字段和引用是否有效。

### python

`python.*` 提供 Python 能力域检查，例如 `py_compile`。

### dotnet

`dotnet.*` 提供通用命令能力域检查。它只知道如何运行传入的项目路径，不理解具体业务。

## Adapter Check

Adapter check 不写入 Core 注册表。

每个 Adapter 可以提供：

```text
Adapters/acceptance_registry.py
Adapters/checks/
```

Core registry 会在运行时合并 Adapter 注册表，因此 `list-checks` 可以同时显示 Core checks 和当前项目 Adapter checks。

## 新增 Check 规则

新增 Core check 前先判断：

- 是否可跨项目复用。
- 是否只依赖传入参数和通用文件结构。
- 是否不理解当前项目业务含义。

如果答案是否，应放到 Adapter。

新增 Adapter check 时，应同步更新 `Adapters/acceptance_registry.py`，并通过 mode 或 `extraChecks` 纳入 Run。

## Check 原子性规则

Check 是可复用的事实验证单元。一个 check 只能验证一种事实。

不得把契约检查、环境准备和行为验收塞进同一个 check。

不得在一个 check 内同时完成以下多类职责：

- 检查静态契约。
- 创建数据库或写入测试数据。
- 启动服务或外部进程。
- 登录或获取 token。
- 连续发送多个请求。
- 同时验证成功路径和失败路径。

跨环境准备、服务启动、登录、数据注入、连续请求等流程必须放入 driver。

Driver 可以负责准备环境、执行复杂流程并输出机器可读结果；check 只验证一个明确结果，例如：

- 某个文件存在。
- 某个字段存在。
- 某个接口返回指定状态码。
- 某个响应字段符合预期。
- 某个 driver 输出的单一结果为 pass。

Mode 负责组合多个原子 check。需要证明多个事实时，新增多个 check 并在 mode 或 `extraChecks` 中组合。

如果一个 check 的失败无法直接判断是哪一种事实失败，这个 check 就太胖，应拆分。

## Driver 职责规则

Driver 是流程执行和环境适配单元。跨环境准备、服务启动、登录、数据注入、连续请求等流程必须放入 driver。

Driver 可以准备环境、执行复杂流程并输出机器可读结果，例如 JSON、日志、状态文件或 Run 产物。

Driver 不直接代表最终验收结论。Driver 只产出事实材料，check 读取 driver 产物后验证一个明确事实。

如果一个 driver 产出多个事实，应由多个 check 分别读取这些字段或产物；不要把多个验收目标压成一个 driver 布尔结果。

## 证据覆盖规则

Iteration 可以通过 `acceptance.requiredEvidence` 声明本次验收必须覆盖的证据类型。

Core 只识别通用证据类型：

- `contract`：静态结构、接口契约、文件、文本、JSON 字段、命名、编译或解析等事实。
- `behavior`：由 driver 执行非原子流程后产出的机器事实。
- `browser`：由浏览器、UI 或端到端交互 driver 产出的机器事实。

正式 `run` 必须验证 `requiredEvidence` 中每一种证据类型都有至少一个对应 check。`behavior` 和 `browser` 类型的 check 必须引用 driver、driver 产物或显式 driver evidence；不能只用静态 contract check 代替。

## Mode 职责规则

Mode 是验收配方，负责组合多个原子 check，并声明这些 check 的参数、名称和 required / optional 严重级别。

Mode 负责组合多个原子 check。需要证明多个事实时，新增多个 check 并在 mode 或 `extraChecks` 中组合。

Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求。这类流程必须放入 driver，mode 只引用读取 driver 产物的 check。

Mode 不承担 check 的判断逻辑，也不承担 driver 的执行流程；它只回答“本次验收由哪些事实组成”。
