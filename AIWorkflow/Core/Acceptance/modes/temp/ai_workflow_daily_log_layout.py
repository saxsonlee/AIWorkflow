MODE = {
    "id": "temp.ai_workflow_daily_log_layout",
    "name": "AIWorkflow 日期日志目录临时验收",
    "checks": [
        {
            "id": "common.file.exists",
            "name": "AI-TDD 设计稿存在",
            "severity": "required",
            "params": {"path": "ProjectHelp/Workflow/AIVerificationWorkflow.md"},
        },
        {
            "id": "common.file.exists",
            "name": "AI-TDD 实现拆分计划存在",
            "severity": "required",
            "params": {"path": "ProjectHelp/Workflow/AITDDImplementationPlan.md"},
        },
        {
            "id": "aiworkflow.context.current_json_valid",
            "name": "Current.json 有效",
            "severity": "required",
            "params": {},
        },
        {
            "id": "common.file.exists",
            "name": "Resolution.json 存在",
            "severity": "required",
            "params": {"path": "${resolution.path}"},
        },
        {
            "id": "common.file.exists",
            "name": "Iteration 详情存在",
            "severity": "required",
            "params": {"path": "${iteration.path}"},
        },
    ],
    "postChecks": [
        {
            "id": "common.json.field_matches",
            "name": "Goal runPath 使用日期和版本目录",
            "severity": "required",
            "params": {
                "path": "${goal.path}",
                "field": "versions[version=${goal.currentVersion}].runPath",
                "pattern": "Goal\\.logs/[0-9]{4}_[0-9]{2}_[0-9]{2}/v[0-9]{3}$",
            },
        },
        {
            "id": "common.json.field_matches",
            "name": "Goal resultPath 使用日期和版本目录",
            "severity": "required",
            "params": {
                "path": "${goal.path}",
                "field": "versions[version=${goal.currentVersion}].resultPath",
                "pattern": "Goal\\.logs/[0-9]{4}_[0-9]{2}_[0-9]{2}/v[0-9]{3}/Result\\.json$",
            },
        },
    ],
}
