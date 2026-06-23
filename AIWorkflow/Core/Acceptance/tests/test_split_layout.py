import subprocess
import sys
import tempfile
import unittest
import shutil
import zipfile
import json
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[5]
RUNNER = PROJECT_ROOT / "ProjectHelp/AIWorkflow/Core/Acceptance/acceptance_runner.py"
AIWORKFLOW_ROOT = PROJECT_ROOT / "ProjectHelp/AIWorkflow"


class SplitLayoutTests(unittest.TestCase):
    def run_runner(self, *args):
        return subprocess.run(
            [sys.executable, str(RUNNER), *args],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

    def load_runner_module(self):
        spec = importlib.util.spec_from_file_location("acceptance_runner_for_test", RUNNER)
        module = importlib.util.module_from_spec(spec)
        original_path = list(sys.path)
        sys.path.insert(0, str(RUNNER.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path[:] = original_path
        return module

    def test_core_workspace_adapter_layout_exists(self):
        self.assertTrue((AIWORKFLOW_ROOT / "Core/Acceptance").is_dir())
        self.assertTrue((AIWORKFLOW_ROOT / "Workspace/Current.json").is_file())
        self.assertTrue((AIWORKFLOW_ROOT / "Workspace/Topics").is_dir())
        self.assertTrue((AIWORKFLOW_ROOT / "Adapters/acceptance_registry.py").is_file())
        self.assertTrue((AIWORKFLOW_ROOT / "Adapters/checks").is_dir())
        self.assertTrue((AIWORKFLOW_ROOT / "Adapters/drivers").is_dir())
        self.assertFalse((AIWORKFLOW_ROOT / "Adapters/CoreProjectUnity").exists())
        self.assertTrue((AIWORKFLOW_ROOT / "Modes/Common").is_dir())
        self.assertTrue((AIWORKFLOW_ROOT / "Modes/CoreProjectUnity").is_dir())

    def test_runtime_artifacts_are_not_inside_core(self):
        self.assertFalse((AIWORKFLOW_ROOT / "Core/Acceptance/Temp").exists())
        self.assertFalse((AIWORKFLOW_ROOT / "Core/Acceptance/Local").exists())
        self.assertTrue((AIWORKFLOW_ROOT / "Workspace/Temp").is_dir())
        self.assertTrue((AIWORKFLOW_ROOT / "Workspace/Local").is_dir())

    def test_runner_validates_current_from_workspace(self):
        result = self.run_runner("validate-current")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Current.json valid.", result.stdout)

    def test_runner_policy_commands_manage_aitdd_switch(self):
        show = self.run_runner("policy", "show")
        self.assertEqual(show.returncode, 0, show.stderr + show.stdout)
        policy = json.loads(show.stdout)
        self.assertEqual(policy["defaultMode"], "enabled")
        self.assertEqual(policy["formalRunPolicy"], "explicit")
        self.assertEqual(policy["templateWorkspacePolicy"], "smoke-only")

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            standalone_root = project_root / "AIWorkflow"
            shutil.copytree(AIWORKFLOW_ROOT / "Core", standalone_root / "Core")
            shutil.copytree(AIWORKFLOW_ROOT / "Workspace.Template", standalone_root / "Workspace")
            runner = standalone_root / "Core/Acceptance/acceptance_runner.py"

            set_result = subprocess.run(
                [sys.executable, str(runner), "policy", "set", "--default-mode", "manual"],
                cwd=standalone_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(set_result.returncode, 0, set_result.stderr + set_result.stdout)
            updated = json.loads((standalone_root / "Workspace/AITDDPolicy.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(updated["defaultMode"], "manual")

    def test_aiworkflow_current_check_uses_workspace_default(self):
        sys.path.insert(0, str(AIWORKFLOW_ROOT / "Core/Acceptance"))
        from checks.aiworkflow.context_checks import current_json_valid

        result = current_json_valid(PROJECT_ROOT, {})
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["details"]["path"], "Workspace/Current.json")

    def test_runner_validates_resolution_and_iteration(self):
        resolution = self.run_runner("validate-resolution")
        self.assertEqual(resolution.returncode, 0, resolution.stderr + resolution.stdout)
        iteration = self.run_runner("validate-iteration")
        self.assertEqual(iteration.returncode, 0, iteration.stderr + iteration.stdout)

    def test_runner_dry_run_resolves_multiple_modes(self):
        result = self.run_runner("run", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)

        self.assertEqual(
            data["modes"],
            [
                "aiworkflow_portable_core_release",
                "temp.aiworkflow_portable_core_split_iteration",
            ],
        )
        self.assertIn("modeSnapshots", data)
        self.assertEqual(len(data["modeSnapshots"]), 2)
        self.assertNotIn("mode", data)
        self.assertNotIn("originalMode", data)
        self.assertNotIn("modeOverridden", data)

    def test_runner_rejects_legacy_acceptance_mode(self):
        module = self.load_runner_module()
        with self.assertRaisesRegex(ValueError, "acceptance.mode is no longer supported"):
            module._validate_acceptance({"mode": "aiworkflow_minimal", "extraChecks": []})

    def test_required_evidence_gate_blocks_missing_declared_behavior_evidence(self):
        module = self.load_runner_module()
        checks = [
            {
                "id": "common.content.contains",
                "name": "静态结构检查",
                "severity": "required",
                "params": {
                    "path": "src/unit.py",
                    "text": "expected_symbol",
                },
            }
        ]

        findings = module._audit_required_evidence(checks, ["contract", "behavior"])

        self.assertTrue(
            any(item["id"] == "aiworkflow.acceptance.required_evidence" for item in findings),
            findings,
        )

    def test_required_evidence_gate_accepts_declared_behavior_driver_artifact(self):
        module = self.load_runner_module()
        checks = [
            {
                "id": "common.json.field_matches",
                "name": "driver 产物字段匹配",
                "severity": "required",
                "acceptanceType": "behavior",
                "params": {
                    "path": "Workspace/Temp/BehaviorResult.json",
                    "field": "status",
                    "pattern": "^pass$",
                    "driver": "Adapters/drivers/run_behavior.py",
                },
            }
        ]

        findings = module._audit_required_evidence(checks, ["behavior"])

        self.assertFalse(
            any(item["id"] == "aiworkflow.acceptance.required_evidence" for item in findings),
            findings,
        )

    def test_core_required_evidence_gate_is_not_keyword_based(self):
        module = self.load_runner_module()
        runner = (AIWORKFLOW_ROOT / "Core/Acceptance/acceptance_runner.py").read_text(encoding="utf-8-sig")
        check_driver_mode = (AIWORKFLOW_ROOT / "Core/docs/check-driver-mode.md").read_text(encoding="utf-8-sig")
        skill = (AIWORKFLOW_ROOT / "Skill.Template/aiworkflow-trigger/SKILL.md").read_text(encoding="utf-8-sig")

        findings = module._audit_required_evidence([], [])

        self.assertEqual(findings, [])
        self.assertNotIn("_requires_behavior_driver", runner)
        self.assertNotIn("服务端收到", runner + check_driver_mode + skill)
        self.assertNotIn("A 做操作 B", runner + check_driver_mode + skill)
        self.assertNotIn("新名字", runner + check_driver_mode + skill)
        self.assertNotIn("跨客户端或跨会话", runner + check_driver_mode + skill)

    def test_registry_discovers_core_and_adapter_modes(self):
        result = self.run_runner("list-modes")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("ai_workflow_design", result.stdout)
        self.assertIn("aiworkflow_minimal", result.stdout)
        self.assertIn("aiworkflow_portable_core_release", result.stdout)
        self.assertIn("temp.lua_ui_management_prefab_dependency_design", result.stdout)

    def test_adapters_only_contain_checks_and_drivers(self):
        adapter_root = AIWORKFLOW_ROOT / "Adapters"
        entries = {path.name for path in adapter_root.iterdir() if path.is_dir() and path.name != "__pycache__"}
        self.assertEqual(entries, {"checks", "drivers"})

    def test_project_modes_live_outside_adapters(self):
        mode_root = AIWORKFLOW_ROOT / "Modes/CoreProjectUnity"
        self.assertTrue((mode_root / "lua_module_system.py").is_file())
        self.assertTrue((mode_root / "lua_naming_rules.py").is_file())
        self.assertTrue((mode_root / "temp/lua_ui_management_prefab_dependency_design.py").is_file())
        self.assertFalse(any((mode_root / "temp").glob("aiworkflow*.py")))

    def test_common_modes_live_outside_project_modes(self):
        common_root = AIWORKFLOW_ROOT / "Modes/Common"
        self.assertTrue((common_root / "temp/aiworkflow_semantic_gate_audit.py").is_file())
        self.assertTrue((common_root / "temp/aiworkflow_technology_neutral_acceptance.py").is_file())

    def test_mode_files_do_not_reference_other_modes(self):
        mode_files = [
            path
            for root in [AIWORKFLOW_ROOT / "Core/Acceptance/modes", AIWORKFLOW_ROOT / "Modes"]
            for path in root.rglob("*.py")
            if "__pycache__" not in path.parts and path.name != "__init__.py"
        ]
        forbidden_fragments = [
            "from modes",
            "import modes",
            "from Modes",
            "import Modes",
            "BASE_MODE",
        ]
        for path in mode_files:
            text = path.read_text(encoding="utf-8-sig")
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, text, path)

    def test_registry_discovers_core_and_adapter_checks(self):
        result = self.run_runner("list-checks")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("common.file.exists", result.stdout)
        self.assertIn("unity.editor.execution_report_passed", result.stdout)
        self.assertIn("project.resource.build_pipeline_dry_run_passed", result.stdout)

    def test_core_registry_keeps_adapter_checks_out_of_core_table(self):
        registry = (AIWORKFLOW_ROOT / "Core/Acceptance/acceptance_registry.py").read_text(encoding="utf-8-sig")
        self.assertNotIn('"project.', registry)
        self.assertNotIn('"unity.', registry)
        adapter_registry = AIWORKFLOW_ROOT / "Adapters/acceptance_registry.py"
        self.assertTrue(adapter_registry.is_file())

    def test_latest_uses_workspace_latest_run(self):
        result = self.run_runner("latest")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("# 最近一次验收", result.stdout)

    def test_top_readme_is_open_source_entry(self):
        readme = (AIWORKFLOW_ROOT / "README.md").read_text(encoding="utf-8-sig")

        self.assertIn("AI 交付可复验的验收证据", readme)
        self.assertIn("Topic / Issue / Resolution / Iteration / Run", readme)
        self.assertIn("AcceptanceReport.md", readme)
        self.assertIn("Result.json", readme)
        self.assertIn("Run.log", readme)
        self.assertIn("## 核心理念", readme)
        self.assertIn("## 安装", readme)
        self.assertIn("## 开始真实任务", readme)
        self.assertIn("## 文档", readme)
        self.assertIn("## 进一步了解", readme)
        self.assertLess(readme.index("## 核心理念"), readme.index("## 安装"))
        self.assertLess(readme.index("## 安装"), readme.index("## 文档"))
        self.assertLess(readme.index("## 文档"), readme.index("## 进一步了解"))
        core_idea = readme[readme.index("## 核心理念"):readme.index("## 安装")]
        self.assertIn("长期保持", core_idea)
        self.assertIn("不断进化", core_idea)
        self.assertIn("可复验的证据、决策、上下文和运行结果", core_idea)
        self.assertIn("事实验证进入 `check`", core_idea)
        self.assertIn("流程执行进入 `driver`", core_idea)
        self.assertIn("验收组合进入 `mode`", core_idea)
        self.assertNotIn("没有工作流时", core_idea)
        self.assertNotIn("这次变更属于哪个问题", core_idea)
        self.assertIn("让 AI 的工作留下验收证据", readme)
        self.assertIn("让项目逐步沉淀验收能力", readme)
        self.assertIn("事实验证写成 `check`", readme)
        self.assertIn("流程执行写成 `driver`", readme)
        self.assertIn("本次组合写成 `temp mode`", readme)
        self.assertIn("`check / driver / mode` 三层能力", readme)
        self.assertIn("区分静态契约和真实行为证据", readme)
        self.assertIn("拆分事实、流程和验收配方", readme)
        self.assertIn("保持可迁移，不绑定具体项目", readme)
        self.assertIn("降低 AI 丢上下文的风险", readme)
        self.assertIn("支持开源协作和团队协作", readme)
        self.assertNotIn("核心卖点", readme)
        self.assertNotIn("## 补充说明", readme)
        self.assertNotIn("## 发布包结构", readme)
        self.assertNotIn("## 安装 Codex Skill", readme)
        self.assertNotIn("解压发布包", readme)
        self.assertIn("本文件位于 `AIWorkflow/README.md`", readme)
        self.assertIn("YourProject/", readme)
        self.assertIn("AIWorkflow-Repo/", readme)
        self.assertIn("目标项目最终必须存在", readme)
        self.assertIn(".codex/skills/aiworkflow-trigger/SKILL.md", readme)
        self.assertNotIn("GitHub 仓库的根目录就是 AIWorkflow 的源码内容", readme)
        self.assertNotIn("git clone <AIWorkflow 仓库地址> AIWorkflow", readme)
        self.assertIn("temp mode", readme)
        self.assertIn("contract / behavior / browser", readme)
        self.assertIn("Current.json", readme)
        self.assertIn("Resolution.json", readme)
        self.assertIn("LatestRun.md", readme)
        self.assertIn("run --template-smoke", readme)
        self.assertIn("真实任务验收", readme)
        self.assertIn("Workspace.Template", readme)
        self.assertIn("Skill.Template/README.md", readme)
        self.assertIn("Core/docs/data-model.md", readme)
        self.assertIn("Core/docs/check-driver-mode.md", readme)
        self.assertIn("Core/docs/setup.md", readme)
        self.assertNotIn("AI coding is fast", readme)
        self.assertNotIn("What You Get", readme)
        self.assertNotIn("Core Idea", readme)
        self.assertNotIn("ProjectHelp/AIWorkflow/", readme)
        self.assertNotIn("ProjectHelp\\AIWorkflow\\", readme)
        self.assertNotIn("## Check 原子性规则", readme)
        self.assertNotIn("## Driver 职责规则", readme)
        self.assertNotIn("## Mode 职责规则", readme)

    def test_core_readme_documents_split_layout(self):
        readme = (AIWORKFLOW_ROOT / "Core/README.md").read_text(encoding="utf-8-sig")
        self.assertIn("Core", readme)
        self.assertIn("Workspace", readme)
        self.assertIn("Adapters", readme)
        self.assertIn("Core/Acceptance", readme)
        self.assertIn("Workspace/Current.json", readme)
        self.assertIn("AIWorkflow 相对路径", readme)
        self.assertIn("Core/docs/architecture.md", readme)
        self.assertIn("Core/docs/path-rules.md", readme)
        self.assertIn("Core/docs/data-model.md", readme)
        self.assertIn("Core/docs/runner.md", readme)
        self.assertIn("Core/docs/check-driver-mode.md", readme)
        self.assertIn("Core/docs/extension-boundary.md", readme)
        self.assertIn("Core/docs/setup.md", readme)
        self.assertLessEqual(len(readme.splitlines()), 180)
        self.assertNotIn("ProjectHelp/AIWorkflow/", readme)
        self.assertNotIn("ProjectHelp\\AIWorkflow\\", readme)
        self.assertNotIn("用于保存 CoreProject 的 AI-TDD 通用验收框架", readme)
        historical_terms = [
            "改造后的",
            "旧版说明",
            "迁移前后",
            "用于对比",
        ]
        for term in historical_terms:
            self.assertNotIn(term, readme)

    def test_core_readme_is_navigation_not_rule_body(self):
        readme = (AIWORKFLOW_ROOT / "Core/README.md").read_text(encoding="utf-8-sig")
        self.assertIn("## 必读文档", readme)
        self.assertIn("Core/docs/setup.md", readme)
        rule_headings = [
            "## Check 原子性规则",
            "## Driver 职责规则",
            "## Mode 职责规则",
            "## 新项目初始化",
            "## Resolution.json",
            "## Runner 命令",
        ]
        for heading in rule_headings:
            self.assertNotIn(heading, readme)

    def test_core_docs_preserve_responsibilities_and_authority(self):
        docs = {
            "architecture": AIWORKFLOW_ROOT / "Core/docs/architecture.md",
            "path_rules": AIWORKFLOW_ROOT / "Core/docs/path-rules.md",
            "data_model": AIWORKFLOW_ROOT / "Core/docs/data-model.md",
            "runner": AIWORKFLOW_ROOT / "Core/docs/runner.md",
            "check_driver_mode": AIWORKFLOW_ROOT / "Core/docs/check-driver-mode.md",
            "extension_boundary": AIWORKFLOW_ROOT / "Core/docs/extension-boundary.md",
            "setup": AIWORKFLOW_ROOT / "Core/docs/setup.md",
        }
        for path in docs.values():
            self.assertTrue(path.is_file(), path)
            text = path.read_text(encoding="utf-8-sig")
            self.assertIn("## 本文职责", text)
            self.assertIn("## 权限边界", text)
            self.assertNotIn("ProjectHelp/AIWorkflow/", text)
            self.assertNotIn("ProjectHelp\\AIWorkflow\\", text)

        architecture = docs["architecture"].read_text(encoding="utf-8-sig")
        path_rules = docs["path_rules"].read_text(encoding="utf-8-sig")
        data_model = docs["data_model"].read_text(encoding="utf-8-sig")
        runner = docs["runner"].read_text(encoding="utf-8-sig")
        check_driver_mode = docs["check_driver_mode"].read_text(encoding="utf-8-sig")
        extension_boundary = docs["extension_boundary"].read_text(encoding="utf-8-sig")
        setup = docs["setup"].read_text(encoding="utf-8-sig")

        self.assertIn("Core/Acceptance", architecture)
        self.assertIn("Workspace.Template/", architecture)
        self.assertIn("AIWorkflow 相对路径", path_rules)
        self.assertIn("Workspace/Current.json", path_rules)
        self.assertIn("Workspace/AITDDPolicy.json", path_rules)
        self.assertIn("源码仓库只保留模板", (AIWORKFLOW_ROOT / "Core/README.md").read_text(encoding="utf-8-sig"))
        self.assertIn("将开源仓库中的 `AIWorkflow/` 目录复制到目标项目根目录", setup)
        self.assertIn("`.codex/` 同时复制到目标项目根目录", setup)
        self.assertIn("从 `Workspace.Template/` 创建新的 `Workspace/`", setup)
        self.assertIn("AITDDPolicy.json", setup)
        self.assertIn("policy show", runner)
        self.assertIn("policy set --default-mode enabled", runner)
        self.assertIn("validate-current` 也会验证 `Workspace/AITDDPolicy.json`", runner)
        self.assertIn("由模板创建的 `Workspace/` 默认 `source` 是 `TEMPLATE`", setup)
        self.assertIn("`Workspace/` 属于宿主项目过程资产", path_rules)
        self.assertNotIn("解压发布包", setup)
        self.assertNotIn("发布包已直接提供", setup)
        self.assertNotIn("发布包直接提供", path_rules)
        self.assertIn("Topic -> Issue -> Resolution -> Iteration -> Run", data_model)
        self.assertIn("Workspace/LatestRun.md", data_model)
        self.assertIn('"requiredEvidence": [', data_model)
        self.assertIn('"contract",', data_model)
        self.assertIn('"behavior"', data_model)
        self.assertIn('"acceptanceType": "behavior"', data_model)
        self.assertIn('"driver": "Adapters/drivers/run_behavior.py"', data_model)
        self.assertIn("Workspace/Temp/BehaviorResult.json", data_model)
        self.assertIn("--template-smoke", runner)
        self.assertIn("blocked", runner)
        self.assertIn("acceptance.modes", runner)
        self.assertNotIn("--mode <mode_name>", runner)
        self.assertIn("Check 原子性规则", check_driver_mode)
        self.assertIn("Driver 职责规则", check_driver_mode)
        self.assertIn("Mode 职责规则", check_driver_mode)
        self.assertIn("Driver 不直接代表最终验收结论", check_driver_mode)
        self.assertIn("证据覆盖规则", check_driver_mode)
        self.assertIn("Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求", check_driver_mode)
        self.assertIn("报告必须区分 `contract`、`behavior` 和 `browser` 验收类型", check_driver_mode)
        self.assertIn("acceptance.requiredEvidence", check_driver_mode)
        self.assertIn("Core 只能描述通用流程", extension_boundary)
        self.assertIn("Adapters/ 只保存项目或技术栈适配能力", extension_boundary)
        self.assertIn("新项目初始化", setup)
        self.assertIn("aiworkflow_minimal", setup)

    def test_core_docs_do_not_mix_responsibilities(self):
        docs = {
            "architecture": (AIWORKFLOW_ROOT / "Core/docs/architecture.md").read_text(encoding="utf-8-sig"),
            "path_rules": (AIWORKFLOW_ROOT / "Core/docs/path-rules.md").read_text(encoding="utf-8-sig"),
            "data_model": (AIWORKFLOW_ROOT / "Core/docs/data-model.md").read_text(encoding="utf-8-sig"),
            "runner": (AIWORKFLOW_ROOT / "Core/docs/runner.md").read_text(encoding="utf-8-sig"),
            "check_driver_mode": (AIWORKFLOW_ROOT / "Core/docs/check-driver-mode.md").read_text(encoding="utf-8-sig"),
            "extension_boundary": (AIWORKFLOW_ROOT / "Core/docs/extension-boundary.md").read_text(encoding="utf-8-sig"),
            "setup": (AIWORKFLOW_ROOT / "Core/docs/setup.md").read_text(encoding="utf-8-sig"),
        }
        self.assertNotIn("## Check 原子性规则", docs["runner"])
        self.assertNotIn("## Driver 职责规则", docs["setup"])
        self.assertNotIn("## 新项目初始化", docs["check_driver_mode"])
        self.assertNotIn("run --template-smoke", docs["path_rules"])
        self.assertNotIn("Topic -> Issue -> Resolution -> Iteration -> Run", docs["runner"])
        self.assertNotIn("Workspace.Template/Current.json", docs["check_driver_mode"])
        self.assertNotIn("validate-current", docs["extension_boundary"])
        self.assertNotIn("acceptance.mode` 指向", docs["data_model"])

    def test_current_resolution_iteration_pointer_is_closed(self):
        current = json.loads((AIWORKFLOW_ROOT / "Workspace/Current.json").read_text(encoding="utf-8-sig"))
        resolution_path = AIWORKFLOW_ROOT / current["resolutionPath"]
        iteration_path = AIWORKFLOW_ROOT / current["iterationPath"]
        resolution = json.loads(resolution_path.read_text(encoding="utf-8-sig"))
        current_iteration = next(
            item for item in resolution["iterations"]
            if item["version"] == current["currentIteration"]
        )

        self.assertEqual(current["issue"], resolution["issue"])
        self.assertEqual(current["currentIteration"], resolution["currentIteration"])
        self.assertEqual(current_iteration["detailPath"], current["iterationPath"])
        self.assertTrue(iteration_path.is_file())

    def test_workspace_current_paths_point_to_workspace(self):
        current = (AIWORKFLOW_ROOT / "Workspace/Current.json").read_text(encoding="utf-8-sig")
        self.assertIn('"topicPath": "Workspace/Topics/AITDDWorkflow"', current)
        self.assertNotIn("ProjectHelp/AIWorkflow/", current)

    def test_runner_latest_uses_aiworkflow_relative_paths(self):
        result = self.run_runner("latest")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Report：Workspace/Topics/", result.stdout)
        self.assertNotIn("ProjectHelp/AIWorkflow/", result.stdout)

    def test_adapter_paths_use_workspace_locations(self):
        adapter_root = AIWORKFLOW_ROOT / "Adapters"
        scanned = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for path in adapter_root.rglob("*.py")
            if "__pycache__" not in path.parts
        )
        self.assertNotIn("ProjectHelp/AIWorkflow/Current.json", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Topics/", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Acceptance/Temp", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Acceptance/Local", scanned)
        self.assertIn("ProjectHelp/AIWorkflow/Workspace/Temp", scanned)

    def test_modes_use_workspace_locations(self):
        mode_root = AIWORKFLOW_ROOT / "Modes"
        scanned = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for path in mode_root.rglob("*.py")
            if "__pycache__" not in path.parts
        )
        self.assertNotIn("ProjectHelp/AIWorkflow/Current.json", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Topics/", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Acceptance/Temp", scanned)
        self.assertNotIn("ProjectHelp/AIWorkflow/Acceptance/Local", scanned)
        self.assertIn("ProjectHelp/AIWorkflow/Workspace/Current.json", scanned)

    def test_core_paths_do_not_reference_old_layout(self):
        core_root = AIWORKFLOW_ROOT / "Core"
        scanned = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for pattern in ("*.py", "*.md")
            for path in core_root.rglob(pattern)
            if "__pycache__" not in path.parts and "tests" not in path.parts and path.name != "README.old.md"
        )
        old_paths = [
            "ProjectHelp/AIWorkflow/Current.json",
            "ProjectHelp/AIWorkflow/Topics/",
            "ProjectHelp/AIWorkflow/ProjectContext.md",
            "ProjectHelp/AIWorkflow/LatestRun.md",
            "ProjectHelp/AIWorkflow/Acceptance/Temp",
            "ProjectHelp/AIWorkflow/Acceptance/Local",
            "ProjectHelp/AIWorkflow/Acceptance/drivers",
            "ProjectHelp/AIWorkflow/Acceptance/checks",
            "\"Acceptance/Temp/",
            "\"Acceptance/Local/",
            "`Acceptance/Temp/",
            "下的 `Acceptance/Temp/",
        ]
        for old_path in old_paths:
            self.assertNotIn(old_path, scanned)

    def test_core_production_files_are_project_neutral(self):
        core_root = AIWORKFLOW_ROOT / "Core"
        scanned = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for pattern in ("*.py", "*.md")
            for path in core_root.rglob(pattern)
            if "__pycache__" not in path.parts and "tests" not in path.parts and path.name != "README.old.md"
        )
        forbidden_terms = [
            "CoreProject",
            "XLua",
            "Assets/",
            "LuaFramework",
            "MuMu",
            "Addressables",
            "AssetBundle",
        ]
        for term in forbidden_terms:
            self.assertNotIn(term, scanned)

    def test_extension_boundary_states_positive_project_detail_rule(self):
        boundary = (AIWORKFLOW_ROOT / "Core/docs/extension-boundary.md").read_text(encoding="utf-8-sig")
        self.assertIn("项目细节必须进入 `Adapters/`、`Modes/` 或宿主项目规则", boundary)
        self.assertIn("Adapter 不应包含 mode", boundary)
        self.assertIn("Mode 不应包含环境准备、服务启动、登录、数据注入或连续请求流程", boundary)

    def test_modes_do_not_execute_driver_processes_directly(self):
        mode_root = AIWORKFLOW_ROOT / "Modes"
        scanned = "\n".join(
            path.read_text(encoding="utf-8-sig", errors="replace")
            for path in mode_root.rglob("*.py")
            if "__pycache__" not in path.parts
        )
        forbidden_fragments = [
            "subprocess.",
            "requests.",
            "urllib.request",
            "socket.",
            "Start-Process",
        ]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, scanned)

    def test_open_source_file_list_exists(self):
        checklist = AIWORKFLOW_ROOT / "Core/OPEN_SOURCE.md"
        text = checklist.read_text(encoding="utf-8-sig")
        self.assertIn("开源文件清单", text)
        self.assertIn("Core/", text)
        self.assertIn("Core/docs/", text)
        self.assertIn("Workspace.Template/", text)
        self.assertIn("Adapters/", text)

    def test_workspace_template_exists(self):
        template_root = AIWORKFLOW_ROOT / "Workspace.Template"
        self.assertTrue((template_root / "Current.json").is_file())
        self.assertTrue((template_root / "AITDDPolicy.json").is_file())
        self.assertTrue((template_root / "LatestRun.md").is_file())
        self.assertTrue((template_root / "ProjectContext.md").is_file())
        self.assertTrue((template_root / "README.md").is_file())
        self.assertTrue((template_root / "Topics/.gitkeep").is_file())
        self.assertTrue((template_root / "Temp/.gitkeep").is_file())
        self.assertTrue((template_root / "Local/.gitkeep").is_file())
        self.assertTrue((template_root / "Topics/ExampleTopic/Issues/ExampleIssue/Issue.md").is_file())
        self.assertTrue((template_root / "Topics/ExampleTopic/Issues/ExampleIssue/Decision.md").is_file())
        self.assertTrue((template_root / "Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Resolution.json").is_file())
        self.assertTrue((template_root / "Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Iterations/v0.1.0.md").is_file())

        current = (template_root / "Current.json").read_text(encoding="utf-8-sig")
        self.assertIn('"topic": "ExampleTopic"', current)
        self.assertIn('"topicPath": "Workspace/Topics/ExampleTopic"', current)
        self.assertIn('"source": "TEMPLATE"', current)
        self.assertNotIn("ProjectHelp/AIWorkflow/", current)

        policy = json.loads((template_root / "AITDDPolicy.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(policy["defaultMode"], "enabled")
        self.assertEqual(policy["formalRunPolicy"], "explicit")
        self.assertEqual(policy["templateWorkspacePolicy"], "smoke-only")
        self.assertIn("AI 必须读取本文件", "\n".join(policy["notes"]))

        resolution = (template_root / "Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Resolution.json").read_text(encoding="utf-8-sig")
        self.assertIn('"modes": [', resolution)
        self.assertIn('"aiworkflow_minimal"', resolution)
        self.assertIn('"requiredEvidence": [', resolution)
        self.assertIn('"contract"', resolution)
        self.assertNotIn('"mode":', resolution)
        self.assertNotIn("ProjectHelp/AIWorkflow/", resolution)

    def test_skill_template_is_installable_and_project_neutral(self):
        skill_root = AIWORKFLOW_ROOT / "Skill.Template/aiworkflow-trigger"
        self.assertTrue((skill_root / "SKILL.md").is_file())
        self.assertTrue((AIWORKFLOW_ROOT / "Skill.Template/find_codex_skills.bat").is_file())
        self.assertTrue((AIWORKFLOW_ROOT / "Skill.Template/find_codex_skills.sh").is_file())
        readme = (AIWORKFLOW_ROOT / "Skill.Template/README.md").read_text(encoding="utf-8-sig")
        bat = (AIWORKFLOW_ROOT / "Skill.Template/find_codex_skills.bat").read_text(encoding="utf-8-sig")
        shell = (AIWORKFLOW_ROOT / "Skill.Template/find_codex_skills.sh").read_text(encoding="utf-8-sig")
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8-sig")

        self.assertIn("find_codex_skills.bat", readme)
        self.assertIn("find_codex_skills.sh", readme)
        self.assertIn("Windows", readme)
        self.assertIn("Linux", readme)
        self.assertIn("macOS", readme)
        self.assertIn(".codex/skills/aiworkflow-trigger/", readme)
        self.assertIn("%USERPROFILE%/.codex/skills/aiworkflow-trigger/", readme)
        self.assertIn("~/.codex/skills/aiworkflow-trigger/", readme)
        self.assertIn(".codex", bat)
        self.assertIn("skills", bat)
        self.assertIn("xcopy", bat)
        self.assertIn("%~dp0", bat)
        self.assertIn("pause", bat)
        self.assertIn("TARGET_KIND=project", bat)
        self.assertIn("TARGET_KIND=user", bat)
        self.assertIn("Target [%TARGET_KIND%]", bat)
        self.assertIn("%USERPROFILE%\\.codex", bat)
        self.assertIn(".codex", shell)
        self.assertIn("skills", shell)
        self.assertIn("cp -R", shell)
        self.assertIn("TARGET_KIND=\"project\"", shell)
        self.assertIn("TARGET_KIND=\"user\"", shell)
        self.assertIn("${HOME}/.codex", shell)
        self.assertIn("AIWorkflow/Core/Acceptance/acceptance_runner.py", readme)
        self.assertIn("AITDDPolicy.json", readme)
        self.assertIn("policy show", readme)
        self.assertIn("policy set --default-mode enabled", readme)
        self.assertIn("AIWorkflow/Workspace/Current.json", skill)
        self.assertIn("AIWorkflow/Workspace/AITDDPolicy.json", skill)
        self.assertIn("defaultMode: \"enabled\"", skill)
        self.assertIn("defaultMode: \"manual\"", skill)
        self.assertIn("defaultMode: \"off\"", skill)
        self.assertIn("AI 必须读取本文件后执行策略", skill)
        self.assertIn("不要让 AI 自行猜测是否启用 AIWorkflow", skill)
        self.assertIn("Core/docs/architecture.md", skill)
        self.assertIn("Core/docs/check-driver-mode.md", skill)
        self.assertIn("Core/docs/path-rules.md", skill)
        self.assertIn("Core/docs/data-model.md", skill)
        self.assertIn("Core/docs/runner.md", skill)
        self.assertIn("Core/docs/extension-boundary.md", skill)
        self.assertIn("Core/docs/setup.md", skill)
        self.assertIn("acceptance_runner.py validate-current", skill)
        self.assertIn("最终回复必须包含验收结果", skill)
        self.assertIn("TEMPLATE", skill)
        self.assertNotIn("CoreProject", readme + skill + bat + shell)
        self.assertNotIn("ProjectHelp/AIWorkflow", readme + skill + bat + shell)

    def test_checkpoint_cleanup_notes_are_recorded(self):
        iteration = (
            AIWORKFLOW_ROOT
            / "Workspace/Topics/AITDDWorkflow/Issues/AIWorkflowPortableCoreSplit/Resolution/Iterations/v0.1.0.md"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("## 检查点整理", iteration)
        self.assertIn("README 内容检查迁移到 Core/docs", iteration)
        self.assertIn("Current / Resolution / Iteration 指针闭环", iteration)
        self.assertIn("Workspace.Template 结构完整与模板误用防护分层", iteration)

    def test_resolution_acceptance_uses_modes_list(self):
        mode = (AIWORKFLOW_ROOT / "Core/Acceptance/modes/aiworkflow_portable_core_release.py").read_text(encoding="utf-8-sig")
        temp_mode = (AIWORKFLOW_ROOT / "Core/Acceptance/modes/temp/aiworkflow_portable_core_split_iteration.py").read_text(encoding="utf-8-sig")
        resolution = json.loads(
            (
                AIWORKFLOW_ROOT
                / "Workspace/Topics/AITDDWorkflow/Issues/AIWorkflowPortableCoreSplit/Resolution/Resolution.json"
            ).read_text(encoding="utf-8-sig")
        )
        iteration = resolution["iterations"][0]
        acceptance = iteration["acceptance"]
        extra_checks = iteration["acceptance"].get("extraChecks", [])

        self.assertIn('"id": "aiworkflow_portable_core_release"', mode)
        self.assertIn('"id": "temp.aiworkflow_portable_core_split_iteration"', temp_mode)
        self.assertIn("Workspace 模板 AITDDPolicy 存在", mode)
        self.assertIn("AITDDPolicy.json", mode)
        self.assertIn("Core docs 架构文档存在", mode)
        self.assertIn("Workspace 模板标记为 TEMPLATE", mode)
        self.assertIn("Skill 导航 Core docs", mode)
        self.assertNotIn("mode", acceptance)
        self.assertEqual(acceptance["requiredEvidence"], ["contract"])
        self.assertEqual(
            acceptance["modes"],
            [
                "aiworkflow_portable_core_release",
                "temp.aiworkflow_portable_core_split_iteration",
            ],
        )
        self.assertEqual(extra_checks, [])

    def test_check_semantics_are_documented_as_atomic_and_reusable(self):
        core_readme = (AIWORKFLOW_ROOT / "Core/README.md").read_text(encoding="utf-8-sig")
        check_driver_mode = (AIWORKFLOW_ROOT / "Core/docs/check-driver-mode.md").read_text(encoding="utf-8-sig")
        checks_readme = (AIWORKFLOW_ROOT / "Core/Acceptance/checks/README.md").read_text(encoding="utf-8-sig")
        skill = (AIWORKFLOW_ROOT / "Skill.Template/aiworkflow-trigger/SKILL.md").read_text(encoding="utf-8-sig")
        combined = core_readme + "\n" + check_driver_mode + "\n" + checks_readme + "\n" + skill

        self.assertIn("Core/docs/check-driver-mode.md", core_readme)
        self.assertIn("Check 原子性规则", check_driver_mode)
        self.assertIn("Driver 职责规则", check_driver_mode)
        self.assertIn("Mode 职责规则", check_driver_mode)
        self.assertIn("一个 check 只能验证一种事实", combined)
        self.assertIn("跨环境准备、服务启动、登录、数据注入、连续请求等流程必须放入 driver", combined)
        self.assertIn("Driver 是流程执行和环境适配单元", combined)
        self.assertIn("Driver 不直接代表最终验收结论", combined)
        self.assertIn("证据覆盖规则", combined)
        self.assertIn("acceptance.requiredEvidence", combined)
        self.assertIn("Core runner 不根据自然语言关键词判断需求应该需要哪种证据", combined)
        self.assertIn("Mode 负责组合多个原子 check", combined)
        self.assertIn("Mode 是验收配方", combined)
        self.assertIn("Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求", combined)
        self.assertIn("长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode", combined)
        self.assertIn("Mode 文件本身不引用其他 mode", combined)
        self.assertIn("acceptance.modes", combined)
        self.assertIn("不得把契约检查、环境准备和行为验收塞进同一个 check", checks_readme)

    def test_report_writer_splits_acceptance_types(self):
        report_writer_path = AIWORKFLOW_ROOT / "Core/Acceptance/report_writer.py"
        text = report_writer_path.read_text(encoding="utf-8-sig")

        self.assertIn("## 验收类型", text)
        self.assertIn("Contract acceptance", text)
        self.assertIn("Behavior acceptance", text)
        self.assertIn("Browser/UI acceptance", text)
        self.assertIn("acceptanceType", text)

    def test_python_unittest_check_is_registered(self):
        registry = (AIWORKFLOW_ROOT / "Core/Acceptance/acceptance_registry.py").read_text(encoding="utf-8-sig")
        checks = (AIWORKFLOW_ROOT / "Core/Acceptance/checks/python/compile_checks.py").read_text(encoding="utf-8-sig")
        mode = (AIWORKFLOW_ROOT / "Core/Acceptance/modes/aiworkflow_portable_core_release.py").read_text(encoding="utf-8-sig")

        self.assertIn("python.unittest_passed", registry)
        self.assertIn("def unittest_passed", checks)
        self.assertIn('"id": "python.unittest_passed"', mode)
        self.assertIn("Core Acceptance unittest 通过", mode)

    def test_core_and_workspace_template_are_minimally_runnable_standalone(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            standalone_root = project_root / "AIWorkflow"
            shutil.copytree(AIWORKFLOW_ROOT / "Core", standalone_root / "Core")
            shutil.copytree(AIWORKFLOW_ROOT / "Workspace.Template", standalone_root / "Workspace.Template")
            shutil.copytree(standalone_root / "Workspace.Template", standalone_root / "Workspace")
            runner = standalone_root / "Core/Acceptance/acceptance_runner.py"

            for command in ["validate-current", "validate-resolution", "validate-iteration"]:
                result = subprocess.run(
                    [sys.executable, str(runner), command],
                    cwd=project_root,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            run_result = subprocess.run(
                [sys.executable, str(runner), "run"],
                cwd=project_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(run_result.returncode, 3, run_result.stderr + run_result.stdout)
            self.assertIn("模板工作区只能用于安装烟测", run_result.stdout)

            smoke_result = subprocess.run(
                [sys.executable, str(runner), "run", "--template-smoke"],
                cwd=project_root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            self.assertEqual(smoke_result.returncode, 0, smoke_result.stderr + smoke_result.stdout)

            latest = (standalone_root / "Workspace/LatestRun.md").read_text(encoding="utf-8-sig")
            iteration_text = (standalone_root / "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Iterations/v0.1.0.md").read_text(encoding="utf-8-sig")
            self.assertIn("Status：pass", latest)
            self.assertIn("Report：Workspace/Topics/", latest)
            self.assertIn("- Status：pass", iteration_text)
            self.assertIn("- 结果：pass。", iteration_text)
            self.assertIn("- Run：r001。", iteration_text)
            self.assertIn("AcceptanceReport.md", iteration_text)
            self.assertIn("Result.json", iteration_text)
            self.assertNotIn("待生成", iteration_text)
            self.assertTrue(
                any((standalone_root / "Workspace/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Runs").rglob("AcceptanceReport.md"))
            )

    def test_open_source_folder_contains_workspace_template_not_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "AIWorkflow.OpenSource"
            standalone_root = repo_root / "AIWorkflow"
            shutil.copytree(AIWORKFLOW_ROOT / "Core", standalone_root / "Core")
            shutil.copytree(AIWORKFLOW_ROOT / "Workspace.Template", standalone_root / "Workspace.Template")
            shutil.copytree(AIWORKFLOW_ROOT / "Skill.Template", standalone_root / "Skill.Template")
            shutil.copytree(
                AIWORKFLOW_ROOT / "Skill.Template/aiworkflow-trigger",
                repo_root / ".codex/skills/aiworkflow-trigger",
            )
            shutil.copy2(AIWORKFLOW_ROOT / "README.md", standalone_root / "README.md")
            (repo_root / "README.md").write_text(
                "复制 `AIWorkflow/` 到目标项目根目录；使用 Codex 时复制 `.codex/`。\n",
                encoding="utf-8",
            )

            names = {
                path.relative_to(repo_root).as_posix()
                for path in repo_root.rglob("*")
                if path.is_file()
                and path.relative_to(repo_root).as_posix() not in {
                    "AIWorkflow/Core/OPEN_SOURCE.md",
                    "AIWorkflow/Core/README.old.md",
                }
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            }
            self.assertIn("README.md", names)
            self.assertIn(".codex/skills/aiworkflow-trigger/SKILL.md", names)
            self.assertIn("AIWorkflow/README.md", names)
            self.assertIn("AIWorkflow/Core/docs/check-driver-mode.md", names)
            self.assertIn("AIWorkflow/Workspace.Template/Current.json", names)
            self.assertNotIn("Core/docs/check-driver-mode.md", names)
            self.assertNotIn("Skill.Template/README.md", names)
            self.assertNotIn("AIWorkflow/Workspace/Current.json", names)
            self.assertNotIn("AIWorkflow/Core/README.old.md", names)
            self.assertNotIn("AIWorkflow/Core/OPEN_SOURCE.md", names)


if __name__ == "__main__":
    unittest.main()
