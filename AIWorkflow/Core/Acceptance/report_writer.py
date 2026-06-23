import json
from pathlib import Path

import path_resolver


def write_outputs(project_root, run_dir, result, workspace_root=None):
    run_path = path_resolver.resolve_project_path(project_root, run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    result_path = run_path / "Result.json"
    report_path = run_path / "AcceptanceReport.md"
    log_path = run_path / "Run.log"
    latest_path = Path(workspace_root) / "LatestRun.md" if workspace_root else Path(project_root, "ProjectHelp/AIWorkflow/Workspace/LatestRun.md")

    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(_build_report(result), encoding="utf-8")
    log_path.write_text(_build_log(result), encoding="utf-8")
    latest_path.write_text(_build_latest(result), encoding="utf-8")

    return {
        "result": result_path,
        "report": report_path,
        "log": log_path,
        "latest": latest_path,
    }


def _build_report(result):
    lines = [
        "# Acceptance Report",
        "",
        "## 基础信息",
        "",
        f"- Topic：{result['topic']}",
        f"- Issue：{result['issue']}",
        f"- Iteration：{result['iteration']}",
        f"- Run：{result['runId']}",
        f"- Status：{result['status']}",
        f"- StartedAt：{result['startedAt']}",
        f"- FinishedAt：{result['finishedAt']}",
        "",
        "## 验收结论",
        "",
        result["summary"],
        "",
        "## 验收类型",
        "",
        f"- Contract acceptance：{_type_status(result, 'contract')}",
        f"- Behavior acceptance：{_type_status(result, 'behavior')}",
        f"- Browser/UI acceptance：{_type_status(result, 'browser')}",
        "",
        "## 检查结果",
        "",
        "| 类型 | 级别 | 状态 | 检查项 | 说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for check in result["checks"]:
        lines.append(f"| {check.get('acceptanceType', 'contract')} | {check['severity']} | {check['status']} | {check['name']} | {check['message']} |")
    lines.extend(
        [
            "",
            "## 产物路径",
            "",
        ]
    )
    for artifact in result["artifacts"]:
        lines.append(f"- {artifact['type']}：{artifact['path']}")
    lines.append("")
    return "\n".join(lines)


def _build_log(result):
    lines = [
        f"[{result['startedAt']}] run started",
        f"command: {result.get('command', '')}",
        f"current: {result.get('currentPath', '')}",
        f"topic: {result['topic']}",
        f"issue: {result['issue']}",
        f"iteration: {result['iteration']}",
        f"run: {result['runId']}",
        f"modes: {', '.join(result.get('modes', []))}",
        "",
    ]
    for check in result["checks"]:
        lines.append(f"[check:{check['status']}] [{check.get('acceptanceType', 'contract')}] {check['id']} {check['name']} - {check['message']}")
    lines.extend(["", f"[result] status={result['status']} summary={result['summary']}", ""])
    if result.get("errors"):
        lines.append("[errors]")
        lines.extend(result["errors"])
        lines.append("")
    lines.append(f"[{result['finishedAt']}] run finished")
    lines.append("")
    return "\n".join(lines)


def _type_status(result, acceptance_type):
    checks = [item for item in result["checks"] if item.get("acceptanceType", "contract") == acceptance_type]
    if not checks:
        return "not declared"
    if any(item["status"] == "blocked" for item in checks):
        return "blocked"
    if any(item["severity"] == "required" and item["status"] == "fail" for item in checks):
        return "fail"
    return "pass"


def _build_latest(result):
    artifact_map = {item["type"]: item["path"] for item in result["artifacts"]}
    lines = [
        "# 最近一次验收",
        "",
        "## 摘要",
        "",
        f"- Topic：{result['topic']}",
        f"- Issue：{result['issue']}",
        f"- Iteration：{result['iteration']}",
        f"- Run：{result['runId']}",
        f"- Status：{result['status']}",
        f"- FinishedAt：{result['finishedAt']}",
        f"- Summary：{result['summary']}",
        "",
        "## 文件入口",
        "",
        f"- Report：{artifact_map.get('report', '')}",
        f"- Result：{artifact_map.get('result', '')}",
        f"- Log：{artifact_map.get('log', '')}",
        f"- Iteration：{artifact_map.get('iteration', '')}",
        "",
    ]
    return "\n".join(lines)
