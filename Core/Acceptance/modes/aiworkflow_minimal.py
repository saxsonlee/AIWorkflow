MODE = {
    "id": "aiworkflow_minimal",
    "name": "AIWorkflow 最小自检",
    "checks": [
        {
            "id": "aiworkflow.context.current_json_valid",
            "name": "Current.json 有效",
            "severity": "required",
            "params": {},
        },
        {
            "id": "aiworkflow.context.aitdd_policy_valid",
            "name": "AITDDPolicy.json 有效",
            "severity": "required",
            "params": {},
        },
        {
            "id": "common.json.field_matches",
            "name": "Resolution 指向当前 Issue",
            "severity": "required",
            "params": {
                "path": "${resolution.path}",
                "field": "issue",
                "pattern": "^${issue}$",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Iteration 详情存在",
            "severity": "required",
            "params": {"path": "${iteration.path}"},
        },
    ],
}
