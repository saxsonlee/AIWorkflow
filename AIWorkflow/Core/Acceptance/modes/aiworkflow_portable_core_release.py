MODE = {
    "id": "aiworkflow_portable_core_release",
    "name": "AIWorkflow 可迁移 Core 发布门禁",
    "checks": [
        {
            "id": "aiworkflow.context.current_json_valid",
            "name": "Current.json 有效",
            "severity": "required",
            "params": {},
        },
        {
            "id": "common.json.field_matches",
            "name": "Resolution 指向当前 Issue",
            "severity": "required",
            "params": {
                "path": "${resolution.path}",
                "field": "issue",
                "pattern": "^${issue}$",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Iteration 详情存在",
            "severity": "required",
            "params": {"path": "${iteration.path}"},
        },
        {
            "id": "python.py_compile_passed",
            "name": "Core Acceptance Python 语义编译通过",
            "severity": "required",
            "params": {
                "paths": [
                    "Core/Acceptance/acceptance_runner.py",
                    "Core/Acceptance/acceptance_registry.py",
                    "Core/Acceptance/path_resolver.py",
                    "Core/Acceptance/report_writer.py",
                    "Core/Acceptance/context_reader.py",
                    "Core/Acceptance/archive_manager.py",
                    "Core/Acceptance/modes/aiworkflow_minimal.py",
                    "Core/Acceptance/modes/aiworkflow_portable_core_release.py",
                    "Core/Acceptance/tests/test_split_layout.py",
                ]
            },
        },
        {
            "id": "python.unittest_passed",
            "name": "Core Acceptance unittest 通过",
            "severity": "required",
            "params": {
                "startDirectory": "Core/Acceptance/tests",
                "pattern": "test*.py",
                "timeoutSeconds": 180,
            },
        },
        {
            "id": "common.content.not_contains",
            "name": "Core registry 不硬编码 project checks",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/acceptance_registry.py",
                "text": "\"project.",
            },
        },
        {
            "id": "common.content.not_contains",
            "name": "Core registry 不硬编码 unity checks",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/acceptance_registry.py",
                "text": "\"unity.",
            },
        },
        {
            "id": "common.content.contains",
            "name": "路径解析支持 Modes 前缀",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/path_resolver.py",
                "text": "\"Modes/\"",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Core docs 架构文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/architecture.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs 路径规则文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/path-rules.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs 数据模型文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/data-model.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs runner 文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/runner.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs check driver mode 文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/check-driver-mode.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs 扩展边界文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/extension-boundary.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Core docs 初始化文档存在",
            "severity": "required",
            "params": {"path": "Core/docs/setup.md"},
        },
        {
            "id": "common.content.contains",
            "name": "Core path-rules 说明 AIWorkflow 相对路径规则",
            "severity": "required",
            "params": {
                "path": "Core/docs/path-rules.md",
                "text": "AIWorkflow 相对路径",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core data-model 说明 Workspace Current 路径",
            "severity": "required",
            "params": {
                "path": "Core/docs/data-model.md",
                "text": "Workspace/Current.json",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core data-model 说明 Current 不是归属证明",
            "severity": "required",
            "params": {
                "path": "Core/docs/data-model.md",
                "text": "不作为新请求归属证明",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core runner 支持 AITDD policy 命令",
            "severity": "required",
            "params": {
                "path": "Core/docs/runner.md",
                "text": "policy set --default-mode enabled",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core architecture 说明 Modes 顶层目录",
            "severity": "required",
            "params": {
                "path": "Core/docs/architecture.md",
                "text": "Modes/",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core architecture 说明 Common Modes",
            "severity": "required",
            "params": {
                "path": "Core/docs/architecture.md",
                "text": "Modes/Common/",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core setup 包含新项目初始化章节",
            "severity": "required",
            "params": {
                "path": "Core/docs/setup.md",
                "text": "新项目初始化",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core setup 说明最小自检 mode",
            "severity": "required",
            "params": {
                "path": "Core/docs/setup.md",
                "text": "aiworkflow_minimal",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core runner 说明模板普通 run blocked",
            "severity": "required",
            "params": {
                "path": "Core/docs/runner.md",
                "text": "普通 `run` 会返回 `blocked`",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core runner 说明 template-smoke",
            "severity": "required",
            "params": {
                "path": "Core/docs/runner.md",
                "text": "run --template-smoke",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core extension 边界声明项目细节归属",
            "severity": "required",
            "params": {
                "path": "Core/docs/extension-boundary.md",
                "text": "项目细节必须进入 `Adapters/`、`Modes/` 或宿主项目规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 定义 check 原子性规则",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "Check 原子性规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 定义 Driver 职责规则",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "Driver 职责规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 定义 Mode 职责规则",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "Mode 职责规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 固化长期能力进入 mode",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 定义证据覆盖规则",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "证据覆盖规则",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 说明 requiredEvidence",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "acceptance.requiredEvidence",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 要求报告区分验收类型",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "报告必须区分 `contract`、`behavior` 和 `browser` 验收类型",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Runner 包含 required evidence gate",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/acceptance_runner.py",
                "text": "aiworkflow.acceptance.required_evidence",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Report writer 输出验收类型",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/report_writer.py",
                "text": "## 验收类型",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core data-model 说明 acceptance.modes",
            "severity": "required",
            "params": {
                "path": "Core/docs/data-model.md",
                "text": "acceptance.modes",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core data-model 说明 requiredEvidence",
            "severity": "required",
            "params": {
                "path": "Core/docs/data-model.md",
                "text": "acceptance.requiredEvidence",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core runner 说明 requiredEvidence gate",
            "severity": "required",
            "params": {
                "path": "Core/docs/runner.md",
                "text": "acceptance.requiredEvidence",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core data-model 禁止旧 mode 字段",
            "severity": "required",
            "params": {
                "path": "Core/docs/data-model.md",
                "text": "acceptance.mode` 是旧结构，不再支持",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core docs 说明 mode 不互相引用",
            "severity": "required",
            "params": {
                "path": "Core/docs/check-driver-mode.md",
                "text": "Mode 文件本身不引用其他 mode",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Checks README 禁止胖 check",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/checks/README.md",
                "text": "不得把契约检查、环境准备和行为验收塞进同一个 check",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Checks README 明确 Driver 不代表最终验收",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/checks/README.md",
                "text": "Driver 不直接代表最终验收结论",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core README 链接 check driver mode 文档",
            "severity": "required",
            "params": {
                "path": "Core/README.md",
                "text": "Core/docs/check-driver-mode.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core README 链接 path-rules 文档",
            "severity": "required",
            "params": {
                "path": "Core/README.md",
                "text": "Core/docs/path-rules.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core README 链接 setup 文档",
            "severity": "required",
            "params": {
                "path": "Core/README.md",
                "text": "Core/docs/setup.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core README 保持入口页职责",
            "severity": "required",
            "params": {
                "path": "Core/README.md",
                "text": "本文只作为 Core 入口页",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 强制最终回复验收结果",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "最终回复必须包含验收结果",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 区分模板烟测与真实任务验收",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "模板安装烟测只证明 AIWorkflow 安装可运行，不能替代真实任务验收",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 使用 AITDDPolicy 作为开关",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "不要让 AI 自行猜测是否启用 AIWorkflow",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 约束 check 单一事实",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "一个 check 只能验证一种事实",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 约束 Mode 不执行流程",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "Mode 不直接执行跨环境准备、服务启动、登录、数据注入或连续请求",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 约束证据覆盖声明",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "acceptance.requiredEvidence",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 区分 contract behavior browser 验收",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "behavior acceptance",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 固化长期能力进入 mode",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "长期、可复用、会反复出现的验收能力必须沉淀为非 `temp` mode",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 说明 modes 组合入口",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "acceptance.modes",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 导航 Core docs",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "Core/docs/check-driver-mode.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Skill 导航 setup 文档",
            "severity": "required",
            "params": {
                "path": "Skill.Template/aiworkflow-trigger/SKILL.md",
                "text": "Core/docs/setup.md",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板 Current 存在",
            "severity": "required",
            "params": {"path": "Workspace.Template/Current.json"},
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板 AITDDPolicy 存在",
            "severity": "required",
            "params": {"path": "Workspace.Template/AITDDPolicy.json"},
        },
        {
            "id": "common.json.field_matches",
            "name": "Workspace 模板默认启用 AITDD",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/AITDDPolicy.json",
                "field": "defaultMode",
                "pattern": "^enabled$",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板 LatestRun 存在",
            "severity": "required",
            "params": {"path": "Workspace.Template/LatestRun.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板 ProjectContext 存在",
            "severity": "required",
            "params": {"path": "Workspace.Template/ProjectContext.md"},
        },
        {
            "id": "common.json.field_matches",
            "name": "Workspace 模板使用示例 Topic",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Current.json",
                "field": "topic",
                "pattern": "^ExampleTopic$",
            },
        },
        {
            "id": "common.content.not_contains",
            "name": "Workspace 模板不写死 AIWorkflow 宿主路径",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Current.json",
                "text": "ProjectHelp/AIWorkflow/",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板 README 存在",
            "severity": "required",
            "params": {"path": "Workspace.Template/README.md"},
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板示例 Issue 存在",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Topics/ExampleTopic/Issues/ExampleIssue/Issue.md"
            },
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板示例 Decision 存在",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Topics/ExampleTopic/Issues/ExampleIssue/Decision.md"
            },
        },
        {
            "id": "common.json.field_matches",
            "name": "Workspace 模板示例使用最小 mode",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Resolution.json",
                "field": "iterations[version=v0.1.0].acceptance.modes[0]",
                "pattern": "^aiworkflow_minimal$",
            },
        },
        {
            "id": "common.file.exists",
            "name": "Workspace 模板示例 Iteration 存在",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Topics/ExampleTopic/Issues/ExampleIssue/Resolution/Iterations/v0.1.0.md"
            },
        },
        {
            "id": "common.content.contains",
            "name": "Workspace 模板 README 说明正式 run",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/README.md",
                "text": "acceptance_runner.py run",
            },
        },
        {
            "id": "common.json.field_matches",
            "name": "Workspace 模板标记为 TEMPLATE",
            "severity": "required",
            "params": {
                "path": "Workspace.Template/Current.json",
                "field": "source",
                "pattern": "^TEMPLATE$",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Runner 阻止模板普通 run",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/acceptance_runner.py",
                "text": "模板工作区只能用于安装烟测",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Runner 支持 template smoke",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/acceptance_runner.py",
                "text": "--template-smoke",
            },
        },
        {
            "id": "common.file.exists",
            "name": "AIWorkflow 顶层 README 存在",
            "severity": "required",
            "params": {"path": "README.md"},
        },
        {
            "id": "common.content.contains",
            "name": "AIWorkflow README 说明自身位于子目录",
            "severity": "required",
            "params": {
                "path": "README.md",
                "text": "本文件位于 `AIWorkflow/README.md`",
            },
        },
        {
            "id": "common.content.contains",
            "name": "AIWorkflow README 说明 Codex 触发目录可选",
            "severity": "required",
            "params": {
                "path": "README.md",
                "text": ".codex/skills/aiworkflow-trigger/SKILL.md",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Core setup 说明复制 AIWorkflow 子目录",
            "severity": "required",
            "params": {
                "path": "Core/docs/setup.md",
                "text": "将开源仓库中的 `AIWorkflow/` 目录复制到目标项目根目录",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Windows skill 安装脚本使用脚本目录",
            "severity": "required",
            "params": {
                "path": "Skill.Template/find_codex_skills.bat",
                "text": "%~dp0",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Windows skill 安装脚本会停留窗口",
            "severity": "required",
            "params": {
                "path": "Skill.Template/find_codex_skills.bat",
                "text": "pause",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Windows skill 安装脚本执行复制",
            "severity": "required",
            "params": {
                "path": "Skill.Template/find_codex_skills.bat",
                "text": "xcopy /E /I /Y",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 README 导航职责",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_core_readme_is_navigation_not_rule_body",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 docs 职责不混写",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_core_docs_do_not_mix_responsibilities",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖指针闭环",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_current_resolution_iteration_pointer_is_closed",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 mode 不直接执行 driver",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_modes_do_not_execute_driver_processes_directly",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖旧 mode 字段拒绝",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_runner_rejects_legacy_acceptance_mode",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 mode 不互相引用",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_mode_files_do_not_reference_other_modes",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 Core docs 职责边界",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_core_docs_preserve_responsibilities_and_authority",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖 Core 生产文件技术中立",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_core_production_files_are_project_neutral",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试覆盖开源源码 Workspace 模板",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_open_source_folder_contains_workspace_template_not_workspace",
            },
        },
        {
            "id": "common.content.contains",
            "name": "Standalone 模板测试存在",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "test_core_and_workspace_template_are_minimally_runnable_standalone",
            },
        },
        {
            "id": "common.content.contains",
            "name": "结构测试排除 README.old 打包",
            "severity": "required",
            "params": {
                "path": "Core/Acceptance/tests/test_split_layout.py",
                "text": "AIWorkflow/Core/README.old.md",
            },
        },
    ],
}
