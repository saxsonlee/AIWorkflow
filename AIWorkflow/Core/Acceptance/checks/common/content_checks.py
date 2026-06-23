import re

import path_resolver


def contains(project_root, params):
    path = params.get("path")
    text = params.get("text", "")
    target = path_resolver.resolve_project_path(project_root, path)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }
    content = target.read_text(encoding=params.get("encoding", "utf-8"))
    if text in content:
        return {
            "status": "pass",
            "message": f"{path} contains expected text.",
            "details": {"path": path, "text": text},
        }
    return {
        "status": "fail",
        "message": f"{path} does not contain expected text.",
        "details": {"path": path, "text": text},
    }


def not_contains(project_root, params):
    path = params.get("path")
    text = params.get("text", "")
    target = path_resolver.resolve_project_path(project_root, path)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }
    content = target.read_text(encoding=params.get("encoding", "utf-8"))
    if text not in content:
        return {
            "status": "pass",
            "message": f"{path} does not contain forbidden text.",
            "details": {"path": path, "text": text},
        }
    return {
        "status": "fail",
        "message": f"{path} contains forbidden text.",
        "details": {"path": path, "text": text},
    }


def matches_regex(project_root, params):
    path = params.get("path")
    pattern = params.get("pattern", "")
    target = path_resolver.resolve_project_path(project_root, path)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }
    content = target.read_text(encoding=params.get("encoding", "utf-8"))
    if re.search(pattern, content, re.MULTILINE):
        return {
            "status": "pass",
            "message": f"{path} matches expected pattern.",
            "details": {"path": path, "pattern": pattern},
        }
    return {
        "status": "fail",
        "message": f"{path} does not match expected pattern.",
        "details": {"path": path, "pattern": pattern},
    }
