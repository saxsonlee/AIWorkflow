MODE = {
    "id": "temp.aiworkflow_goal_driven_acceptance_design",
    "name": "AIWorkflow 目标驱动验收设计自检",
    "checks": [
        {
            "id": "common.content.contains",
            "name": "README 包含目标驱动验收规则",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "## 目标驱动验收设计规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录最终目标反推验收",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "AITDD 的验收标准必须从当前需要达成的最终目标反推",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录标准流程",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "当前需要达成的目标 -> 拆分最终验收点 -> 必要时拆分多个 Run -> 验收每个 Run 的目标 -> 最终整体验收是否达成目标",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录不能检查已做动作",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "验收项必须检查目标达成事实，而不是检查 AI 已经做过的动作。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录文档目录不能替代功能验收",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "文档更新、目录存在、指针切换只能证明设计或记录已更新，不能替代功能能力验收。",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿包含目标驱动验收章节",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "## 目标驱动验收",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Issue 记录机制边界",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/GoalDrivenAcceptanceDesign/Issue.md",
                "text": "文档更新类验收不能替代功能能力验收",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Iteration 记录后续配置系统重验收",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/GoalDrivenAcceptanceDesign/Resolution/Iterations/v0.1.0.md",
                "text": "LuaConfigSystem 后续应按该规则重新拆分 xlsx 到 table 的功能验收",
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
