MODE = {
    "id": "temp.aiworkflow_request_ownership_rules",
    "name": "AIWorkflow 请求归属与 Current 边界规则自检",
    "checks": [
        {
            "id": "common.content.contains",
            "name": "README 明确 Current 是执行指针",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "`Current.json` 是执行指针，不是归属证明。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 明确 Current 不回答新请求归属",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "新请求应该归属哪个 Topic / Issue？",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 包含请求归属判断规则",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "## 请求归属判断规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录触发上下文不等于问题本体",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "问题在哪个上下文里暴露，不等于它就属于那个上下文。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录影响范围归属规则",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "影响跨领域流程 / 工具 / 工作方式 -> 对应机制 Topic",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录抽象层级变化非固定词表",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "这些只是抽象层级变化的例子，不是固定触发词表。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录归属判断必须显式记录",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "归属判断必须显式记录",
            },
        },
    ],
    "postChecks": [
        {
            "id": "common.json.field_matches",
            "name": "Resolution latestRunPath 使用 rNNN 目录",
            "severity": "required",
            "params": {
                "path": "${resolution.path}",
                "field": "iterations[version=${iteration}].latestRunPath",
                "pattern": "Resolution/Runs/[0-9]{4}_[0-9]{2}_[0-9]{2}/r[0-9]{3}$",
            },
        },
    ],
}
