import json
from pathlib import Path


DEFAULT_POLICY = {
    "schemaVersion": "1.0",
    "defaultMode": "enabled",
    "formalRunPolicy": "explicit",
    "templateWorkspacePolicy": "smoke-only",
    "userOverridePhrases": {
        "disable": [
            "先不用 AITDD",
            "只讨论",
            "不需要验收",
        ],
        "formalRun": [
            "正式验收",
            "准备提交",
            "进行 AITDD 验证",
        ],
    },
    "notes": [
        "defaultMode=enabled 表示当前项目默认启用 AITDD；AI 必须读取本文件后执行策略，而不是自行判断开关。",
        "formalRunPolicy=explicit 表示正式 run 需要用户明确要求，或当前任务已经进入明确的提交/正式验收阶段。",
        "templateWorkspacePolicy=smoke-only 表示模板工作区只能用于安装烟测，不能作为真实任务验收入口。",
    ],
}

DEFAULT_MODES = {"enabled", "manual", "off"}
FORMAL_RUN_POLICIES = {"explicit", "auto"}
TEMPLATE_WORKSPACE_POLICIES = {"smoke-only"}


def policy_path(aiworkflow_root):
    return Path(aiworkflow_root) / "Workspace" / "AITDDPolicy.json"


def load_policy(aiworkflow_root):
    path = policy_path(aiworkflow_root)
    if not path.exists():
        raise FileNotFoundError(path.relative_to(aiworkflow_root).as_posix())
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    validate_policy(data)
    return data


def save_policy(aiworkflow_root, policy):
    validate_policy(policy)
    path = policy_path(aiworkflow_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)
    return path


def create_default_policy(aiworkflow_root, overwrite=False):
    path = policy_path(aiworkflow_root)
    if path.exists() and not overwrite:
        return path
    return save_policy(aiworkflow_root, dict(DEFAULT_POLICY))


def update_policy(aiworkflow_root, default_mode=None, formal_run_policy=None, template_workspace_policy=None):
    try:
        policy = load_policy(aiworkflow_root)
    except FileNotFoundError:
        policy = dict(DEFAULT_POLICY)
    if default_mode is not None:
        policy["defaultMode"] = default_mode
    if formal_run_policy is not None:
        policy["formalRunPolicy"] = formal_run_policy
    if template_workspace_policy is not None:
        policy["templateWorkspacePolicy"] = template_workspace_policy
    save_policy(aiworkflow_root, policy)
    return policy


def validate_policy(policy):
    required = [
        "schemaVersion",
        "defaultMode",
        "formalRunPolicy",
        "templateWorkspacePolicy",
        "userOverridePhrases",
    ]
    missing = [key for key in required if key not in policy]
    if missing:
        raise ValueError(f"AITDDPolicy.json missing fields: {', '.join(missing)}")
    if policy["defaultMode"] not in DEFAULT_MODES:
        raise ValueError("AITDDPolicy.json defaultMode must be enabled, manual, or off.")
    if policy["formalRunPolicy"] not in FORMAL_RUN_POLICIES:
        raise ValueError("AITDDPolicy.json formalRunPolicy must be explicit or auto.")
    if policy["templateWorkspacePolicy"] not in TEMPLATE_WORKSPACE_POLICIES:
        raise ValueError("AITDDPolicy.json templateWorkspacePolicy must be smoke-only.")
    overrides = policy["userOverridePhrases"]
    if not isinstance(overrides, dict):
        raise ValueError("AITDDPolicy.json userOverridePhrases must be an object.")
    for key in ["disable", "formalRun"]:
        value = overrides.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"AITDDPolicy.json userOverridePhrases.{key} must be a non-empty string list.")
