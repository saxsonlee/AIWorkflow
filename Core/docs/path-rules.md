# AIWorkflow Path Rules

## 本文职责

本文说明 AIWorkflow 内部路径规则。它回答“文档、配置、报告和检查参数中的路径应该怎么写”。

## 权限边界

本文只定义路径写法和解析边界，不定义数据模型字段含义、不定义 runner 命令、不定义 check / driver / mode 的职责。

## 基本规则

AIWorkflow 内部路径统一使用 AIWorkflow 相对路径：

```text
Core/Acceptance/acceptance_runner.py
Workspace/Current.json
Workspace/AITDDPolicy.json
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Resolution.json
Workspace.Template/Current.json
Adapters/checks/
Modes/<ModeGroupName>/temp/<mode_name>.py
Modes/Common/temp/<mode_name>.py
```

禁止在 Core 文档、Core check、Core mode 或通用配置中写死宿主项目路径。

Runner 会以 AIWorkflow 根目录解析 `Core/`、`Workspace/`、`Workspace.Template/`、`Adapters/`、`Modes/` 和 `Skill.Template/`。

只有当验收项明确检查 AIWorkflow 外部文件时，才使用宿主项目相对路径。

## Current 路径

当前工作区入口固定为：

```text
Workspace/Current.json
```

`Workspace/Current.json` 中的路径字段也使用 AIWorkflow 相对路径，例如：

```json
{
  "topicPath": "Workspace/Topics/<Topic>",
  "issuePath": "Workspace/Topics/<Topic>/Issues/<Issue>/Issue.md",
  "decisionPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Decision.md",
  "resolutionPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Resolution.json",
  "iterationPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Iterations/v0.1.0.md"
}
```

## Policy 路径

AITDD 开关固定为：

```text
Workspace/AITDDPolicy.json
```

Skill、runner 和文档都应引用该路径，不应把开关写入聊天提示或宿主项目绝对路径。

## Run 路径

Run 产物放在：

```text
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/
```

`Workspace/LatestRun.md`、`Result.json` 和 `AcceptanceReport.md` 中的文件入口应继续使用 AIWorkflow 相对路径。

## 模板路径

源码中保留 `Workspace.Template/`，用于创建模板工作区。

接入项目后，由使用者创建：

```text
AIWorkflow/Workspace/
```

`Workspace/` 属于宿主项目过程资产，不随开源源码默认携带。可以从 `Workspace.Template/` 复制生成，也可以直接放入已有项目自己的工作区。
