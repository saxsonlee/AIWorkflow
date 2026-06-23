# AIWorkflow Data Model

## 本文职责

本文说明 AIWorkflow 的核心数据模型和关键文件。它回答“Topic / Issue / Resolution / Iteration / Run 分别是什么”。

## 权限边界

本文只定义数据结构和文件职责，不定义 runner 命令细节、不定义路径解析算法、不定义 check / driver / mode 的职责。

## 核心模型

AIWorkflow 的核心模型为：

```text
Topic -> Issue -> Resolution -> Iteration -> Run
```

`Topic` 是长期主题域。

`Issue` 是具体问题边界，包含 `Issue.md` 和 `Decision.md`。

`Resolution` 是该 Issue 的线性解决进程，索引文件为 `Resolution/Resolution.json`。

`Iteration` 是 Resolution 中的一次推进，详情文件放在 `Resolution/Iterations/`。

`Run` 是一次验收执行记录，目录放在 `Resolution/Runs/YYYY_MM_DD/rNNN/`。

## Current.json

`Workspace/Current.json` 保存当前执行指针，不作为新请求归属证明。

最小字段：

```json
{
  "schemaVersion": "1.0",
  "topic": "",
  "topicPath": "Workspace/Topics/<Topic>",
  "issue": "",
  "issuePath": "Workspace/Topics/<Topic>/Issues/<Issue>/Issue.md",
  "decisionPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Decision.md",
  "resolutionPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Resolution.json",
  "currentIteration": "v0.1.0",
  "iterationPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Iterations/v0.1.0.md",
  "updatedAt": "",
  "source": "AI_CONTEXT"
}
```

新请求需要按问题本体、修改对象和影响范围重新判断归属，不能只因为 `Workspace/Current.json` 指向某个 Issue 就直接归入该 Issue。

## Resolution.json

`Resolution/Resolution.json` 是 Issue 的线性进程索引。

`iterations[]` 中的每一项至少包含：

```json
{
  "version": "v0.1.0",
  "createdAt": "",
  "type": "maintenance",
  "summary": "",
  "status": "pending",
  "detailPath": "Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Iterations/v0.1.0.md",
  "acceptance": {
    "modes": [
      "aiworkflow_minimal",
      "temp.current_iteration"
    ],
    "requiredEvidence": [
      "contract"
    ],
    "extraChecks": [],
    "extraPostChecks": []
  }
}
```

`acceptance` 是 `run` 的执行入口。没有 `acceptance` 时，`validate-iteration` 可以通过，但 `run` 会返回 `blocked`。

`acceptance.modes` 指向本次验收使用的一组配方。Runner 按数组顺序合并这些 mode 的 checks 和 postChecks。

`acceptance.requiredEvidence` 声明正式 `run` 必须覆盖的证据类型。允许值为 `contract`、`behavior`、`browser`。如果省略，runner 按 `["contract"]` 处理。

当一次 Iteration 同时需要静态契约和行为产物证明时，可以声明：

```json
{
  "acceptance": {
    "modes": [
      "example_contract_mode",
      "temp.current_iteration_behavior"
    ],
    "requiredEvidence": [
      "contract",
      "behavior"
    ],
    "extraChecks": [
      {
        "id": "common.json.field_matches",
        "name": "driver 产物状态匹配",
        "severity": "required",
        "acceptanceType": "behavior",
        "params": {
          "path": "Workspace/Temp/BehaviorResult.json",
          "field": "status",
          "pattern": "^pass$",
          "driver": "Adapters/drivers/run_behavior.py"
        }
      }
    ],
    "extraPostChecks": []
  }
}
```

这个示例只展示数据结构：`requiredEvidence` 声明需要 `behavior` 证据，读取 driver 产物的 check 通过 `acceptanceType` 和 `params.driver` 表示该事实来自 driver。driver 的职责和 check 的拆分规则见 `Core/docs/check-driver-mode.md`。

长期、可复用、会反复出现的验收能力必须进入非 `temp` mode；当前 Iteration 的一次性检查集合应进入 `temp.*` mode。mode 文件本身不引用其他 mode，组合关系只写在 `Resolution.json` 的 `acceptance.modes`。

`acceptance.mode` 是旧结构，不再支持。

`acceptance.extraChecks` 只保存当前 Iteration 的临时补充事实，例如本轮新增文件、迁移记录或一次性审计点。如果某个检查已经成为发布门禁、项目惯例或技术栈惯例，应迁移到 mode。

## Run 产物

正式执行 `run` 后，runner 会生成：

```text
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/Result.json
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/AcceptanceReport.md
Workspace/Topics/<Topic>/Issues/<Issue>/Resolution/Runs/YYYY_MM_DD/rNNN/Run.log
```

`Workspace/LatestRun.md` 会指向最近一次 Run。

Run 完成后，runner 会把当前 Iteration 详情中的状态、结果、Run、Report 和 Result 入口同步回写。

## 状态

Iteration 和 Run 使用同一套状态：

```text
pending
pass
fail
blocked
```

`pass` 表示本次声明的验收目标通过。

`fail` 表示 required 检查失败。

`blocked` 表示验收条件不足或环境不可执行。
