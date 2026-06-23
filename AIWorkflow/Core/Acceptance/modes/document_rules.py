MODE = {
    "id": "document_rules",
    "name": "文档规则验收",
    "checks": [
        {
            "id": "common.file.exists",
            "name": "项目 README 存在",
            "severity": "required",
            "params": {"path": "ProjectHelp/README.md"},
        }
    ],
}
