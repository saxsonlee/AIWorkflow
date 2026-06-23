import py_compile
import subprocess
import sys

import path_resolver


def py_compile_passed(project_root, params):
    paths = params.get("paths", [])
    if isinstance(paths, str):
        paths = [paths]
    if not paths:
        return {
            "status": "blocked",
            "message": "No Python paths were provided for py_compile.",
        }

    compiled = []
    for path in paths:
        target = path_resolver.resolve_project_path(project_root, path)
        if not target.exists():
            return {
                "status": "fail",
                "message": f"{path} does not exist.",
            }
        try:
            py_compile.compile(str(target), doraise=True)
        except py_compile.PyCompileError as exc:
            return {
                "status": "fail",
                "message": f"{path} failed py_compile: {exc.msg}",
            }
        compiled.append(path)

    return {
        "status": "pass",
        "message": f"py_compile passed for {', '.join(compiled)}.",
    }


def unittest_passed(project_root, params):
    start_directory = params.get("startDirectory")
    pattern = params.get("pattern", "test*.py")
    timeout = int(params.get("timeoutSeconds", 120))
    if not start_directory:
        return {
            "status": "blocked",
            "message": "No unittest startDirectory was provided.",
        }

    target = path_resolver.resolve_project_path(project_root, start_directory)
    if not target.exists():
        return {
            "status": "fail",
            "message": f"{start_directory} does not exist.",
        }

    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(target),
        "-p",
        pattern,
        "-v",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=project_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "blocked",
            "message": f"unittest timed out after {timeout} seconds.",
        }

    output = (completed.stdout + completed.stderr).strip()
    if completed.returncode == 0:
        return {
            "status": "pass",
            "message": f"unittest passed for {start_directory}.",
            "details": {"output": output[-4000:]},
        }
    return {
        "status": "fail",
        "message": f"unittest failed for {start_directory}: {output[-4000:]}",
    }
