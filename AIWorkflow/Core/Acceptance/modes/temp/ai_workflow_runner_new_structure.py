MODE = {
    "id": "temp.ai_workflow_runner_new_structure",
    "name": "AIWorkflow 新 runner 结构验收",
    "checks": [
        {
            "id": "aiworkflow.context.current_json_valid",
            "name": "Current.json 使用新结构",
            "severity": "required",
            "params": {},
        },
        {
            "id": "common.file.exists",
            "name": "新 Issue.md 存在",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/ControlIssueGoalVisibility/Issue.md",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Issue 级 Decision.md 存在",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/ControlIssueGoalVisibility/Decision.md",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Resolution.json 存在",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/ControlIssueGoalVisibility/Resolution/Resolution.json",
            },
        },
        {
            "id": "common.file.exists",
            "name": "当前 Iteration 详情存在",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Workspace/Topics/AITDDWorkflow/Issues/ControlIssueGoalVisibility/Resolution/Iterations/v0.2.0.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "runner 不包含 validate-goal 命令",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Acceptance/acceptance_runner.py",
                "text": "validate-resolution",
            },
        },
        {
            "id": "common.content.not_contains",
            "name": "runner 移除 validate-goal",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Acceptance/acceptance_runner.py",
                "text": "validate-goal",
            },
        },
        {
            "id": "common.content.contains",
            "name": "runner 支持 validate-iteration",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Acceptance/acceptance_runner.py",
                "text": "validate-iteration",
            },
        },
        {
            "id": "common.content.contains",
            "name": "runner 使用 rNNN 目录",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Acceptance/acceptance_runner.py",
                "text": "return date_dir / f\"r{max_index + 1:03d}\"",
            },
        },
        {
            "id": "common.content.contains",
            "name": "report writer 输出 Topic",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/Acceptance/report_writer.py",
                "text": "Topic：{result['topic']}",
            },
        },
        {
            "id": "common.content.contains",
            "name": "README 记录 run 参数",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/AIWorkflow/README.md",
                "text": "run [--mode <mode_name>] [--dry-run]",
            },
        },
        {
            "id": "common.content.contains",
            "name": "设计稿记录 acceptance 可选",
            "severity": "required",
            "params": {
                "path": "ProjectHelp/Workflow/AIVerificationWorkflow.md",
                "text": "`acceptance` 放在 `Resolution.json.iterations[]` 单项中，并作为可选字段。",
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
