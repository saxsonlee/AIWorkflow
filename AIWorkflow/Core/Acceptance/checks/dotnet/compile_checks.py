import subprocess
from pathlib import Path


def build_passed(project_root, params):
    project = params.get("project")
    if not project:
        return {
            "status": "blocked",
            "message": "No dotnet project was provided.",
        }

    root = Path(project_root)
    project_path = root / project
    if not project_path.exists():
        return {
            "status": "fail",
            "message": f"{project} does not exist.",
        }

    timeout_seconds = int(params.get("timeoutSeconds", 180))
    completed = subprocess.run(
        ["dotnet", "build", str(project_path)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
    )

    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    if completed.returncode == 0:
        return {
            "status": "pass",
            "message": f"dotnet build passed for {project}.",
            "details": {"project": project},
        }

    return {
        "status": "fail",
        "message": f"dotnet build failed for {project}.",
        "details": {
            "project": project,
            "exitCode": completed.returncode,
            "outputTail": "\n".join(output.splitlines()[-80:]),
        },
    }
