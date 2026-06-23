MODE = {
    "id": "optimization_record",
    "name": "优化点记录验收",
    "checks": [
        {
            "id": "common.file.exists",
            "name": "优化点记录文件存在",
            "severity": "required",
            "params": {"path": "ProjectHelp/Optimization/OptimizationPoints.md"},
        }
    ],
}
