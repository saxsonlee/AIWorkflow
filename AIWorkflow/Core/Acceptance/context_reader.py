from pathlib import Path


def project_context_exists(project_root):
    return Path(project_root, "ProjectHelp/AIWorkflow/Workspace/ProjectContext.md").exists()


def read_project_context(project_root):
    path = Path(project_root, "ProjectHelp/AIWorkflow/Workspace/ProjectContext.md")
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
