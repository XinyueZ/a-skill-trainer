# -*- coding: utf-8 -*-
"""
Internationalization (i18n) dictionary and helper for WikiSkill UI.
Supports: English (en, default), Simplified Chinese (zh), German (de).
"""

import streamlit as st

T = {
    "en": {
        "page_title": "Skill Incubation and Refinement",
        "app_title": "Skill Incubation and Refinement",
        "skills_repo_title": "📚 Skills Repository",
        "skills_repo_caption": "Real-time catalog of skills accumulated in workspace/skills/",
        "no_skills_found": "No skill directories found in workspace/skills/",
        "select_skill_dir": "Select Skill Directory:",
        "skill_md_title": "📖 `{skill}/SKILL.md`",
        "skill_md_label": "SKILL.md Content",
        "skill_md_not_found": "SKILL.md not found in this directory.",
        "view_purpose_expander": "View PURPOSE.md",
        "purpose_md_label": "PURPOSE.md",
        "error_read_skill": "Error reading SKILL.md: {err}",
        "error_read_purpose": "Error reading PURPOSE.md: {err}",
        "session_overview_title": "📊 Session Status Overview",
        "current_iteration_label": "Current Iteration:",
        "task_id_label": "Task ID:",
        "session_id_label": "Session ID:",
        "status_label": "Status:",
        "not_generated": "Not generated",
        "generating_session_id": "⏳ Generating in inference...",
        "global_reset_btn": "🗑️ Global Reset (Reset All)",
        "language_label": "🌐 Language / 语言 / Sprache",
        "config_expander_title": "⚙️ Task Configuration & Parameters",
        "task_id_input_label": "Task ID (Unique Integer)",
        "task_id_help": "Randomly generated task ID, integer only.",
        "task_name_input_label": "Task Name (Optional description)",
        "engine_radio_label": "Select Inference Engine Implementation:",
        "engine_default_suffix": " (Default)",
        "engine_caption_note": "ℹ️ **Note**: `inference_agent` uses **LangChain deepagents**; `inference_antigravity` uses **Google Antigravity**. Both share identical public interfaces.",
        "query_input_label": "Task Instruction / Query (Multiline, required):",
        "query_placeholder": "Enter task instructions / query here...",
        "query_help": "Locked as readonly when iteration >= 1.",
        "active_session_label": "Active Session ID :",
        "start_btn": "🚀 Start (Launch Iteration {iteration})",
        "start_iteration_btn": "🚀 Start (Launch Iteration {iteration})",
        "query_empty_error": "❌ Task Query cannot be empty! Please enter your instructions.",
        "pipeline_title": "🔄 Evolution Pipeline (Current: Iteration {iteration})",
        "stage1_title": "1️⃣ Inference Stage — `{engine}.py`",
        "stage1_running": "🏃‍♂️ Running inference agent...",
        "stage1_done": "✅ Inference stage completed!",
        "stage1_failed": "❌ Inference stage failed (Exit code {code})",
        "session_id_parse_failed": "❌ Failed to parse session_id from inference output!",
        "stage2_title": "2️⃣ Wiki Maintainer Stage",
        "stage2_running": "🏃‍♂️ Running Wiki Maintainer to analyze traces and update knowledge base...",
        "stage2_done": "✅ Wiki Maintainer knowledge base synchronized!",
        "stage2_failed": "❌ Wiki Maintainer failed (Exit code {code})",
        "stage3_title": "3️⃣ Skill Proposer Stage",
        "stage3_running": "🏃‍♂️ Running Skill Proposer to diagnose traces and draft skill proposal...",
        "stage3_done": "✅ Skill Proposer proposal generated!",
        "stage3_failed": "❌ Skill Proposer failed (Exit code {code})",
        "stage4_title": "4️⃣ Harness Evaluation & Decision Stage",
        "stage4_applying": "🏃‍♂️ Harness is applying proposal and generating Git Diff...",
        "proposal_not_found": "❌ Generated proposal file not found: {path}",
        "waiting_exec": "⏳ Waiting to run...",
        "no_diff_info": "ℹ️ No code changes detected (Git Diff is empty)",
        "diff_title": "🔍 Code Diff Comparison (Git Diff Side-by-Side)",
        "diff_caption": "Left: Original code (deletions in red). Right: Modified code (additions in green), with line numbers.",
        "col_old_label": "◀ Original Version (Old)",
        "col_new_label": "▶ Modified Version (New)",
        "human_review_prompt": "👤 Please review the generated proposal and provide human feedback:",
        "feedback_input_label": "Feedback (Feedback to guide subsequent iterations & recorded in audit log):",
        "feedback_placeholder": "e.g. Make the scripts more robust / Add strict library versions...",
        "accept_btn": "✅ Accept (Apply & Commit Proposal)",
        "reject_btn": "❌ Reject (Discard & Rollback Proposal)",
        "decision_accepted_banner": "🎉 Iteration {iteration}: Proposal ACCEPTED and committed to workspace/skills",
        "decision_rejected_banner": "⚠️ Iteration {iteration}: Proposal REJECTED and rolled back to clean state",
        "recorded_feedback_label": "📝 Recorded Feedback for this round:",
        "continue_btn": "⏭️ Continue (Proceed to Iteration {iteration})",
        "reset_btn": "🗑️ Complete (Clear Outputs & Reset Workspace)",
        "new_query_btn": "🌱 New Query (Start New Task on Current Skills)",
        "view_terminal_logs": "View Terminal Output & Logs",
        "unified_pipeline_title": "🔄 Incubation and Refinement of SKILL — Iteration {iteration}",
        "iteration_status_badge": "🔄 Current Round: Iteration {iteration}",
        "running_iteration_btn": "🏃‍♂️ Autonomous Evolution in Progress — Iteration {iteration}...",
        "step1_name": "Inference",
        "step2_name": "Wiki Maintainer",
        "step3_name": "Skill Proposer",
        "step_status_waiting": "Waiting",
        "step_status_running": "Running...",
        "step_status_done": "Completed",
        "step_status_failed": "Failed",
        "pipeline_all_done": "✅ Pipeline steps completed! Entering Harness evaluation...",
        "unified_pipeline_logs": "View Pipeline Execution Terminal Logs",
        "skills_browser_title": "📂 Workspace Skills Browser",
        "skill_view_mode_label": "Display Mode:",
        "skill_view_mode_rendered": "Rendered View",
        "skill_view_mode_source": "Source Code",
        "session_id_toast": "🔑 New Session ID Generated: {sid}",
        "terminal_popover_caption": "Real-time streaming terminal logs from pipeline execution.",
        "harness_modal_title": "⚖️ Harness Evaluation & Human Decision",
        "review_results_btn": "⚖️ Review & Decide / 评判结果",
        "review_pending_notice": "A skill proposal is ready. Click below to review and evaluate the result.",
        "view_diff_expander": "🔍 View Code Diff Comparison",
    },
    "zh": {
        "page_title": "Skill 孵化和完善",
        "app_title": "Skill 孵化和完善",
        "skills_repo_title": "📚 Skills 技能仓库",
        "skills_repo_caption": "实时展示 workspace/skills/ 目录下沉淀的技能",
        "no_skills_found": "workspace/skills/ 暂无已生成的技能目录",
        "select_skill_dir": "选择技能目录:",
        "skill_md_title": "📖 `{skill}/SKILL.md",
        "skill_md_label": "SKILL.md 内容",
        "skill_md_not_found": "该技能目录下未找到 SKILL.md 文件",
        "view_purpose_expander": "查看 PURPOSE.md",
        "purpose_md_label": "PURPOSE.md",
        "error_read_skill": "读取 SKILL.md 出错: {err}",
        "error_read_purpose": "读取 PURPOSE.md 出错: {err}",
        "session_overview_title": "📊 会话状态概览",
        "current_iteration_label": "当前迭代轮次 (Iteration):",
        "task_id_label": "Task ID:",
        "session_id_label": "Session ID:",
        "status_label": "运行状态:",
        "not_generated": "未生成",
        "generating_session_id": "⏳ 推理生成中...",
        "global_reset_btn": "🗑️ 全局重置 (Reset All)",
        "language_label": "🌐 语言 / Language / Sprache",
        "config_expander_title": "⚙️ 任务配置与输入参数",
        "task_id_input_label": "Task ID (唯一整数)",
        "task_id_help": "随机生成的任务ID，仅支持整数类型",
        "task_name_input_label": "Task Name (可选任务描述名)",
        "engine_radio_label": "选择推理引擎实现 (Inference Engine):",
        "engine_default_suffix": " (默认)",
        "engine_caption_note": "ℹ️ **说明**：`inference_agent` 采用 **LangChain deepagents** 框架；`inference_antigravity` 采用 **Google Antigravity** 框架。两者功能接口完全一致。",
        "query_input_label": "任务指令 / Query (多行文本输入，必填):",
        "query_placeholder": "在此输入任务指令 / Query...",
        "query_help": "iteration >= 1 时锁定为只读",
        "active_session_label": "Active Session ID:",
        "start_btn": "🚀 Start (启动 Iteration {iteration} 训练流程)",
        "start_iteration_btn": "🚀 Start (启动 Iteration {iteration} 训练流程)",
        "query_empty_error": "❌ 任务 Query 不能为空，请输入任务指令！",
        "pipeline_title": "🔄 演化流程执行流水线 (当前轮次: Iteration {iteration})",
        "stage1_title": "1️⃣ 推理环节 (Inference Stage) — `{engine}.py`",
        "stage1_running": "🏃‍♂️ 正在执行推理 (Inference)...",
        "stage1_done": "✅ 推理执行完毕！",
        "stage1_failed": "❌ 推理执行失败 (Exit code {code})",
        "session_id_parse_failed": "❌ 未能从推理输出中解析出 session_id！",
        "stage2_title": "2️⃣ Wiki 知识库维护环节 (Wiki Maintainer Stage)",
        "stage2_running": "🏃‍♂️ 正在执行 Wiki Maintainer 分析日志并更新知识库...",
        "stage2_done": "✅ Wiki Maintainer 知识库同步完毕！",
        "stage2_failed": "❌ Wiki Maintainer 执行失败 (Exit code {code})",
        "stage3_title": "3️⃣ Skill 提案生成环节 (Skill Proposer Stage)",
        "stage3_running": "🏃‍♂️ 正在执行 Skill Proposer 诊断并生成技能提案...",
        "stage3_done": "✅ Skill Proposer 提案生成完毕！",
        "stage3_failed": "❌ Skill Proposer 执行失败 (Exit code {code})",
        "stage4_title": "4️⃣ Harness 决策与验证环节 (Harness Stage)",
        "stage4_applying": "🏃‍♂️ Harness 正在自动应用提案并生成 Git Diff 对比...",
        "proposal_not_found": "❌ 未找到生成的提案文件: {path}",
        "waiting_exec": "⏳ 等待执行...",
        "no_diff_info": "ℹ️ 无代码变动 (Git Diff 为空)",
        "diff_title": "🔍 代码差异对比 (Git Diff Side-by-Side)",
        "diff_caption": "左侧为原始代码（删除标红），右侧为修改后代码（新增标绿），带行号。",
        "col_old_label": "◀ 原版本 (Original / Old)",
        "col_new_label": "▶ 修改后版本 (Modified / New)",
        "human_review_prompt": "👤 请对当前生成的提案进行审核与人类反馈 (Feedback)：",
        "feedback_input_label": "Feedback (人类反馈意见，用于指导下一轮迭代与记录演化记录):",
        "feedback_placeholder": "例如: Make the scripts more robust / Add strong library versions...",
        "accept_btn": "✅ Accept (接受并提交提案)",
        "reject_btn": "❌ Reject (拒绝并回退提案)",
        "decision_accepted_banner": "🎉 Iteration {iteration}: 提案已通过 (ACCEPTED) 并自动提交至 workspace/skills",
        "decision_rejected_banner": "⚠️ Iteration {iteration}: 提案已拒绝 (REJECTED) 并自动回退至干净状态",
        "recorded_feedback_label": "📝 本轮记录的反馈意见:",
        "continue_btn": "⏭️ Continue (进入 Iteration {iteration})",
        "reset_btn": "🗑️ 完成并清空所有",
        "new_query_btn": "🌱 New Query (基于当前成果开启新任务)",
        "view_terminal_logs": "查看终端运行输出与日志",
        "unified_pipeline_title": "🔄 孵化和完善 SKILL — Iteration {iteration}",
        "iteration_status_badge": "🔄 当前轮次: Iteration {iteration}",
        "running_iteration_btn": "🏃‍♂️ 正在自主演化 — Iteration {iteration}...",
        "step1_name": "Inference 推理",
        "step2_name": "Wiki 知识库维护",
        "step3_name": "Skill 提案生成",
        "step_status_waiting": "等待中",
        "step_status_running": "执行中...",
        "step_status_done": "已完成",
        "step_status_failed": "失败",
        "pipeline_all_done": "✅ 流水线环节执行完毕！正在进入 Harness 评估...",
        "unified_pipeline_logs": "查看完整流水线终端运行日志",
        "skills_browser_title": "📂 Workspace 技能浏览与查看",
        "skill_view_mode_label": "查看模式:",
        "skill_view_mode_rendered": "渲染效果",
        "skill_view_mode_source": "源代码",
        "session_id_toast": "🔑 新 Session ID 已生成: {sid}",
        "terminal_popover_caption": "流水线各环节实时流式执行终端日志。",
        "harness_modal_title": "⚖️ Harness 评估与人类决策",
        "review_results_btn": "⚖️ 评判结果",
        "review_pending_notice": "技能提案已生成，请点击下方按钮完成评判决策。",
        "view_diff_expander": "🔍 查看代码差异对比 (Git Diff)",
    },
    "de": {
        "page_title": "SKILL inkubieren und verfeinern",
        "app_title": "SKILL inkubieren und verfeinern",
        "skills_repo_title": "📚 Skills-Repository",
        "skills_repo_caption": "Echtzeitkatalog der unter workspace/skills/ gesammelten Fähigkeiten",
        "no_skills_found": "Keine Skill-Verzeichnisse in workspace/skills/ gefunden",
        "select_skill_dir": "Skill-Verzeichnis auswählen:",
        "skill_md_title": "📖 `{skill}/SKILL.md`",
        "skill_md_label": "SKILL.md Inhalt",
        "skill_md_not_found": "Keine SKILL.md in diesem Verzeichnis gefunden.",
        "view_purpose_expander": "PURPOSE.md ansehen",
        "purpose_md_label": "PURPOSE.md",
        "error_read_skill": "Fehler beim Lesen von SKILL.md: {err}",
        "error_read_purpose": "Fehler beim Lesen von PURPOSE.md: {err}",
        "session_overview_title": "📊 Sitzungsübersicht",
        "current_iteration_label": "Aktuelle Iterationsrunde:",
        "task_id_label": "Task-ID:",
        "session_id_label": "Sitzungs-ID:",
        "status_label": "Status:",
        "not_generated": "Nicht generiert",
        "generating_session_id": "⏳ Wird in Inferenz generiert...",
        "global_reset_btn": "🗑️ Globaler Reset (Alles zurücksetzen)",
        "language_label": "🌐 Sprache / Language / 语言",
        "config_expander_title": "⚙️ Aufgabenkonfiguration & Parameter",
        "task_id_input_label": "Task-ID (Eindeutige Ganzzahl)",
        "task_id_help": "Zufällig generierte Task-ID, nur Ganzzahl.",
        "task_name_input_label": "Task-Name (Optionale Beschreibung)",
        "engine_radio_label": "Inference-Engine-Implementierung auswählen:",
        "engine_default_suffix": " (Standard)",
        "engine_caption_note": "ℹ️ **Hinweis**: `inference_agent` basiert auf **LangChain deepagents**; `inference_antigravity` basiert auf **Google Antigravity**. Beide bieten identische Schnittstellen.",
        "query_input_label": "Aufgaben-Prompt / Query (Mehrzeilig, erforderlich):",
        "query_placeholder": "Aufgabenanweisung / Query hier eingeben...",
        "query_help": "Schreibgeschützt gesperrt, wenn Iteration >= 1.",
        "active_session_label": "Aktive Sitzungs-ID:",
        "start_btn": "🚀 Start (Runde {iteration} starten)",
        "start_iteration_btn": "🚀 Start (Runde {iteration} starten)",
        "query_empty_error": "❌ Prompt darf nicht leer sein! Bitte geben Sie Anweisungen ein.",
        "pipeline_title": "🔄 Evolutions-Pipeline (Aktuelle Runde: Iteration {iteration})",
        "stage1_title": "1️⃣ Inferenz-Phase — `{engine}.py`",
        "stage1_running": "🏃‍♂️ Inferenz-Agent wird ausgeführt...",
        "stage1_done": "✅ Inferenz-Phase abgeschlossen!",
        "stage1_failed": "❌ Inferenz fehlgeschlagen (Exit-Code {code})",
        "session_id_parse_failed": "❌ Sitzungs-ID konnte nicht aus Inferenz-Ausgabe gelesen werden!",
        "stage2_title": "2️⃣ Wiki-Wartungsphase (Wiki Maintainer)",
        "stage2_running": "🏃‍♂️ Wiki Maintainer analysiert Traces und aktualisiert die Wissensbasis...",
        "stage2_done": "✅ Wiki Maintainer Wissensbasis synchronisiert!",
        "stage2_failed": "❌ Wiki Maintainer fehlgeschlagen (Exit-Code {code})",
        "stage3_title": "3️⃣ Skill-Vorschlagsphase (Skill Proposer)",
        "stage3_running": "🏃‍♂️ Skill Proposer analysiert Traces und entwirft Skill-Vorschlag...",
        "stage3_done": "✅ Skill-Vorschlag erfolgreich generiert!",
        "stage3_failed": "❌ Skill Proposer fehlgeschlagen (Exit-Code {code})",
        "stage4_title": "4️⃣ Harness-Phase (Validierung & Entscheidung)",
        "stage4_applying": "🏃‍♂️ Harness wendet Vorschlag an und generiert Git Diff...",
        "proposal_not_found": "❌ Generierte Vorschlagsdatei nicht gefunden: {path}",
        "waiting_exec": "⏳ Wartet auf Ausführung...",
        "no_diff_info": "ℹ️ Keine Code-Änderungen erkannt (Git Diff ist leer)",
        "diff_title": "🔍 Code-Vergleich (Side-by-Side Diff)",
        "diff_caption": "Links: Originalcode (Löschungen in Rot). Rechts: Geänderter Code (Hinzufügungen in Grün), mit Zeilennummern.",
        "col_old_label": "◀ Originalversion (Alt)",
        "col_new_label": "▶ Geänderte Version (Neu)",
        "human_review_prompt": "👤 Bitte überprüfen Sie den Vorschlag und geben Sie Feedback:",
        "feedback_input_label": "Feedback (Feedback zur Steuerung der nächsten Iterationen):",
        "feedback_placeholder": "z.B. Skripte robuster gestalten / Strikte Bibliotheksversionen hinzufügen...",
        "accept_btn": "✅ Accept (Vorschlag annehmen & committen)",
        "reject_btn": "❌ Reject (Vorschlag ablehnen & zurücksetzen)",
        "decision_accepted_banner": "🎉 Iteration {iteration}: Vorschlag ANGENOMMEN und in workspace/skills committet",
        "decision_rejected_banner": "⚠️ Iteration {iteration}: Vorschlag ABGELEHNT und zurückgesetzt",
        "recorded_feedback_label": "📝 Erfasstes Feedback für diese Runde:",
        "continue_btn": "⏭️ Continue (Weiter zu Iteration {iteration})",
        "reset_btn": "🗑️ Vollständig abschließen (Ausgaben leeren & Workspace zurücksetzen)",
        "new_query_btn": "🌱 New Query (Neue Aufgabe auf aktuellem Stand)",
        "view_terminal_logs": "Terminal-Ausgabe & Logs anzeigen",
        "unified_pipeline_title": "🔄 Inkubation und Verfeinerung von SKILL — Iteration {iteration}",
        "iteration_status_badge": "🔄 Aktuelle Runde: Iteration {iteration}",
        "running_iteration_btn": "🏃‍♂️ Autonome Evolution läuft — Iteration {iteration}...",
        "step1_name": "Inferenz",
        "step2_name": "Wiki-Wartung",
        "step3_name": "Skill-Vorschlag",
        "step_status_waiting": "Wartend",
        "step_status_running": "Wird ausgeführt...",
        "step_status_done": "Abgeschlossen",
        "step_status_failed": "Fehlgeschlagen",
        "pipeline_all_done": "✅ Pipeline-Schritte abgeschlossen! Harness-Validierung wird gestartet...",
        "unified_pipeline_logs": "Vollständiges Pipeline-Terminalprotokoll anzeigen",
        "skills_browser_title": "📂 Workspace Skills-Explorer",
        "skill_view_mode_label": "Ansichtsmodus:",
        "skill_view_mode_rendered": "Gerenderte Ansicht",
        "skill_view_mode_source": "Quellcode",
        "session_id_toast": "🔑 Neue Sitzungs-ID generiert: {sid}",
        "terminal_popover_caption": "Echtzeit-Streaming-Terminalprotokolle der Pipeline-Ausführung.",
        "harness_modal_title": "⚖️ Harness-Validierung & Menschliche Entscheidung",
        "review_results_btn": "⚖️ Ergebnis bewerten",
        "review_pending_notice": "Ein Skill-Vorschlag liegt vor. Klicken Sie unten, um das Ergebnis zu bewerten.",
        "view_diff_expander": "🔍 Code-Vergleich anzeigen (Git Diff)",
    },
}


def detect_browser_language() -> str:
    """
    Detect the user's browser language preference.
    Checks Streamlit context headers (Accept-Language) and locale.
    Falls back to 'en' (English) if unknown.
    """
    # Check user manual override in session state first
    if "selected_lang" in st.session_state and st.session_state.selected_lang in T:
        return st.session_state.selected_lang

    raw_header = ""
    if hasattr(st, "context") and st.context:
        headers = getattr(st.context, "headers", None)
        if headers:
            raw_header = headers.get("accept-language", "") or headers.get(
                "Accept-Language", ""
            )
        if not raw_header:
            locale_val = getattr(st.context, "locale", None)
            if locale_val:
                raw_header = str(locale_val)

    if raw_header:
        val = raw_header.lower()
        first = val.split(",")[0].strip()
        if first.startswith("zh") or "zh-" in first:
            return "zh"
        if first.startswith("de") or "de-" in first:
            return "de"
        if first.startswith("en") or "en-" in first:
            return "en"
        # Search anywhere
        if "zh" in val:
            return "zh"
        if "de" in val:
            return "de"

    return "en"


def t(key: str, lang: str = None, **kwargs) -> str:
    """
    Retrieve translated string for the specified key.
    If lang is not provided, auto-detects from browser context.
    Falls back to English ('en') if translation is missing.
    """
    if not lang:
        lang = detect_browser_language()

    lang_dict = T.get(lang, T["en"])
    template = lang_dict.get(key, T["en"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
