from pathlib import Path


def file_pascal_case(project_root, params):
    root = Path(project_root, params.get("root", "."))
    suffix = params.get("suffix", "")
    for path in root.rglob(f"*{suffix}"):
        if not path.is_file():
            continue
        name = path.stem
        if not name or not name[0].isupper():
            return {
                "status": "fail",
                "message": f"{path.relative_to(project_root).as_posix()} is not PascalCase.",
                "details": {"path": path.relative_to(project_root).as_posix()},
            }
    return {
        "status": "pass",
        "message": f"Files under {root.relative_to(project_root).as_posix()} are PascalCase.",
        "details": {"root": root.relative_to(project_root).as_posix()},
    }
