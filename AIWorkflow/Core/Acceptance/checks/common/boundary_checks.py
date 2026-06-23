from pathlib import Path


def only_allowed_files_changed(project_root, params):
    changed = params.get("changed", [])
    allowed = params.get("allowed", [])
    unexpected = []
    for item in changed:
        if not _is_allowed(item, allowed):
            unexpected.append(item)
    if unexpected:
        return {
            "status": "fail",
            "message": f"Unexpected changed files: {', '.join(unexpected)}.",
            "details": {"unexpected": unexpected},
        }
    return {
        "status": "pass",
        "message": "Changed files are within allowed boundaries.",
        "details": {"changed": changed},
    }


def _is_allowed(path, allowed):
    normalized = Path(path).as_posix()
    for pattern in allowed:
        pattern = Path(pattern).as_posix()
        if normalized == pattern or normalized.startswith(pattern.rstrip("/") + "/"):
            return True
    return False
