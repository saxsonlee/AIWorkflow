# Check / Driver / Mode Rules

## 本文职责

本文定义 Check、Driver、Mode 的职责和权限边界。它回答“一个验收目标应该怎样拆成事实、流程和配方”。

## 权限边界

本文只定义 Check / Driver / Mode 的职责，不定义具体项目契约、不定义 runner 命令、不定义 Workspace 数据字段。

## Check 与 Mode 分类

Core check 分类：

- `common.*`：文件、文本、JSON、命名、边界等基础检查。
- `aiworkflow.*`：AIWorkflow 自身结构检查。
- `python.*`、`dotnet.*` 等能力域检查：可迁移但依赖对应能力域。

Adapter check 分类：

- `project.*`：项目专用事实。
- 技术栈专用能力域：宿主编辑器、平台构建、设备运行等。

Mode 放在：

```text
Core/Acceptance/modes/
Core/Acceptance/modes/temp/
Modes/Common/
Modes/Common/temp/
Modes/<ModeGroupName>/
Modes/<ModeGroupName>/temp/
```

临时 mode 使用 `temp.<mode_name>` 标识。

Core 内置的 `aiworkflow_minimal` 是最小自检 mode，只检查 `Current.json`、`Resolution.json` 和当前 Iteration 文件，不依赖宿主项目、Adapter、外部命令或私有路径。

## Check 原子性规则

Check 是可复用的事实验证单元。一个 check 只能验证一种事实。

允许的 check 形态包括：

- 文件、目录或入口是否存在。
- 文本、JSON 字段、状态码、返回字段或命名规则是否匹配。
- 单个编译、解析、连接、启动或请求结果是否满足预期。
- 单个契约项或同一契约文件中的同类静态事实是否成立。

禁止把契约检查、环境准备和行为验收塞进同一个 check。

以下流程不得直接写进 check：

- 跨环境准备。
- 服务启动。
- 登录。
- 数据注入。
- 临时数据库构造。
- 连续请求。
- 多阶段业务流程。

跨环境准备、服务启动、登录、数据注入、连续请求等流程必须放入 driver。driver 可以执行流程并产出机器结果，check 只读取输入或 driver 产物，验证一个明确事实。

Mode 负责组合多个原子 check。一个目标需要多个事实证明时，应由 mode 或 Iteration 的 `extraChecks` 组合多个 check，而不是扩大单个 check 的职责。

如果一个 check 同时回答“契约是否存在”“环境是否准备好”“行为是否正确”，必须拆分。

## Driver 职责规则

Driver 是流程执行和环境适配单元。Driver 负责把非原子的外部过程执行完，并产出可被 check 读取的机器结果。

允许的 driver 形态包括：

- 准备或清理跨环境依赖。
- 启动、停止或探测服务与外部进程。
- 登录、获取 token 或建立连接。
- 构造临时数据库、写入测试数据或准备测试文件。
- 执行连续请求、多阶段业务流程或外部工具命令。
- 将执行结果写入 JSON、日志、状态文件或 Run 产物。

Driver 不直接代表最终验收结论。Driver 可以报告流程是否执行成功、产出哪些字段、收到哪些状态码和响应内容；最终是否通过，应由 check 读取 driver 产物后验证一个明确事实。

Driver 不应混入 mode 的组合职责，也不应把多个验收目标压成一个布尔结论。一个 driver 产出多个事实时，应拆成多个 check 分别读取。

## 证据覆盖规则

Iteration 的 `acceptance.requiredEvidence` 用于声明本次验收必须覆盖的证据类型。Core 只识别通用证据类型，不推断具体业务语义。

允许的证据类型：

- `contract`：静态结构、接口契约、文件、文本、JSON 字段、命名、编译或解析等事实。
- `behavior`：由 driver 执行非原子流程后产出的机器事实。
- `browser`：由浏览器、UI 或端到端交互 driver 产出的机器事实。

正式 `run` 必须验证 `requiredEvidence` 中每一种证据类型都有至少一个对应 check。`behavior` 和 `browser` 类型的 check 必须引用 driver、driver 产物或显式 driver evidence；不能只用静态 contract check 代替。

Core runner 不根据自然语言关键词判断某个需求是否应该需要 `behavior` 或 `browser`。这个判断应在 Iteration acceptance、mode 或宿主项目规则中完成，并通过 `requiredEvidence` 显式声明。

报告必须区分 `contract`、`behavior` 和 `browser` 验收类型。

## Mode 职责规则

Mode 是验收配方，负责组合多个原子 check，并声明本次验收需要哪些事实共同成立。

允许的 mode 形态包括：

- 选择一组 check。
- 为 check 提供参数、名称和 required / optional 严重级别。
- 组合 Core、Adapters 或项目自定义 check。
- 定义当前验收的静态契约、运行结果、报告产物和后置校验要求。

Mode 负责组合多个原子 check。一个目标需要多个事实证明时，应由 mode 或 Iteration 的 `extraChecks` 组合多个 check，而不是扩大单个 check 的职责。

长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode。当前 Iteration 的一次性检查集合应沉淀为 `temp.*` mode。Iteration 的 `extraChecks` 只保存无法形成 mode 的极少数临时补充事实。

如果某个 `extraChecks` 在多个 Iteration 中反复出现，或已经成为发布门禁、项目惯例、技术栈惯例，应迁移到对应 mode。

Mode 文件本身不引用其他 mode。多个 mode 的组合关系应写在 `Resolution.json` 的 `acceptance.modes` 中。

Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求。这类流程必须放入 driver，mode 只引用读取 driver 产物的 check。

Mode 不应承担 check 的判断逻辑，也不应承担 driver 的执行流程。Mode 只回答“本次验收由哪些事实组成”。
