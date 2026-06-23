MODE = {
    "id": "temp.aiworkflow_check_lifecycle_rules",
    "name": "AIWorkflow Check 生命周期规则验收",
    "checks": [
        {
            "id": "common.content.contains",
            "name": "README 记录 Check 生命周期规则标题",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "## Check 生命周期规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录执行前阶段",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "执行前：",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求判断 check 覆盖目标",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "判断现有 mode / checks / extraChecks 是否足以覆盖本次验收目标。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求主动新增 check",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "如果缺少必要 check，AI 应主动新增或调整 check。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录临时 check 目录",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "ProjectHelp/AIWorkflow/Workspace/Temp/checks/",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录执行后阶段",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "执行后：",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求固定可复用 check",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "如果 check 对后续同类验收仍有价值，应固定到 `ProjectHelp/AIWorkflow/Core/Acceptance/checks/`",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求删除一次性 check",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "如果 check 只服务本次一次性验收，应在 Run 完成并记录结果后删除",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求长期 mode 不引用已删除 check",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "不得让当前长期 mode 继续引用已删除 check。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录固定与临时判断标准",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "固定 check：可被多个 Iteration、多个 Issue 或长期阶段复用。",
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
