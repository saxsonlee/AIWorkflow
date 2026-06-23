MODE = {
    "id": "temp.ai_workflow_topic_resolution_design",
    "name": "AIWorkflow Topic / Issue / Resolution 策划案验收",
    "checks": [
        {
            "id": "common.content.contains",
            "name": "设计稿记录新层级模型",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "Topic / Issue / Resolution / Iteration / Run",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 Resolution.json 最小结构",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "\"currentIteration\": \"\"",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 Iteration 详情短结构",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "## 本次处理",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 r001 Run 目录规则",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "Resolution/Runs/YYYY_MM_DD/r001/",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 Issue 级 Decision",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "Decision.md 移动到 Issue 下",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录不需要 LatestIteration",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "不需要 `LatestIteration.md`",
            },
        },
        {
            "id": "common.content.contains",
            "name": "实现计划记录新模型",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AITDDImplementationPlan.md",
                "text": "Topic / Issue / Resolution / Iteration / Run",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录新模型",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "Topic / Issue / Resolution / Iteration / Run",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录硬切迁移策略",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "旧的 `Issue / Goal / Run` 模型仍存在于当前实现中，但新结构迁移采用硬切策略。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录硬切新结构策略",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "旧目录不需要为了兼容 runner 保留，但可以作为普通历史文件暂时留在磁盘上。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录不保留 validate-goal",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "不保留 `validate-goal` 兼容命令。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "实现计划记录硬切策略",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AITDDImplementationPlan.md",
                "text": "新结构迁移采用硬切策略，不做旧 `Issue / Goal / Run` 兼容。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录旧目录只作历史",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "旧目录可以作为普通历史文件暂时留在磁盘上，但不再参与新 AIWorkflow 的读取、写入和判断。",
            },
        },
    ],
}
