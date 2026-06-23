MODE = {
    "id": "temp.aiworkflow_portable_core_split_iteration",
    "name": "AIWorkflow Portable Core Split 当前 Iteration 临时验收",
    "checks": [
        {
            "id": "python.py_compile_passed",
            "name": "当前 Iteration 临时 mode 可编译",
            "severity": "required",
            "params": {
                "paths": [
                    "Core/Acceptance/modes/temp/aiworkflow_portable_core_split_iteration.py",
                ]
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 modes 组合入口",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_resolution_acceptance_uses_modes_list",
            },
        },
        {
            "id": "common.file.exists",
            "name": "当前 Iteration 临时 mode 存在",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/modes/temp/aiworkflow_portable_core_split_iteration.py",
            },
        },
        {
            "id": "common.content.contains",
            "name": "当前 Iteration 记录 modes 组合迁移",
            "severity": "required",
            "params": {
                "path": "Workspace/Topics/AITDDWorkflow/Issues/AIWorkflowPortableCoreSplit/Resolution/Iterations/v0.1.0.md",
                "text": "`acceptance.mode` 迁移为 `acceptance.modes`",
            },
        },
    ],
}
