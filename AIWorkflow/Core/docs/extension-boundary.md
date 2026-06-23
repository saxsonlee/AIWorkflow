# AIWorkflow Extension Boundary

## 本文职责

本文定义 Core、Adapters、Modes 和宿主项目规则之间的扩展边界。它回答“什么可以进入 Core，什么必须留在项目侧”。

## 权限边界

本文只定义扩展归属，不定义具体 check 内容、不定义 driver 执行细节、不定义 runner 命令。

## 技术中立规则

Core 只能描述通用流程、通用路径规则、通用验收状态和可迁移能力域。

具体语言、引擎、编辑器、平台、资源系统、生成链路和业务目录应放入 Adapter、项目协作规则或当前 Issue 的验收上下文。

项目细节必须进入 `Adapters/`、`Modes/` 或宿主项目规则，不能写入 Core 文档、Core checks、Core modes 或 Core runner。

如果某个项目需要专用执行器或专用 checks，应通过 `Adapters/` 接入，而不是把项目要求写入 Core 门禁。

## Core 权限

Core 可以包含：

- runner 和报告生成。
- 路径解析和上下文读取。
- 通用文件、文本、JSON、命名、边界检查。
- 可迁移能力域检查。
- 不依赖宿主项目的最小 mode。
- AIWorkflow 自身结构测试。

Core 不应包含：

- 具体项目业务词。
- 具体宿主项目路径。
- 项目私有构建链路。
- 一次性业务验收流程。
- 本地机器环境假设。

## Adapter 权限

Adapters/ 只保存项目或技术栈适配能力：

```text
Adapters/
  acceptance_registry.py
  checks/
  drivers/
```

Adapter 可以包含：

- 项目专用 checks。
- 技术栈专用 checks。
- 项目或技术栈 driver。
- Adapter check 注册入口。

Adapter 不应包含 mode。需要组合多个 checks 时，应放入 `Modes/`。

## Mode 权限

Modes 保存 Core 之外的验收配方：

```text
Modes/Common/
Modes/<ProjectOrStack>/
```

`Modes/Common/` 保存跨项目可复用、但尚未固定为 Core 内置能力的配方。

`Modes/<ProjectOrStack>/` 保存项目或技术栈相关配方。

Mode 不应包含环境准备、服务启动、登录、数据注入或连续请求流程。这些流程必须放入 driver。

## 宿主项目规则

宿主项目规则用于记录项目专属约束，例如语言、引擎、目录、构建链路、平台、生成物归属和本地协作约定。

这些内容不应写入 Core 文档，除非它们已经抽象为可迁移能力域。
