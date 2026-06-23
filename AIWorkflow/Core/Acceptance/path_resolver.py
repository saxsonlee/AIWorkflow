from pathlib import Path


AIWORKFLOW_PREFIX = "ProjectHelp/AIWorkflow/"
AIWORKFLOW_RELATIVE_PREFIXES = ("Core/", "Workspace/", "Workspace.Template/", "Skill.Template/", "Adapters/", "Modes/")


def aiworkflow_root_from_acceptance():
    return Path(__file__).resolve().parents[2]


def display_path(project_root, target):
    try:
        return Path(target).relative_to(project_root).as_posix()
    except ValueError:
        return Path(target).as_posix()


def to_aiworkflow_relative(path):
    text = _normalize(path)
    if text.startswith(AIWORKFLOW_PREFIX):
        return text[len(AIWORKFLOW_PREFIX):]
    return text


def to_project_relative(path):
    text = _normalize(path)
    if text.startswith(AIWORKFLOW_PREFIX):
        return text
    if text.startswith(AIWORKFLOW_RELATIVE_PREFIXES):
        return AIWORKFLOW_PREFIX + text
    return text


def resolve_project_path(project_root, path):
    target = Path(path)
    if target.is_absolute():
        return target
    text = _normalize(path)
    if text.startswith(AIWORKFLOW_PREFIX):
        return Path(project_root, text)
    if text.startswith(AIWORKFLOW_RELATIVE_PREFIXES):
        return aiworkflow_root_from_acceptance() / text
    return Path(project_root, text)


def resolve_aiworkflow_path(aiworkflow_root, path):
    target = Path(path)
    if target.is_absolute():
        return target
    return Path(aiworkflow_root, to_aiworkflow_relative(path))


def _normalize(path):
    return str(path).replace("\\", "/")
