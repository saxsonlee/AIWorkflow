# AIWorkflow Core

## 定位

AIWorkflow 是一套可迁移的 AI-TDD 验收工作流。它把一次工作组织为 `Topic / Issue / Resolution / Iteration / Run`，并通过可运行检查生成机器结果、验收报告和执行日志。

`Core/` 是 AIWorkflow 的通用核心，只保存工作流机制、通用检查、报告生成、路径解析和基础运行能力。项目、引擎、平台、业务目录和本地环境差异应放在 `Adapters/`、`Modes/` 或宿主项目自己的规则中。

## 入口职责

本文只作为 Core 入口页，负责说明最小结构、必读规则和文档索引。

详细规则拆分到 `Core/docs/`。拆分后的文档仍然保持各自职能和权限：规则只在对应文档中定义，入口页只做导航，不覆盖或改写规则。

## 最小结构

```text
AIWorkflow/
  README.md
  Core/
    README.md
    docs/
    Acceptance/
  Workspace.Template/
  Skill.Template/
  Workspace/        # 由 Workspace.Template/ 创建，不随源码工作区默认携带
  Adapters/         # 可选，宿主项目需要专用 check / driver 时创建
  Modes/            # 可选，宿主项目需要 Core 外验收配方时创建
```

`Core/Acceptance` 保存 runner、registry、通用 checks、Core 内置 modes、报告生成和路径解析。

`Workspace/` 保存当前工作区事实，包括 `Workspace/Current.json`、`Workspace/AITDDPolicy.json`、`Topic / Issue / Resolution / Iteration / Run`、`Workspace/LatestRun.md`、临时交换产物和本地缓存。

`Workspace.Template/` 用于在新项目中初始化 `Workspace/`。源码仓库只保留模板；接入项目时由使用者创建自己的 `Workspace/`。

`Skill.Template/` 用于安装 Codex skill，让目标项目中的 AI 知道什么时候进入 AIWorkflow。

`Adapters/` 只保存项目或技术栈适配能力，包括 checks、drivers 和注册入口。

`Modes/` 保存 Core 之外的验收配方。`Modes/Common/` 保存跨项目可复用配方，`Modes/<ProjectOrStack>/` 保存项目或技术栈相关配方。

## 必读文档

按任务读取对应文档：

- 架构与目录职责：`Core/docs/architecture.md`
- AIWorkflow 相对路径：`Core/docs/path-rules.md`
- Topic / Issue / Resolution / Iteration / Run 数据模型：`Core/docs/data-model.md`
- runner 命令、状态和 Run 产物：`Core/docs/runner.md`
- Check / Driver / Mode 职责和权限边界：`Core/docs/check-driver-mode.md`
- Core / Adapters / Modes 扩展边界：`Core/docs/extension-boundary.md`
- 新项目初始化和迁移检查：`Core/docs/setup.md`

## 使用方式

普通使用不需要记 runner 命令。接入项目复制出 `Workspace/` 并安装触发规则后，直接向 AI 描述任务即可；AI 会按 `Workspace/AITDDPolicy.json` 判断是否进入 AIWorkflow，并在对话中展示验收结果。

Runner 命令主要用于手动排查、CI 或维护脚本，详见 `Core/docs/runner.md`。

## 核心约束

- AIWorkflow 内部路径统一使用 AIWorkflow 相对路径。
- `Workspace/Current.json` 只是当前执行指针，不作为新请求归属证明。
- `Workspace/AITDDPolicy.json` 是项目级 AITDD 开关；AI 必须读取它，不应自行判断是否启用。
- 没有 `acceptance` 的 Iteration 可以通过结构验证，但正式 `run` 会返回 `blocked`。
- Check 只能验证一种事实。
- Driver 负责流程执行和环境适配，不直接代表最终验收结论。
- Mode 是验收配方，只组合多个原子 check，不直接执行跨环境准备、服务启动、登录、数据注入或连续请求。
- `Resolution.json` 使用 `acceptance.modes` 组合多个 mode；mode 文件本身不引用其他 mode。
- 长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode；当前 Iteration 的一次性检查集合应进入 `temp.*` mode。
- Core 只能描述通用流程、通用路径规则、通用验收状态和可迁移能力域。

## 最小自检

Core 内置的 `aiworkflow_minimal` 是最小自检 mode，只检查 `Workspace/Current.json`、`Resolution.json` 和当前 Iteration 文件，不依赖宿主项目、Adapter、外部命令或私有路径。
