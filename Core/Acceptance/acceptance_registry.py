import importlib
import importlib.util
import sys
from pathlib import Path

ACCEPTANCE_ROOT = Path(__file__).resolve().parent
AIWORKFLOW_ROOT = ACCEPTANCE_ROOT.parents[1]
ADAPTERS_ROOT = AIWORKFLOW_ROOT / "Adapters"
MODES_ROOT = AIWORKFLOW_ROOT / "Modes"

for import_root in [ACCEPTANCE_ROOT, AIWORKFLOW_ROOT]:
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

CHECKS = {
    "common.file.exists": ("checks.common.file_checks", "exists"),
    "common.file.not_exists": ("checks.common.file_checks", "not_exists"),
    "common.content.contains": ("checks.common.content_checks", "contains"),
    "common.content.not_contains": ("checks.common.content_checks", "not_contains"),
    "common.content.matches_regex": ("checks.common.content_checks", "matches_regex"),
    "common.json.field_matches": ("checks.common.json_checks", "field_matches"),
    "common.naming.file_pascal_case": ("checks.common.naming_checks", "file_pascal_case"),
    "common.boundary.only_allowed_files_changed": ("checks.common.boundary_checks", "only_allowed_files_changed"),
    "aiworkflow.context.current_json_valid": ("checks.aiworkflow.context_checks", "current_json_valid"),
    "aiworkflow.context.aitdd_policy_valid": ("checks.aiworkflow.context_checks", "aitdd_policy_valid"),
    "aiworkflow.record.goal_version_added": ("checks.aiworkflow.record_checks", "goal_version_added"),
    "dotnet.compile_passed": ("checks.dotnet.compile_checks", "build_passed"),
    "python.py_compile_passed": ("checks.python.compile_checks", "py_compile_passed"),
    "python.unittest_passed": ("checks.python.compile_checks", "unittest_passed"),
}


def list_modes():
    return sorted(_discover_modes().keys())


def list_checks():
    return sorted(_discover_checks().keys())


def load_mode(mode_id):
    modes = _discover_modes()
    if mode_id not in modes:
        raise KeyError(f"Unknown mode: {mode_id}")
    module = importlib.import_module(modes[mode_id])
    return module.MODE


def load_check(check_id):
    checks = _discover_checks()
    if check_id not in checks:
        raise KeyError(f"Unknown check: {check_id}")
    module_name, function_name = checks[check_id]
    module = _import_check_module(module_name)
    return getattr(module, function_name)


def _discover_checks():
    discovered = dict(CHECKS)
    module_path = ADAPTERS_ROOT / "acceptance_registry.py"
    if module_path.exists():
        spec = importlib.util.spec_from_file_location("_aiworkflow_adapter_registry", module_path)
        if spec is not None and spec.loader is not None:
            adapter_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(adapter_module)
            discovered.update(getattr(adapter_module, "CHECKS", {}))
    return discovered


def _import_check_module(module_name):
    if module_name.startswith("checks.project.") or module_name.startswith("checks.unity."):
        module_path = ADAPTERS_ROOT / Path(*module_name.split(".")).with_suffix(".py")
        if module_path.exists():
            spec_name = f"_aiworkflow_adapter_{module_name.replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(spec_name, module_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
    return importlib.import_module(module_name)


def _discover_modes():
    discovered = {}
    discovered.update(_discover_mode_tree(ACCEPTANCE_ROOT / "modes", "modes"))
    for mode_root in MODES_ROOT.glob("*/"):
        discovered.update(_discover_mode_tree(mode_root, f"Modes.{mode_root.name}"))
    return discovered


def _discover_mode_tree(root, module_prefix):
    discovered = {}
    discovered.update(_discover_mode_files(root, module_prefix, ""))
    discovered.update(_discover_mode_files(root / "temp", f"{module_prefix}.temp", "temp."))
    return discovered


def _discover_mode_files(root, module_prefix, id_prefix):
    if not root.exists():
        return {}
    result = {}
    for path in root.glob("*.py"):
        if path.name.startswith("_"):
            continue
        mode_id = f"{id_prefix}{path.stem}"
        result[mode_id] = f"{module_prefix}.{path.stem}"
    return result
