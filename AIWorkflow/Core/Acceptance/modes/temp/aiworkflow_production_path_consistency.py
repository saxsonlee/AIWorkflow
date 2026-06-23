MODE = {
    "id": "temp.aiworkflow_production_path_consistency",
    "name": "AIWorkflow 正式路径一致性规则自检",
    "checks": [
        {
            "id": "common.content.contains",
            "name": "README 包含正式路径一致性规则",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "## 正式路径一致性规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求复用正式路径",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "验收必须优先复用这些正式路径",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 禁止测试路径冒充最终通过",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "测试验收器不得添加比正式环境更宽松的搜索路径",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 要求补正式路径一致性 Run",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "必须补一个正式路径一致性 Run",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿包含正式路径一致性章节",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "## 正式路径一致性",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 LuaLoader 示例",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "验收器必须复用运行时 `LuaLoader`",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Iteration 记录正式路径一致性目标",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/GoalDrivenAcceptanceDesign/Resolution/Iterations/v0.1.2.md",
                "text": "正式路径一致性",
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
