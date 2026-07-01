import argparse
import shutil
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ACCEPTANCE_ROOT = Path(__file__).resolve().parent
CORE_ROOT = ACCEPTANCE_ROOT.parent
AIWORKFLOW_ROOT = CORE_ROOT.parent
PROJECT_ROOT = AIWORKFLOW_ROOT.parent
WORKSPACE_ROOT = AIWORKFLOW_ROOT / "Workspace"
CURRENT_PATH = Path("Workspace/Current.json")

sys.path.insert(0, str(ACCEPTANCE_ROOT))

import acceptance_registry
import aitdd_policy
import path_resolver
import report_writer


EXIT_CODES = {
    "pass": 0,
    "fail": 2,
    "blocked": 3,
    "error": 10,
}

ITERATION_TYPES = {
    "initial",
    "adjustment",
    "fix",
    "validation",
    "maintenance",
    "archive",
}

STATUSES = {
    "pending",
    "pass",
    "fail",
    "blocked",
}

EVIDENCE_TYPES = {
    "contract",
    "behavior",
    "browser",
}


def main():
    parser = argparse.ArgumentParser(description="AI-TDD acceptance runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--dry-run", action="store_true")
    run_parser.add_argument("--template-smoke", action="store_true")

    subparsers.add_parser("validate-current")
    subparsers.add_parser("validate-resolution")
    subparsers.add_parser("validate-iteration")
    subparsers.add_parser("list-modes")
    subparsers.add_parser("list-checks")
    subparsers.add_parser("latest")
    policy_parser = subparsers.add_parser("policy")
    policy_subparsers = policy_parser.add_subparsers(dest="policy_command", required=True)
    policy_subparsers.add_parser("show")
    policy_set_parser = policy_subparsers.add_parser("set")
    policy_set_parser.add_argument("--default-mode", choices=sorted(aitdd_policy.DEFAULT_MODES))
    policy_set_parser.add_argument("--formal-run-policy", choices=sorted(aitdd_policy.FORMAL_RUN_POLICIES))
    policy_set_parser.add_argument("--template-workspace-policy", choices=sorted(aitdd_policy.TEMPLATE_WORKSPACE_POLICIES))
    policy_subparsers.add_parser("init")

    args = parser.parse_args()

    try:
        if args.command == "run":
            return run(args)
        if args.command == "validate-current":
            validate_current()
            print("Current.json valid.")
            return 0
        if args.command == "validate-resolution":
            current = validate_current()
            validate_resolution(current["resolutionPath"])
            print("Resolution.json valid.")
            return 0
        if args.command == "validate-iteration":
            current = validate_current()
            resolution = validate_resolution(current["resolutionPath"])
            validate_iteration(current, resolution)
            print("Iteration valid.")
            return 0
        if args.command == "list-modes":
            for mode in acceptance_registry.list_modes():
                print(mode)
            return 0
        if args.command == "list-checks":
            for check in acceptance_registry.list_checks():
                print(check)
            return 0
        if args.command == "latest":
            latest_path = WORKSPACE_ROOT / "LatestRun.md"
            if not latest_path.exists():
                print("LatestRun.md does not exist.")
                return EXIT_CODES["blocked"]
            print(latest_path.read_text(encoding="utf-8-sig"))
            return 0
        if args.command == "policy":
            return policy_command(args)
    except Exception as ex:
        print(f"runner error: {ex}", file=sys.stderr)
        return EXIT_CODES["error"]


def run(args):
    current = validate_current()
    resolution = validate_resolution(current["resolutionPath"])
    iteration = validate_iteration(current, resolution)
    acceptance = iteration.get("acceptance")

    if not acceptance:
        return _write_blocked_without_acceptance(current, iteration)

    mode_ids = acceptance["modes"]
    modes = [acceptance_registry.load_mode(mode_id) for mode_id in mode_ids]
    context = _check_context(current, resolution, iteration)
    checks = _annotate_checks(_resolve_checks(_merge_checks(_mode_checks(modes, "checks"), acceptance.get("extraChecks", [])), context))
    post_checks = _annotate_checks(_resolve_checks(_merge_checks(_mode_checks(modes, "postChecks"), acceptance.get("extraPostChecks", [])), context))
    required_evidence = acceptance.get("requiredEvidence", ["contract"])
    semantic_hints = acceptance.get("semanticHints", [])
    gate_findings = _audit_semantic_gates(checks + post_checks)
    gate_findings.extend(_audit_semantic_hints(semantic_hints, required_evidence))
    gate_findings.extend(_audit_required_evidence(checks + post_checks, required_evidence))

    if args.dry_run:
        dry_run = {
            "topic": current["topic"],
            "issue": current["issue"],
            "iteration": iteration["version"],
            "modes": mode_ids,
            "requiredEvidence": required_evidence,
            "semanticHints": semantic_hints,
            "templateSmoke": args.template_smoke,
            "modeSnapshots": modes,
            "checks": checks,
            "postChecks": post_checks,
            "semanticGateFindings": gate_findings,
        }
        print(json.dumps(dry_run, ensure_ascii=False, indent=2))
        return 0

    if _is_template_workspace(current) and not args.template_smoke:
        print("验收被阻塞：模板工作区只能用于安装烟测。真实任务验收前请先创建或切换到正式 Topic / Issue / Iteration；如只验证安装，请运行 run --template-smoke。")
        return EXIT_CODES["blocked"]

    now = _now()
    run_date = now.strftime("%Y_%m_%d")
    run_dir = _next_run_dir(Path(current["resolutionPath"]).parent / "Runs" / run_date)
    run_id = Path(run_dir).name
    results = []
    errors = []

    for finding in gate_findings:
        results.append(finding)

    for check_call in checks:
        results.append(_run_check(check_call, errors))

    status = _summarize(results)
    summary = _summary(status)
    artifacts = _build_artifacts(current, run_dir)
    artifacts.extend(_archive_check_artifacts(run_dir, checks, status))
    result = _build_result(
        current,
        iteration,
        run_id,
        status,
        summary,
        results,
        errors,
        now,
        mode_ids,
        modes,
        required_evidence,
        semantic_hints,
        checks,
        post_checks,
        gate_findings,
        run_dir,
        artifacts,
    )
    report_writer.write_outputs(PROJECT_ROOT, run_dir, result, WORKSPACE_ROOT)
    _update_iteration(current["resolutionPath"], iteration["version"], status, run_dir, current)

    for check_call in post_checks:
        results.append(_run_check(check_call, errors))

    if post_checks:
        status = _summarize(results)
        summary = _summary(status)
        artifacts = _build_artifacts(current, run_dir)
        artifacts.extend(_archive_check_artifacts(run_dir, checks + post_checks, status))
        result = _build_result(
            current,
            iteration,
            run_id,
            status,
            summary,
            results,
            errors,
            now,
            mode_ids,
            modes,
            required_evidence,
            semantic_hints,
            checks,
            post_checks,
            gate_findings,
            run_dir,
            artifacts,
        )
        report_writer.write_outputs(PROJECT_ROOT, run_dir, result, WORKSPACE_ROOT)
        _update_iteration(current["resolutionPath"], iteration["version"], status, run_dir, current)

    print(summary)
    return EXIT_CODES[status]


def validate_current():
    path = AIWORKFLOW_ROOT / CURRENT_PATH
    if not path.exists():
        raise FileNotFoundError(CURRENT_PATH.as_posix())
    data = json.loads(path.read_text(encoding="utf-8-sig"))
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
    _require_fields(data, required, "Current.json")
    for key in ["topicPath", "issuePath", "decisionPath", "resolutionPath", "iterationPath"]:
        if not path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, data[key]).exists():
            raise FileNotFoundError(f"{key}: {data[key]}")
    if not data["currentIteration"]:
        raise ValueError("Current.json currentIteration is empty.")
    aitdd_policy.load_policy(AIWORKFLOW_ROOT)
    return data


def policy_command(args):
    if args.policy_command == "show":
        policy = aitdd_policy.load_policy(AIWORKFLOW_ROOT)
        print(json.dumps(policy, ensure_ascii=False, indent=2))
        return 0
    if args.policy_command == "init":
        path = aitdd_policy.create_default_policy(AIWORKFLOW_ROOT)
        print(f"{path_resolver.to_aiworkflow_relative(path.relative_to(AIWORKFLOW_ROOT).as_posix())} ready.")
        return 0
    if args.policy_command == "set":
        if not any([args.default_mode, args.formal_run_policy, args.template_workspace_policy]):
            raise ValueError("policy set requires at least one option.")
        policy = aitdd_policy.update_policy(
            AIWORKFLOW_ROOT,
            default_mode=args.default_mode,
            formal_run_policy=args.formal_run_policy,
            template_workspace_policy=args.template_workspace_policy,
        )
        print(json.dumps(policy, ensure_ascii=False, indent=2))
        return 0


def validate_resolution(resolution_path):
    path = path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, resolution_path)
    if not path.exists():
        raise FileNotFoundError(resolution_path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    required = ["schemaVersion", "topic", "issue", "status", "currentIteration", "iterations"]
    _require_fields(data, required, "Resolution.json")
    if data["status"] != "active":
        raise ValueError("Resolution.json status must be active.")
    if not isinstance(data["iterations"], list):
        raise ValueError("Resolution.json iterations must be a list.")
    if _current_iteration(data) is None:
        raise ValueError("Resolution.json currentIteration is missing from iterations.")
    return data


def validate_iteration(current, resolution):
    iteration = _current_iteration(resolution)
    _require_fields(iteration, ["version", "createdAt", "type", "summary", "status", "detailPath"], "Resolution.json current iteration")
    if iteration["version"] != current["currentIteration"]:
        raise ValueError("Current.json currentIteration does not match Resolution.json currentIteration.")
    if iteration["detailPath"] != current["iterationPath"]:
        raise ValueError("Current.json iterationPath does not match Resolution.json current iteration detailPath.")
    if iteration["type"] not in ITERATION_TYPES:
        raise ValueError(f"Unknown iteration type: {iteration['type']}")
    if iteration["status"] not in STATUSES:
        raise ValueError(f"Unknown iteration status: {iteration['status']}")
    if not path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, iteration["detailPath"]).exists():
        raise FileNotFoundError(f"detailPath: {iteration['detailPath']}")
    if "acceptance" in iteration:
        _validate_acceptance(iteration["acceptance"])
    return iteration


def _validate_acceptance(acceptance):
    if "mode" in acceptance:
        raise ValueError("iteration acceptance.mode is no longer supported; use acceptance.modes.")
    _require_fields(acceptance, ["modes", "extraChecks"], "iteration acceptance")
    if not isinstance(acceptance["modes"], list) or not acceptance["modes"]:
        raise ValueError("iteration acceptance.modes must be a non-empty list.")
    for mode_id in acceptance["modes"]:
        if not isinstance(mode_id, str) or not mode_id:
            raise ValueError("iteration acceptance.modes must contain non-empty strings.")
    if not isinstance(acceptance["extraChecks"], list):
        raise ValueError("iteration acceptance.extraChecks must be a list.")
    if "extraPostChecks" in acceptance and not isinstance(acceptance["extraPostChecks"], list):
        raise ValueError("iteration acceptance.extraPostChecks must be a list.")
    if "requiredEvidence" in acceptance:
        _validate_required_evidence(acceptance["requiredEvidence"])
    if "semanticHints" in acceptance:
        _validate_semantic_hints(acceptance["semanticHints"])


def _validate_required_evidence(required_evidence):
    if not isinstance(required_evidence, list) or not required_evidence:
        raise ValueError("iteration acceptance.requiredEvidence must be a non-empty list.")
    for evidence_type in required_evidence:
        if evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f"Unknown required evidence type: {evidence_type}")


def _validate_semantic_hints(semantic_hints):
    if not isinstance(semantic_hints, list):
        raise ValueError("iteration acceptance.semanticHints must be a list.")
    for hint in semantic_hints:
        if hint not in EVIDENCE_TYPES:
            raise ValueError(f"Unknown semantic hint: {hint}")


def _run_check(check_call, errors):
    try:
        _require_fields(check_call, ["id", "name", "severity", "params"], "check call")
        if check_call["severity"] != "required":
            raise ValueError("Only required severity is supported.")
        check = acceptance_registry.load_check(check_call["id"])
        raw = check(PROJECT_ROOT, check_call["params"])
        status = raw.get("status", "blocked")
        message = raw.get("message", "")
    except Exception as ex:
        status = "blocked"
        message = f"Check execution failed: {ex}"
        errors.append(message)
    return {
        "id": check_call.get("id", "unknown"),
        "name": check_call.get("name", "unknown"),
        "severity": check_call.get("severity", "required"),
        "acceptanceType": _check_acceptance_type(check_call),
        "status": status,
        "message": message,
    }


def _merge_checks(mode_checks, iteration_checks):
    return list(mode_checks) + list(iteration_checks)


def _mode_checks(modes, key):
    result = []
    for mode in modes:
        result.extend(mode.get(key, []))
    return result


def _build_result(
    current,
    iteration,
    run_id,
    status,
    summary,
    results,
    errors,
    started_at,
    mode_ids,
    mode_snapshots,
    required_evidence,
    semantic_hints,
    checks,
    post_checks,
    semantic_gate_findings,
    run_dir,
    artifacts,
):
    return {
        "schemaVersion": "1.0",
        "topic": current["topic"],
        "issue": current["issue"],
        "iteration": iteration["version"],
        "runId": run_id,
        "status": status,
        "summary": summary,
        "startedAt": started_at.isoformat(),
        "finishedAt": _now().isoformat(),
        "modes": mode_ids,
        "modeSnapshots": mode_snapshots,
        "requiredEvidence": required_evidence,
        "semanticHints": semantic_hints,
        "resolvedChecks": checks,
        "resolvedPostChecks": post_checks,
        "semanticGateFindings": semantic_gate_findings,
        "checks": results,
        "artifacts": artifacts,
        "command": " ".join(sys.argv),
        "currentPath": CURRENT_PATH.as_posix(),
        "topicPath": current["topicPath"],
        "issuePath": current["issuePath"],
        "decisionPath": current["decisionPath"],
        "resolutionPath": current["resolutionPath"],
        "iterationPath": current["iterationPath"],
        "errors": errors,
    }


def _build_artifacts(current, run_dir):
    run_path = path_resolver.to_aiworkflow_relative(Path(run_dir).as_posix())
    return [
        {"type": "report", "path": f"{run_path}/AcceptanceReport.md"},
        {"type": "result", "path": f"{run_path}/Result.json"},
        {"type": "log", "path": f"{run_path}/Run.log"},
        {"type": "iteration", "path": current["iterationPath"]},
    ]


def _archive_check_artifacts(run_dir, check_calls, status):
    artifacts = []
    archived_targets = set()
    for check_call in check_calls:
        for artifact in check_call.get("artifacts", []):
            source = artifact.get("source")
            target_name = artifact.get("targetName")
            artifact_type = artifact.get("type", "check-artifact")
            remove_source = artifact.get("removeSource", False) and status == "pass"
            if not source or not target_name:
                continue
            target_key = f"{source}->{target_name}"
            if target_key in archived_targets:
                continue
            archived_targets.add(target_key)
            source_path = path_resolver.resolve_project_path(PROJECT_ROOT, source)
            if not source_path.exists():
                continue
            target_path = path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, run_dir) / target_name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)
            artifacts.append({"type": artifact_type, "path": path_resolver.to_aiworkflow_relative(target_path.relative_to(AIWORKFLOW_ROOT).as_posix())})
            if remove_source:
                source_path.unlink()
    return artifacts


def _next_run_dir(date_dir):
    date_dir_abs = path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, date_dir)
    date_dir_abs.mkdir(parents=True, exist_ok=True)
    max_index = 0
    for item in date_dir_abs.iterdir():
        if not item.is_dir():
            continue
        name = item.name
        if len(name) == 4 and name.startswith("r") and name[1:].isdigit():
            max_index = max(max_index, int(name[1:]))
    return date_dir / f"r{max_index + 1:03d}"


def _current_iteration(resolution):
    return next((item for item in resolution["iterations"] if item.get("version") == resolution["currentIteration"]), None)


def _check_context(current, resolution, iteration):
    return {
        "topic": current["topic"],
        "issue": current["issue"],
        "resolution.path": current["resolutionPath"],
        "iteration": iteration["version"],
        "iteration.path": iteration["detailPath"],
        "current.iteration": iteration["version"],
    }


def _resolve_checks(checks, context):
    return [_resolve_value(check, context) for check in checks]


def _annotate_checks(checks):
    return [_annotate_check(check) for check in checks]


def _annotate_check(check):
    result = dict(check)
    result.setdefault("acceptanceType", _check_acceptance_type(result))
    return result


def _resolve_value(value, context):
    if isinstance(value, dict):
        return {key: _resolve_value(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_value(item, context) for item in value]
    if isinstance(value, str):
        result = value
        for key, item in context.items():
            result = result.replace("${" + key + "}", item)
        return result
    return value


def _audit_semantic_gates(checks):
    targets = _semantic_targets(checks)
    findings = []
    gate_ids = {check.get("id", "") for check in checks}
    gate_text = json.dumps(checks, ensure_ascii=False)

    gate_rules = [
        {
            "extension": ".cs",
            "name": "C# / host compilation semantic gate",
            "acceptedIds": {
                "unity.editor.execution_report_passed",
                "unity.editor.compile_fresh",
                "dotnet.compile_passed",
                "csharp.compile_passed",
            },
            "acceptedTexts": [
                "runtime assembly",
                "editor assembly",
                "host compile",
                "compile",
                "compilation",
            ],
        },
        {
            "extension": ".lua",
            "name": "Lua semantic or runtime gate",
            "acceptedIds": {
                "unity.editor.execution_report_passed",
                "lua.syntax_passed",
                "lua.runtime_passed",
                "xlua.runtime_smoke_passed",
            },
            "acceptedTexts": [
                "script syntax",
                "script runtime",
                "host bridge",
                "syntax",
                "runtime",
            ],
        },
        {
            "extension": ".py",
            "name": "Python syntax gate",
            "acceptedIds": {
                "python.py_compile_passed",
            },
            "acceptedTexts": [
                "py_compile",
            ],
        },
        {
            "extension": ".json",
            "name": "JSON parse or field gate",
            "acceptedIds": {
                "common.json.field_matches",
                "common.json.valid",
            },
            "acceptedTexts": [],
        },
    ]

    for rule in gate_rules:
        paths = sorted(path for path in targets if path.lower().endswith(rule["extension"]))
        if not paths:
            continue
        has_gate = bool(gate_ids.intersection(rule["acceptedIds"])) or any(text in gate_text for text in rule["acceptedTexts"])
        has_waiver = _has_semantic_gate_waiver(checks, rule["extension"])
        if has_gate or has_waiver:
            continue
        findings.append(
            {
                "id": "aiworkflow.mode.semantic_gate_audit",
                "name": f"Missing {rule['name']}",
                "severity": "required",
                "acceptanceType": "contract",
                "status": "blocked",
                "message": (
                    f"Mode checks {', '.join(paths)} with text/file assertions but has no semantic gate "
                    f"for {rule['extension']} targets."
                ),
            }
        )
    return findings


def _audit_required_evidence(checks, required_evidence):
    findings = []
    for evidence_type in required_evidence:
        if _has_evidence_type(checks, evidence_type):
            continue
        findings.append(
            {
                "id": "aiworkflow.acceptance.required_evidence",
                "name": f"Missing {evidence_type} acceptance evidence",
                "severity": "required",
                "acceptanceType": evidence_type,
                "status": "blocked",
                "message": f"Iteration declares requiredEvidence '{evidence_type}', but no resolved check provides it.",
            }
        )
    return findings


def _audit_semantic_hints(semantic_hints, required_evidence):
    findings = []
    required = set(required_evidence)
    for hint in semantic_hints:
        if hint in required:
            continue
        findings.append(
            {
                "id": "aiworkflow.acceptance.semantic_hint_evidence",
                "name": f"Missing requiredEvidence for semantic hint {hint}",
                "severity": "required",
                "acceptanceType": hint,
                "status": "blocked",
                "message": (
                    f"Iteration declares semanticHints '{hint}', but acceptance.requiredEvidence "
                    f"does not include '{hint}'."
                ),
            }
        )
    return findings


def _has_evidence_type(checks, evidence_type):
    for check in checks:
        check_type = _check_acceptance_type(check)
        if check_type != evidence_type:
            continue
        if evidence_type in {"behavior", "browser"} and not _check_has_driver_evidence(check):
            continue
        return True
    return False


def _check_has_driver_evidence(check):
    params = check.get("params", {})
    driver_keys = ["driver", "driverPath", "driverCommand", "driverScript", "driverArtifact"]
    if any(params.get(key) for key in driver_keys):
        return True
    for artifact in check.get("artifacts", []):
        artifact_type = str(artifact.get("type", "")).lower()
        if "video" in artifact_type:
            continue
        if artifact.get("evidence") is True:
            return True
        if any(token in artifact_type for token in ["driver", "behavior", "browser-trace", "browser-dom", "browser-accessibility", "browser-json", "ui-metadata", "ui-log", "e2e-log"]):
            return True
    evidence = str(check.get("evidence", "")).lower()
    return evidence in {"behavior-driver", "browser-driver", "driver-artifact"}


def _check_acceptance_type(check):
    explicit = check.get("acceptanceType") or check.get("acceptanceCategory")
    if explicit:
        return explicit
    evidence = str(check.get("evidence", "")).lower()
    if evidence.startswith("behavior"):
        return "behavior"
    if evidence.startswith("browser") or evidence.startswith("ui"):
        return "browser"
    if _check_has_driver_evidence(check):
        return "behavior"
    return "contract"


def _semantic_targets(checks):
    targets = set()
    for check in checks:
        params = check.get("params", {})
        for key in ["path", "source"]:
            value = params.get(key)
            if isinstance(value, str):
                targets.add(value.replace("\\", "/"))
        for artifact in check.get("artifacts", []):
            source = artifact.get("source")
            if isinstance(source, str):
                targets.add(source.replace("\\", "/"))
    return targets


def _has_semantic_gate_waiver(checks, extension):
    marker = f"semanticGateWaiver:{extension}"
    for check in checks:
        params = check.get("params", {})
        if params.get("semanticGateWaiver") == extension:
            return True
        if marker in check.get("name", ""):
            return True
    return False


def _summarize(results):
    if any(item["status"] == "blocked" for item in results):
        return "blocked"
    if any(item["severity"] == "required" and item["status"] == "fail" for item in results):
        return "fail"
    return "pass"


def _summary(status):
    return {
        "pass": "验收通过。",
        "fail": "验收失败，存在 required 检查失败。",
        "blocked": "验收被阻塞，存在无法执行的检查。",
    }[status]


def _is_template_workspace(current):
    if str(current.get("source", "")).upper() == "TEMPLATE":
        return True
    return current.get("topic") == "ExampleTopic" and current.get("issue") == "ExampleIssue"


def _update_iteration(resolution_path, version, status, run_dir, current=None):
    path = path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, resolution_path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    relative_run = path_resolver.to_aiworkflow_relative(Path(run_dir).as_posix())
    for item in data["iterations"]:
        if item.get("version") == version:
            item["status"] = status
            item["latestRunPath"] = relative_run
            break
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if current:
        _update_iteration_detail(current["iterationPath"], status, relative_run)


def _update_iteration_detail(iteration_path, status, relative_run):
    path = path_resolver.resolve_aiworkflow_path(AIWORKFLOW_ROOT, iteration_path)
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8-sig")
    report_path = f"{relative_run}/AcceptanceReport.md"
    result_path = f"{relative_run}/Result.json"
    run_id = Path(relative_run).name

    text = _replace_or_add_line(text, "- Status：", f"- Status：{status}", "## 基础信息")
    text = _replace_or_add_line(text, "- 结果：", f"- 结果：{status}。", "## 验收")
    text = _replace_or_add_line(text, "- Run：", f"- Run：{run_id}。", "## 验收")
    text = _replace_or_add_line(text, "- Report：", f"- Report：`{report_path}`。", "## 验收")
    text = _replace_or_add_line(text, "- Result：", f"- Result：`{result_path}`。", "## 验收")
    path.write_text(text, encoding="utf-8")


def _replace_or_add_line(text, prefix, replacement, section_title):
    lines = text.splitlines()
    section_index = _find_line(lines, section_title)
    if section_index is None:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend([section_title, "", replacement])
        return "\n".join(lines) + "\n"

    next_section = _find_next_section(lines, section_index + 1)
    for index in range(section_index + 1, next_section):
        if lines[index].startswith(prefix):
            lines[index] = replacement
            return "\n".join(lines) + "\n"

    insert_index = next_section
    while insert_index > section_index + 1 and lines[insert_index - 1] == "":
        insert_index -= 1
    lines.insert(insert_index, replacement)
    return "\n".join(lines) + "\n"


def _find_line(lines, target):
    for index, line in enumerate(lines):
        if line.strip() == target:
            return index
    return None


def _find_next_section(lines, start):
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            return index
    return len(lines)


def _write_blocked_without_acceptance(current, iteration):
    now = _now()
    run_date = now.strftime("%Y_%m_%d")
    run_dir = _next_run_dir(Path(current["resolutionPath"]).parent / "Runs" / run_date)
    run_id = Path(run_dir).name
    result = _build_result(
        current,
        iteration,
        run_id,
        "blocked",
        "验收被阻塞，当前 Iteration 未定义 acceptance。",
        [],
        ["Current iteration has no acceptance."],
        now,
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        run_dir,
        _build_artifacts(current, run_dir),
    )
    report_writer.write_outputs(PROJECT_ROOT, run_dir, result, WORKSPACE_ROOT)
    _update_iteration(current["resolutionPath"], iteration["version"], "blocked", run_dir, current)
    print(result["summary"])
    return EXIT_CODES["blocked"]


def _require_fields(data, fields, label):
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def _now():
    return datetime.now(timezone(timedelta(hours=8)))


if __name__ == "__main__":
    raise SystemExit(main())
