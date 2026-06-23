import json
from pathlib import Path

import path_resolver


def current_json_valid(project_root, params):
    path = params.get("path")
    target = _resolve_path(project_root, path, "Workspace/Current.json")
    display_path = path_resolver.to_aiworkflow_relative(_display_path(project_root, target))
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{display_path} does not exist.",
            "details": {"path": display_path},
        }

    data = json.loads(target.read_text(encoding=params.get("encoding", "utf-8-sig")))
    required = [
        "schemaVersion",
        "topic",
        "topicPath",
        "issue",
        "issuePath",
        "decisionPath",
        "resolutionPath",
        "currentIteration",
        "iterationPath",
        "updatedAt",
        "source",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        return {
            "status": "fail",
            "message": f"{display_path} missing fields: {', '.join(missing)}.",
            "details": {"missing": missing},
        }
    aiworkflow_root = _aiworkflow_root()
    for key in ["topicPath", "issuePath", "decisionPath", "resolutionPath", "iterationPath"]:
        ref = path_resolver.resolve_aiworkflow_path(aiworkflow_root, data[key])
        if not ref.exists():
            return {
                "status": "fail",
                "message": f"{display_path} references missing {key}: {data[key]}.",
                "details": {"key": key, "path": data[key]},
            }
    return {
        "status": "pass",
        "message": f"{display_path} is valid.",
        "details": {"path": display_path},
    }


def aitdd_policy_valid(project_root, params):
    path = params.get("path")
    target = _resolve_path(project_root, path, "Workspace/AITDDPolicy.json")
    display_path = path_resolver.to_aiworkflow_relative(_display_path(project_root, target))
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{display_path} does not exist.",
            "details": {"path": display_path},
        }

    data = json.loads(target.read_text(encoding=params.get("encoding", "utf-8-sig")))
    required = [
        "schemaVersion",
        "defaultMode",
        "formalRunPolicy",
        "templateWorkspacePolicy",
        "userOverridePhrases",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        return {
            "status": "fail",
            "message": f"{display_path} missing fields: {', '.join(missing)}.",
            "details": {"missing": missing},
        }

    failures = []
    if data.get("defaultMode") not in {"enabled", "manual", "off"}:
        failures.append("defaultMode must be enabled, manual, or off")
    if data.get("formalRunPolicy") not in {"explicit", "auto"}:
        failures.append("formalRunPolicy must be explicit or auto")
    if data.get("templateWorkspacePolicy") != "smoke-only":
        failures.append("templateWorkspacePolicy must be smoke-only")
    overrides = data.get("userOverridePhrases")
    if not isinstance(overrides, dict):
        failures.append("userOverridePhrases must be an object")
    else:
        for key in ["disable", "formalRun"]:
            value = overrides.get(key)
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                failures.append(f"userOverridePhrases.{key} must be a non-empty string list")

    if failures:
        return {
            "status": "fail",
            "message": f"{display_path} is invalid: {'; '.join(failures)}.",
            "details": {"failures": failures},
        }
    return {
        "status": "pass",
        "message": f"{display_path} is valid.",
        "details": {
            "path": display_path,
            "defaultMode": data.get("defaultMode"),
            "formalRunPolicy": data.get("formalRunPolicy"),
        },
    }


def _resolve_path(project_root, path, default_relative_to_aiworkflow):
    if path:
        target = Path(path)
        return target if target.is_absolute() else path_resolver.resolve_project_path(project_root, target)
    return _aiworkflow_root() / default_relative_to_aiworkflow


def _aiworkflow_root():
    return Path(__file__).resolve().parents[4]


def _display_path(project_root, target):
    try:
        return target.relative_to(project_root).as_posix()
    except ValueError:
        return target.as_posix()
