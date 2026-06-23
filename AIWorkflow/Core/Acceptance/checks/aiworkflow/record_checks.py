from pathlib import Path


def goal_version_added(project_root, params):
    path = params.get("path")
    version = params.get("version")
    target = Path(project_root, path)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }
    content = target.read_text(encoding=params.get("encoding", "utf-8"))
    if version in content:
        return {
            "status": "pass",
            "message": f"{path} contains version {version}.",
            "details": {"path": path, "version": version},
        }
    return {
        "status": "fail",
        "message": f"{path} does not contain version {version}.",
        "details": {"path": path, "version": version},
    }
