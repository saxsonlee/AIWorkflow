import json
import re

import path_resolver


def field_matches(project_root, params):
    path = params.get("path")
    field = params.get("field")
    pattern = params.get("pattern")
    target = path_resolver.resolve_project_path(project_root, path)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{path} does not exist.",
            "details": {"path": path},
        }

    data = json.loads(target.read_text(encoding=params.get("encoding", "utf-8-sig")))
    value = _resolve_field(data, field)
    if value is None:
        return {
            "status": "fail",
            "message": f"{path} field {field} does not exist.",
            "details": {"path": path, "field": field},
        }

    text = str(value)
    if re.search(pattern, text):
        return {
            "status": "pass",
            "message": f"{path} field {field} matches expected pattern.",
            "details": {"path": path, "field": field, "value": text},
        }
    return {
        "status": "fail",
        "message": f"{path} field {field} does not match expected pattern.",
        "details": {"path": path, "field": field, "value": text, "pattern": pattern},
    }


def _resolve_field(data, field):
    current = data
    for part in _split_field(field):
        if "[" in part and part.endswith("]"):
            name, selector = part.split("[", 1)
            selector = selector[:-1]
            current = current.get(name) if isinstance(current, dict) else None
            if not isinstance(current, list):
                return None
            current = _select_list_item(current, selector)
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _split_field(field):
    parts = []
    current = []
    bracket_depth = 0
    for char in field:
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth = max(0, bracket_depth - 1)
        if char == "." and bracket_depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current))
    return parts


def _select_list_item(items, selector):
    if selector.isdigit():
        index = int(selector)
        return items[index] if index < len(items) else None
    if "=" not in selector:
        return None
    key, expected = selector.split("=", 1)
    for item in items:
        if isinstance(item, dict) and str(item.get(key)) == expected:
            return item
    return None
