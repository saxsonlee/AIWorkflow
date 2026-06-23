MODE = {
    "id": "ai_workflow_design",
    "name": "AI-TDD 工作流设计验收",
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
}
