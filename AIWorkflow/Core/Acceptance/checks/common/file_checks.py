from pathlib import Path

import path_resolver


def exists(project_root, params):
    path = params.get("path")
    target = _resolve(project_root, path)
    if target.exists():
        return {
            "status": "pass",
            "message": f"{path} exists.",
            "details": {"path": path},
        }
    return {
        "status": "fail",
        "message": f"{path} does not exist.",
        "details": {"path": path},
    }


def not_exists(project_root, params):
    path = params.get("path")
    target = _resolve(project_root, path)
    if not target.exists():
        return {
            "status": "pass",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }
    return {
        "status": "fail",
        "message": f"{path} exists.",
        "details": {"path": path},
    }


def _resolve(project_root, path):
    return path_resolver.resolve_project_path(project_root, path)
