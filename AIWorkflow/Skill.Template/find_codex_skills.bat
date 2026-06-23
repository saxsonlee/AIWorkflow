@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "SOURCE_DIR=%SCRIPT_DIR%\aiworkflow-trigger"
set "PROJECT_SEARCH=%SCRIPT_DIR%"
set "PROJECT_CODEX_DIR="
set "USER_CODEX_DIR=%USERPROFILE%\.codex"

echo AIWorkflow skill installer
echo.

if not exist "%SOURCE_DIR%\SKILL.md" (
  echo [error] Skill source not found:
  echo %SOURCE_DIR%\SKILL.md
  echo.
  pause
  exit /b 1
)

:search
if exist "%PROJECT_SEARCH%\.codex\" (
  set "PROJECT_CODEX_DIR=%PROJECT_SEARCH%\.codex"
  goto choose_target
)

for %%I in ("%PROJECT_SEARCH%\..") do set "NEXT=%%~fI"
if /I "%NEXT%"=="%PROJECT_SEARCH%" goto choose_target
set "PROJECT_SEARCH=%NEXT%"
goto search

:choose_target
if defined PROJECT_CODEX_DIR (
  set "TARGET_SKILLS_DIR=%PROJECT_CODEX_DIR%\skills"
  set "TARGET_KIND=project"
  goto install
)

if exist "%USER_CODEX_DIR%\" (
  set "TARGET_SKILLS_DIR=%USER_CODEX_DIR%\skills"
  set "TARGET_KIND=user"
  goto install
)

echo [error] Could not find project .codex or user .codex.
echo Project search started from:
echo %SCRIPT_DIR%
echo.
echo Expected one of:
echo ^<project^>\.codex
echo %USER_CODEX_DIR%
echo.
pause
exit /b 1

:install
set "TARGET_DIR=%TARGET_SKILLS_DIR%\aiworkflow-trigger"
echo Source:
echo %SOURCE_DIR%
echo.
echo Target [%TARGET_KIND%]:
echo %TARGET_DIR%
echo.

if not exist "%TARGET_SKILLS_DIR%\" mkdir "%TARGET_SKILLS_DIR%"
if exist "%TARGET_DIR%\" (
  echo Existing target found. Updating files...
) else (
  echo Installing new skill...
)

xcopy /E /I /Y "%SOURCE_DIR%" "%TARGET_DIR%"
if errorlevel 1 (
  echo.
  echo [error] Skill install failed.
  pause
  exit /b 1
)

echo.
echo [success] AIWorkflow skill installed.
echo Skill file:
echo %TARGET_DIR%\SKILL.md
echo.
pause
exit /b 0
