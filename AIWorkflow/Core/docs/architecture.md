# AIWorkflow Core Architecture

## 本文职责

本文说明 AIWorkflow 的目录结构和各目录职责。它回答“AIWorkflow 由哪些部分组成，每个部分负责什么”。

## 权限边界

本文只定义架构职责，不定义 runner 命令细节、不定义数据模型字段、不定义 check / driver / mode 的原子性规则。

## 总体结构

```text
AIWorkflow/
  README.md
  Core/
  Workspace/
  Workspace.Template/
  Skill.Template/
  Adapters/
  Modes/
```

`Core/` 保存可迁移核心。

`Workspace/` 保存当前工作区事实，包括当前指针、项目上下文、Topic / Issue / Resolution / Iteration / Run、最近一次验收入口、临时交换产物和本地缓存。

`Workspace.Template/` 是空工作区模板，用于在新项目中初始化 `Workspace/`。

`Skill.Template/` 是 Codex skill 安装模板，用于让新项目中的 AI 能识别什么时候进入 AIWorkflow。

`Adapters/` 保存项目或技术栈适配能力，只包含项目专用 checks、drivers 和注册入口。

`Modes/` 保存 Core 之外的验收配方。Mode 负责组合 checks，不直接承载执行器实现。

`Modes/Common/` 保存跨项目可复用、但尚未固定为 Core 内置能力的配方。

`Modes/<ProjectOrStack>/` 保存项目或技术栈相关配方。

## Core 目录结构

```text
Core/
  README.md
  OPEN_SOURCE.md
  docs/
    architecture.md
    path-rules.md
    data-model.md
    runner.md
    check-driver-mode.md
    extension-boundary.md
    setup.md
  Acceptance/
    acceptance_runner.py
    acceptance_registry.py
    archive_manager.py
    context_reader.py
    path_resolver.py
    report_writer.py
    checks/
      aiworkflow/
      common/
      dotnet/
      python/
    modes/
      temp/
    tests/
```

`Core/Acceptance` 保存 AIWorkflow 最小可运行能力。

`Core/Acceptance/checks` 保存可迁移的通用 check。

`Core/Acceptance/modes` 保存 Core 内置 mode。Core 内置 mode 不应依赖宿主项目、私有路径或本地环境。

`Core/docs` 保存 Core 规范文档。入口页只做导航，具体规则由对应文档承载。

## Workspace 结构

```text
Workspace/
  Current.json
  LatestRun.md
  ProjectContext.md
  Local/
  Temp/
  Topics/
    <Topic>/
      Issues/
        <Issue>/
          Issue.md
          Decision.md
          Resolution/
            Resolution.json
            Iterations/
            Runs/
```

`Workspace/Temp` 保存临时交换产物。

`Workspace/Local` 保存本地缓存或不可开源状态。

`Workspace/Topics` 保存真实工作流记录。

## 扩展目录

```text
Adapters/
  acceptance_registry.py
  checks/
  drivers/
Modes/
  Common/
  <ModeGroupName>/
```

`Adapters/` 不包含 mode。项目或技术栈 mode 必须放到 `Modes/`。

`Modes/` 不保存 driver。需要流程执行时由 mode 组合读取 driver 产物的 check。
