#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_DIR="${SCRIPT_DIR}/aiworkflow-trigger"
PROJECT_SEARCH="$SCRIPT_DIR"
PROJECT_CODEX_DIR=""
USER_CODEX_DIR="${HOME}/.codex"

echo "AIWorkflow skill installer"
echo

if [ ! -f "${SOURCE_DIR}/SKILL.md" ]; then
  echo "[error] Skill source not found:"
  echo "${SOURCE_DIR}/SKILL.md"
  exit 1
fi

while :; do
  if [ -d "${PROJECT_SEARCH}/.codex" ]; then
    PROJECT_CODEX_DIR="${PROJECT_SEARCH}/.codex"
    break
  fi

  NEXT=$(cd "${PROJECT_SEARCH}/.." && pwd)
  if [ "$NEXT" = "$PROJECT_SEARCH" ]; then
    break
  fi
  PROJECT_SEARCH="$NEXT"
done

if [ -n "$PROJECT_CODEX_DIR" ]; then
  TARGET_SKILLS_DIR="${PROJECT_CODEX_DIR}/skills"
  TARGET_KIND="project"
elif [ -d "$USER_CODEX_DIR" ]; then
  TARGET_SKILLS_DIR="${USER_CODEX_DIR}/skills"
  TARGET_KIND="user"
else
  echo "[error] Could not find project .codex or user .codex."
  echo "Project search started from:"
  echo "$SCRIPT_DIR"
  echo
  echo "Expected one of:"
  echo "<project>/.codex"
  echo "$USER_CODEX_DIR"
  exit 1
fi

TARGET_DIR="${TARGET_SKILLS_DIR}/aiworkflow-trigger"

echo "Source:"
echo "$SOURCE_DIR"
echo
echo "Target [${TARGET_KIND}]:"
echo "$TARGET_DIR"
echo

mkdir -p "$TARGET_SKILLS_DIR"
rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo
echo "[success] AIWorkflow skill installed."
echo "Skill file:"
echo "${TARGET_DIR}/SKILL.md"
