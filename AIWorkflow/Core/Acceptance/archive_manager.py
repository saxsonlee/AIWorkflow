from pathlib import Path


def list_issues(project_root):
    issues_root = Path(project_root, "ProjectHelp/AIWorkflow/Workspace/Topics")
    if not issues_root.exists():
        return []
    return sorted(path.name for path in issues_root.iterdir() if path.is_dir())
