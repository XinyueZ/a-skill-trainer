# -*- coding: utf-8 -*-
import html
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Ensure trainer and current working directory are on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINER_DIR = os.path.join(CURRENT_DIR, "trainer")
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if TRAINER_DIR not in sys.path:
    sys.path.insert(0, TRAINER_DIR)

import streamlit as st
import streamlit.components.v1 as components
from harness import Harness
from T import T, detect_browser_language, t

# Configure page settings
st.set_page_config(
    page_title="WikiSkill Training Workflow",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Python interpreter configuration
CONDA_PYTHON = "/opt/homebrew/anaconda3/envs/wikiskill/bin/python"
PYTHON_BIN = CONDA_PYTHON if os.path.exists(CONDA_PYTHON) else sys.executable

# --- Premium Steady-State CSS Styling ---
st.markdown(
    """
<style>
/* Core typography and resets */
h1, h2, h3, h4 {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* 1. Eliminate Streamlit ghosting and stale element duplicates permanently */
[data-stale="true"],
.element-container:has([data-stale="true"]),
div[data-testid="stAppViewContainer"] [data-stale="true"] {
    display: none !important;
}

/* 2. Hide all top right buttons except the running status animation */
[data-testid="stDeployButton"],
#MainMenu,
[data-testid="stMainMenu"],
header[data-testid="stHeader"] .stAppDeployButton,
header[data-testid="stHeader"] [data-testid="manage-app-button"],
button[title="View app options"],
button[title="Manage app"] {
    display: none !important;
}
[data-testid="stStatusWidget"] {
    display: flex !important;
    visibility: visible !important;
}

/* 3. Keep sidebar permanently open and maximized to widest possible layout */
[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"],
[data-testid="collapsedControl"] {
    display: none !important;
}
section[data-testid="stSidebar"] {
    width: 45vw !important;
    min-width: 450px !important;
    max-width: 50vw !important;
}
section[data-testid="stSidebar"] > div {
    width: 100% !important;
}
div[data-testid="stSidebarUserContent"] {
    padding: 1.5rem 1.5rem !important;
}

/* 4. Floating Terminal Popover (Fixed Bottom-Left, HIGHEST LAYER above sidebar, as in light_chat.py) */
[data-testid="stPopover"] {
    position: fixed !important;
    bottom: 24px !important;
    left: 24px !important;
    right: auto !important;
    z-index: 9999999 !important;
    width: auto !important;
    max-width: none !important;
    min-width: auto !important;
}

/* Allow the popover container to expand naturally beyond default width/height limits */
[data-baseweb="popover"] {
    max-width: none !important;
    max-height: none !important;
    z-index: 99999999 !important;
}

/* Set exact dimensions and styling on stPopoverBody */
[data-testid="stPopoverBody"] {
    width: 800px !important;
    min-width: 500px !important;
    max-width: 85vw !important;
    height: calc(100vh - 120px) !important;
    min-height: 450px !important;
    max-height: calc(100vh - 100px) !important;
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    padding: 16px 16px 12px 16px !important;
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.85) !important;
    z-index: 99999999 !important;
}

/* Pass flex properties down the Streamlit dom tree */
[data-testid="stPopoverBody"] > div,
[data-testid="stPopoverBody"] > div > [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stPopoverBody"] > div > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"],
[data-testid="stPopoverBody"] > div > [data-testid="stVerticalBlock"] {
    flex: 1 1 0% !important;
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

[data-testid="stPopoverBody"] div.element-container:has(pre),
[data-testid="stPopoverBody"] .stCode,
[data-testid="stPopoverBody"] [data-testid="stCode"],
[data-testid="stPopoverBody"] [data-testid="stCodeBlock"],
[data-testid="stPopoverBody"] .stCodeBlock {
    flex: 1 1 0% !important;
    height: 100% !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    margin-bottom: 0 !important;
}

[data-testid="stPopoverBody"] pre {
    flex: 1 1 0% !important;
    height: 100% !important;
    min-height: 0 !important;
    max-height: 100% !important;
    overflow-y: auto !important;
    overflow-x: auto !important;
    background-color: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    margin: 0 !important;
}

/* Circular floating trigger button */
.stPopover button,
[data-testid="stPopover"] > button {
    background: #1f6feb !important;
    color: white !important;
    border: none !important;
    padding: 0 !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    border-radius: 50% !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 54px !important;
    height: 54px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.stPopover button:hover,
[data-testid="stPopover"] > button:hover {
    background: #388bfd !important;
    transform: translateY(-3px) scale(1.06) !important;
    box-shadow: 0 10px 24px rgba(31, 111, 235, 0.7) !important;
}

/* 5. Action Button Styling */
.red-reset-container button,
div[data-testid="stButton"] > button:has(div:contains("Reset")),
div[data-testid="stButton"] > button:has(p:contains("Reset")),
div[data-testid="stButton"] > button:has(span:contains("Reset")) {
    background-color: #dc2626 !important;
    border: 1px solid #b91c1c !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.red-reset-container button:hover {
    background-color: #b91c1c !important;
    border-color: #991b1b !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(220, 38, 38, 0.4) !important;
}

.green-accept-container button,
.green-new-query-container button {
    background-color: #16a34a !important;
    border: 1px solid #15803d !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.green-accept-container button:hover,
.green-new-query-container button:hover {
    background-color: #15803d !important;
    border-color: #166534 !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(22, 163, 74, 0.4) !important;
}

.orange-reject-container button {
    background-color: #ea580c !important;
    border: 1px solid #c2410c !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.orange-reject-container button:hover {
    background-color: #c2410c !important;
    border-color: #9a3412 !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(234, 88, 12, 0.4) !important;
}

.blue-btn-container button {
    background-color: #2563eb !important;
    border: 1px solid #1d4ed8 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.blue-btn-container button:hover {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.4) !important;
}

/* Side-by-Side Diff Styling (GitHub style) */
.diff-container {
    font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
    font-size: 12px;
    line-height: 20px;
    border: 1px solid #30363d;
    border-radius: 6px;
    margin: 16px 0;
    overflow-x: auto;
    background-color: #0d1117;
    color: #c9d1d9;
}
.diff-header {
    background-color: #161b22;
    padding: 8px 16px;
    font-weight: 600;
    border-bottom: 1px solid #30363d;
    color: #58a6ff;
    display: flex;
    align-items: center;
    gap: 8px;
}
.diff-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}
.diff-table th {
    background-color: #21262d;
    padding: 6px 12px;
    font-size: 11px;
    text-transform: uppercase;
    color: #8b949e;
    border-bottom: 1px solid #30363d;
}
.diff-table th.col-left {
    width: 50%;
    border-right: 1px solid #30363d;
    text-align: left;
}
.diff-table th.col-right {
    width: 50%;
    text-align: left;
}
.diff-table td {
    padding: 0 4px;
    vertical-align: top;
    white-space: pre-wrap;
    word-break: break-all;
}
.line-num {
    width: 42px;
    min-width: 42px;
    text-align: right;
    padding-right: 8px !important;
    color: #6e7681;
    user-select: none;
}
.code-text {
    padding-left: 8px !important;
}
.hunk-header-row td {
    background-color: #1f242c;
    color: #8b949e;
    padding: 4px 12px;
    font-style: italic;
    border-top: 1px solid #30363d;
    border-bottom: 1px solid #30363d;
}
.bg-del {
    background-color: rgba(248, 81, 73, 0.15) !important;
}
.text-del {
    color: #ff7b72 !important;
}
.num-del {
    background-color: rgba(248, 81, 73, 0.25) !important;
    color: #ffa198 !important;
}
.bg-add {
    background-color: rgba(46, 160, 67, 0.15) !important;
}
.text-add {
    color: #7ee787 !important;
}
.num-add {
    background-color: rgba(46, 160, 67, 0.25) !important;
    color: #7ee787 !important;
}
.bg-empty {
    background-color: #0d1117;
}
.border-split {
    border-right: 1px solid #30363d;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Helper Functions ---


def strip_ansi(text: str) -> str:
    """Strip ANSI color and terminal escape sequences."""
    return re.sub(r"\x1B(?:[@-Z\-_]|\[[0-?]*[ -/]*[@-~])", "", text)


def get_workspace_skills() -> list[str]:
    """Retrieve all skill directory names in workspace/skills/."""
    skills_dir = os.path.join(CURRENT_DIR, "workspace", "skills")
    if not os.path.exists(skills_dir):
        return []
    return sorted(
        [
            d
            for d in os.listdir(skills_dir)
            if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith(".")
        ]
    )


def get_initial_iteration() -> int:
    """Read workspace/wiki/log.md, find max iteration and add 1. Fallback to 1."""
    found_iters = []
    log_path = os.path.join(CURRENT_DIR, "workspace", "wiki", "log.md")
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            matches = re.findall(
                r"##\s*Iteration\s*(\d+)\s*:", content, flags=re.IGNORECASE
            )
            for m in matches:
                found_iters.append(int(m))
        except Exception:
            pass

    if not found_iters:
        impact_path = os.path.join(CURRENT_DIR, "workspace", "wiki", "skill-impact.md")
        if os.path.exists(impact_path):
            try:
                with open(impact_path, "r", encoding="utf-8") as f:
                    content = f.read()
                matches = re.findall(
                    r"##\s*Iteration\s*(\d+)\s*:", content, flags=re.IGNORECASE
                )
                for m in matches:
                    found_iters.append(int(m))
            except Exception:
                pass

    if found_iters:
        return max(found_iters) + 1
    return 1


def extract_session_id(output_text: str) -> str:
    """Extract UUID session_id from inference stdout, latest_session.txt, or output folder."""
    # 1. Search stdout lines backwards for printed UUID
    for line in reversed(output_text.splitlines()):
        line_clean = line.strip()
        m = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            line_clean,
        )
        if m:
            return m.group(0)

    # 2. Check newest UUID folder in output/
    out_dir = os.path.join(CURRENT_DIR, "output")
    if os.path.exists(out_dir):
        subdirs = [
            d
            for d in os.listdir(out_dir)
            if os.path.isdir(os.path.join(out_dir, d))
            and re.match(
                r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                d,
            )
        ]
        if subdirs:
            subdirs.sort(
                key=lambda d: os.path.getmtime(os.path.join(out_dir, d)), reverse=True
            )
            return subdirs[0]

    # 3. Check latest_session.txt
    latest_file = os.path.join(CURRENT_DIR, "output", "latest_session.txt")
    if os.path.exists(latest_file):
        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                sid = f.read().strip()
                if sid:
                    return sid
        except Exception:
            pass

    return ""


def parse_git_diff_to_html(diff_text: str, lang: str = None) -> str:
    """Convert raw git diff string into GitHub-style side-by-side HTML view."""
    if not diff_text or not diff_text.strip():
        no_diff_msg = t("no_diff_info", lang=lang)
        return f'<div style="padding: 16px; color: #8b949e; background: #161b22; border: 1px solid #30363d; border-radius: 6px; font-family: monospace;">{no_diff_msg}</div>'

    files = []
    current_file = None
    lines = diff_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("diff --git"):
            parts = line.split()
            file_name = parts[-1].replace("b/", "") if len(parts) >= 4 else "unknown"
            current_file = {"name": file_name, "hunks": []}
            files.append(current_file)
            i += 1
            continue
        if current_file is None:
            i += 1
            continue
        if line.startswith("@@"):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            old_line = int(m.group(1)) if m else 1
            new_line = int(m.group(3)) if m else 1
            hunk = {"header": line, "raw_lines": []}
            current_file["hunks"].append(hunk)
            i += 1
            while (
                i < len(lines)
                and not lines[i].startswith("diff --git")
                and not lines[i].startswith("@@")
            ):
                l = lines[i]
                if l.startswith("---") or l.startswith("+++"):
                    i += 1
                    continue
                if l.startswith("-"):
                    hunk["raw_lines"].append(
                        {"type": "del", "num": old_line, "text": l[1:]}
                    )
                    old_line += 1
                elif l.startswith("+"):
                    hunk["raw_lines"].append(
                        {"type": "add", "num": new_line, "text": l[1:]}
                    )
                    new_line += 1
                elif l.startswith(" ") or l == "":
                    content = l[1:] if l.startswith(" ") else l
                    hunk["raw_lines"].append(
                        {
                            "type": "ctx",
                            "old_num": old_line,
                            "new_num": new_line,
                            "text": content,
                        }
                    )
                    old_line += 1
                    new_line += 1
                else:
                    i += 1
                    continue
                i += 1
            continue
        i += 1

    col_old = t("col_old_label", lang=lang)
    col_new = t("col_new_label", lang=lang)

    html_out = []
    for f in files:
        html_out.append('<div class="diff-container">')
        html_out.append(f'<div class="diff-header">📄 {html.escape(f["name"])}</div>')
        html_out.append('<table class="diff-table">')
        html_out.append(
            f'<thead><tr><th colspan="2" class="col-left">{html.escape(col_old)}</th><th colspan="2" class="col-right">{html.escape(col_new)}</th></tr></thead>'
        )
        html_out.append("<tbody>")

        for hunk in f["hunks"]:
            html_out.append(
                f'<tr class="hunk-header-row"><td colspan="4">{html.escape(hunk["header"])}</td></tr>'
            )

            del_buf = []
            add_buf = []

            def render_aligned(rows_html):
                m = max(len(del_buf), len(add_buf))
                for idx in range(m):
                    d = del_buf[idx] if idx < len(del_buf) else None
                    a = add_buf[idx] if idx < len(add_buf) else None

                    old_num_str = str(d["num"]) if d else ""
                    old_text_str = html.escape(d["text"]) if d else ""
                    old_num_class = "line-num num-del" if d else "line-num bg-empty"
                    old_text_class = (
                        "code-text bg-del text-del border-split"
                        if d
                        else "code-text bg-empty border-split"
                    )
                    old_prefix = "- " if d else ""

                    new_num_str = str(a["num"]) if a else ""
                    new_text_str = html.escape(a["text"]) if a else ""
                    new_num_class = "line-num num-add" if a else "line-num bg-empty"
                    new_text_class = (
                        "code-text bg-add text-add" if a else "code-text bg-empty"
                    )
                    new_prefix = "+ " if a else ""

                    rows_html.append(
                        f'<tr><td class="{old_num_class}">{old_num_str}</td><td class="{old_text_class}">{old_prefix}{old_text_str}</td><td class="{new_num_class}">{new_num_str}</td><td class="{new_text_class}">{new_prefix}{new_text_str}</td></tr>'
                    )
                del_buf.clear()
                add_buf.clear()

            for item in hunk["raw_lines"]:
                if item["type"] == "del":
                    del_buf.append(item)
                elif item["type"] == "add":
                    add_buf.append(item)
                elif item["type"] == "ctx":
                    render_aligned(html_out)
                    num_old = str(item["old_num"])
                    num_new = str(item["new_num"])
                    text = html.escape(item["text"])
                    html_out.append(
                        f'<tr><td class="line-num">{num_old}</td><td class="code-text border-split">  {text}</td><td class="line-num">{num_new}</td><td class="code-text">  {text}</td></tr>'
                    )
            render_aligned(html_out)

        html_out.append("</tbody></table></div>")

    return "".join(html_out)


def run_streaming_process(
    cmd: list[str], log_placeholder, prefix_text: str = ""
) -> tuple[int, str]:
    """Execute subprocess and live stream terminal stdout with smooth throttling and full unclipped history."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    trainer_dir = os.path.join(CURRENT_DIR, "trainer")
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{CURRENT_DIR}:{trainer_dir}:{existing_pp}"

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        env=env,
        cwd=CURRENT_DIR,
    )

    all_lines = []
    last_render_time = 0.0
    RENDER_INTERVAL = (
        0.25  # Smooth 4fps throttle to prevent DOM thrashing and allow smooth scrolling
    )

    for raw_line in iter(proc.stdout.readline, ""):
        if not raw_line:
            break
        clean = strip_ansi(raw_line)
        all_lines.append(clean)

        now = time.time()
        if now - last_render_time >= RENDER_INTERVAL:
            full_display = prefix_text + "".join(all_lines)
            st.session_state.logs["unified"] = full_display
            log_placeholder.code(full_display, language="bash")
            last_render_time = now

    proc.stdout.close()
    return_code = proc.wait()

    # Final complete flush
    full_output = "".join(all_lines)
    final_full = prefix_text + full_output
    st.session_state.logs["unified"] = final_full
    log_placeholder.code(final_full, language="bash")
    return return_code, full_output


def render_step_card_html(
    step_num: int, title: str, state: str, elapsed: float = None
) -> str:
    """Generate responsive dark-themed step status card HTML with elapsed duration."""
    lang_texts = {
        "waiting": t("step_status_waiting"),
        "running": t("step_status_running"),
        "done": t("step_status_done"),
        "failed": t("step_status_failed"),
    }
    styles = {
        "waiting": {
            "bg": "#161b22",
            "border": "#30363d",
            "title_color": "#8b949e",
            "status_color": "#6e7681",
            "text": lang_texts["waiting"],
        },
        "running": {
            "bg": "#1f242c",
            "border": "#1f6feb",
            "title_color": "#58a6ff",
            "status_color": "#79c0ff",
            "text": lang_texts["running"],
        },
        "done": {
            "bg": "#16231a",
            "border": "#238636",
            "title_color": "#7ee787",
            "status_color": "#56d364",
            "text": lang_texts["done"],
        },
        "failed": {
            "bg": "#2a1719",
            "border": "#da3633",
            "title_color": "#f85149",
            "status_color": "#ff7b72",
            "text": lang_texts["failed"],
        },
    }
    s = styles.get(state, styles["waiting"])

    time_badge = ""
    if elapsed is not None and state in ("done", "failed"):
        time_badge = f" ({elapsed:.1f}s)"

    return (
        f'<div style="background-color: {s["bg"]}; border: 1px solid {s["border"]}; border-radius: 8px; padding: 12px 8px; text-align: center;">'
        f'<div style="font-size: 13px; font-weight: 600; color: {s["title_color"]};">{step_num}. {title}</div>'
        f'<div style="font-size: 11px; color: {s["status_color"]}; margin-top: 4px;">{s["text"]}{time_badge}</div>'
        "</div>"
    )


def perform_continue():
    """Advance to next iteration with current settings."""
    st.session_state.iteration += 1
    st.session_state.session_id = None
    st.session_state.pipeline_status = "running"
    st.session_state.auto_popup = False
    st.session_state.harness_instance = None
    st.session_state.diff_text = ""
    st.session_state.decision = None
    st.session_state.feedback = ""
    st.session_state.step_states = {
        "step1": "waiting",
        "step2": "waiting",
        "step3": "waiting",
    }
    st.session_state.step_times = {
        "step1": None,
        "step2": None,
        "step3": None,
    }
    st.session_state.logs = {
        "unified": "",
        "inference": "",
        "wiki_maintainer": "",
        "skill_proposer": "",
        "harness": "",
    }


def perform_new_query():
    """Start a fresh new query based on current evolved workspace (keeps iteration & workspace intact)."""
    st.session_state.session_id = None
    st.session_state.active_query = ""
    st.session_state.widget_query = ""
    st.session_state.widget_task_id = random.randint(1000, 9999)
    st.session_state.pipeline_status = "idle"
    st.session_state.auto_popup = False
    st.session_state.step_states = {
        "step1": "waiting",
        "step2": "waiting",
        "step3": "waiting",
    }
    st.session_state.step_times = {
        "step1": None,
        "step2": None,
        "step3": None,
    }
    st.session_state.harness_instance = None
    st.session_state.diff_text = ""
    st.session_state.decision = None
    st.session_state.feedback = ""
    st.session_state.logs = {
        "unified": "",
        "inference": "",
        "wiki_maintainer": "",
        "skill_proposer": "",
        "harness": "",
    }


def perform_full_reset():
    """Execute clean-all-outputs.sh & reset-workspace.sh and revert everything to initial blank state."""
    subprocess.run(["bash", "./clean-all-outputs.sh"], cwd=CURRENT_DIR, check=False)
    subprocess.run(
        ["bash", "./reset-workspace.sh", "--workspace", "./workspace"],
        cwd=CURRENT_DIR,
        check=False,
    )

    cur_lang = st.session_state.get("selected_lang", None)

    st.session_state.iteration = get_initial_iteration()
    st.session_state.session_id = None
    st.session_state.widget_task_id = random.randint(1000, 9999)
    st.session_state.widget_task_name = "walk-through-task"
    st.session_state.pipeline_status = "idle"
    st.session_state.auto_popup = False
    st.session_state.step_states = {
        "step1": "waiting",
        "step2": "waiting",
        "step3": "waiting",
    }
    st.session_state.step_times = {
        "step1": None,
        "step2": None,
        "step3": None,
    }
    st.session_state.harness_instance = None
    st.session_state.diff_text = ""
    st.session_state.decision = None
    st.session_state.feedback = ""
    st.session_state.active_query = ""
    st.session_state.widget_query = ""
    st.session_state.logs = {
        "unified": "",
        "inference": "",
        "wiki_maintainer": "",
        "skill_proposer": "",
        "harness": "",
    }
    if cur_lang:
        st.session_state.selected_lang = cur_lang


# --- Initialize Session State (Using native keys for flawless reactivity) ---
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.iteration = get_initial_iteration()
    st.session_state.session_id = None
    st.session_state.auto_popup = False
    st.session_state.pipeline_status = (
        "idle"  # idle | running | awaiting_decision | decision_made
    )
    st.session_state.step_states = {
        "step1": "waiting",
        "step2": "waiting",
        "step3": "waiting",
    }
    st.session_state.step_times = {
        "step1": None,
        "step2": None,
        "step3": None,
    }
    st.session_state.harness_instance = None
    st.session_state.diff_text = ""
    st.session_state.decision = None
    st.session_state.feedback = ""
    st.session_state.logs = {
        "unified": "",
        "inference": "",
        "wiki_maintainer": "",
        "skill_proposer": "",
        "harness": "",
    }
    # Direct widget initial states to prevent Streamlit state conflict
    st.session_state.widget_task_id = random.randint(1000, 9999)
    st.session_state.widget_task_name = "walk-through-task"
    st.session_state.active_query = ""
    st.session_state.widget_query = ""
    st.session_state.widget_engine = "inference_agent"
    st.session_state.selected_lang = detect_browser_language()


# --- Sidebar: Workspace Skills Inspector & Global Reset ---
with st.sidebar:
    lang_options = {
        "en": "English (en)",
        "zh": "简体中文 (zh)",
        "de": "Deutsch (de)",
    }
    current_lang = st.session_state.get("selected_lang", "en")
    if current_lang not in lang_options:
        current_lang = "en"

    def on_lang_change():
        st.session_state.selected_lang = st.session_state.widget_lang

    st.selectbox(
        t("language_label"),
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(current_lang),
        key="widget_lang",
        on_change=on_lang_change,
    )

    st.divider()
    st.title(t("skills_repo_title"))
    st.caption(t("skills_repo_caption"))

    skills_list = get_workspace_skills()
    if not skills_list:
        st.info(t("no_skills_found"))
    else:
        selected_sidebar_skill = st.selectbox(
            t("select_skill_dir"), skills_list, key="widget_sidebar_skill"
        )
        if selected_sidebar_skill:
            skill_md_path = os.path.join(
                CURRENT_DIR, "workspace", "skills", selected_sidebar_skill, "SKILL.md"
            )
            purpose_md_path = os.path.join(
                CURRENT_DIR, "workspace", "skills", selected_sidebar_skill, "PURPOSE.md"
            )

            if os.path.exists(skill_md_path):
                st.markdown(t("skill_md_title", skill=selected_sidebar_skill))
                try:
                    with open(skill_md_path, "r", encoding="utf-8") as f:
                        st.code(body=f.read(), height=300, language="markdown")
                except Exception as e:
                    st.error(t("error_read_skill", err=str(e)))
            else:
                st.warning(t("skill_md_not_found"))

            if os.path.exists(purpose_md_path):
                with st.expander(t("view_purpose_expander")):
                    try:
                        with open(purpose_md_path, "r", encoding="utf-8") as f:
                            st.code(body=f.read(), height=300, language="markdown")
                    except Exception as e:
                        st.error(t("error_read_purpose", err=str(e)))

    st.divider()
    st.markdown(f"### {t('session_overview_title')}")
    st.write(f"**{t('current_iteration_label')}** `{st.session_state.iteration}`")
    st.write(f"**{t('task_id_label')}** `{st.session_state.widget_task_id}`")
    sidebar_session_placeholder = st.empty()
    st.write(f"**{t('status_label')}** `{st.session_state.pipeline_status}`")

    def update_sidebar_session(sid=None):
        current_sid = sid or st.session_state.get("session_id")
        if current_sid:
            sidebar_session_placeholder.write(
                f"**{t('session_id_label')}** `{current_sid}`"
            )
        else:
            sidebar_session_placeholder.empty()

    update_sidebar_session()

    # Global emergency reset button in sidebar (Red)
    st.markdown('<div class="red-reset-container">', unsafe_allow_html=True)
    if st.button(t("global_reset_btn"), key="sidebar_reset_btn"):
        perform_full_reset()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# --- Main Area ---
st.title(t("app_title"))

# Prominent Top Status Card (Iteration & Session Details)
top_status_card_placeholder = st.empty()


def update_top_status_card(sid=None):
    current_sid = sid or st.session_state.get("session_id")
    sid_html = ""
    if current_sid:
        sid_html = f'<span style="font-size: 13px; color: #8b949e;">{t("session_id_label")} <code style="color: #e6edf3; background: #21262d; padding: 2px 6px; border-radius: 4px;">{current_sid}</code></span>'

    badge = t("iteration_status_badge", iteration=st.session_state.iteration)
    task_label = t("task_id_label")
    task_val = st.session_state.widget_task_id

    card_html = (
        '<div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 18px; margin: 12px 0 16px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">'
        f'<span style="font-size: 16px; font-weight: 700; color: #58a6ff;">{badge}</span>'
        f'<span style="font-size: 13px; color: #8b949e;">{task_label} <strong style="color: #79c0ff;">{task_val}</strong></span>'
        f"{sid_html}"
        "</div>"
    )
    top_status_card_placeholder.markdown(card_html, unsafe_allow_html=True)


update_top_status_card()

# --- Configuration & Input Section (Encapsulated in st.form for 100% single-click responsiveness) ---
is_locked = st.session_state.pipeline_status != "idle"

with st.expander(
    t("config_expander_title"), expanded=(st.session_state.pipeline_status == "idle")
):
    with st.form("task_config_form", clear_on_submit=False):
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            st.number_input(
                t("task_id_input_label"),
                min_value=1,
                step=1,
                disabled=is_locked,
                help=t("task_id_help"),
                key="widget_task_id",
            )

        with col_t2:
            st.text_input(
                t("task_name_input_label"),
                disabled=is_locked,
                key="widget_task_name",
            )

        # Inference engine radio choice (Requirement 8)
        st.markdown(f"**{t('engine_radio_label')}**")
        is_engine_disabled = st.session_state.pipeline_status == "running"
        st.radio(
            label="Inference Engine",
            options=[
                "inference_agent",
            ],  # "inference_antigravity"
            format_func=lambda x: (
                f"{x}{t('engine_default_suffix')}" if x == "inference_agent" else x
            ),
            horizontal=True,
            disabled=is_engine_disabled,
            label_visibility="collapsed",
            key="widget_engine",
        )
        st.caption(t("engine_caption_note"))

        # Query multiline text area (Requirement 6)
        query_val = st.text_area(
            t("query_input_label"),
            height=100,
            disabled=is_locked,
            help=t("query_help"),
            placeholder=t("query_placeholder"),
            key="widget_query",
        )

        # Session ID display: Only visible once generated by inference
        if st.session_state.get("session_id"):
            st.text_input(
                t("active_session_label"),
                value=st.session_state.session_id,
                disabled=True,
            )

        # Permanent Form Submit / Action Button Slot inside form (100% single-click launch)
        st.markdown('<div class="blue-btn-container">', unsafe_allow_html=True)
        if st.session_state.pipeline_status == "idle":
            btn_text = t("start_btn", iteration=st.session_state.iteration)
            submitted = st.form_submit_button(
                btn_text, type="primary", use_container_width=True
            )
            if submitted:
                raw_q = (query_val or "").strip()
                if not raw_q:
                    st.error(t("query_empty_error"))
                else:
                    st.session_state.active_query = raw_q
                    st.session_state.pipeline_status = "running"
                    st.rerun()
        else:
            st.form_submit_button(
                t("running_iteration_btn", iteration=st.session_state.iteration),
                type="primary",
                disabled=True,
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

# --- Unified Pipeline Container (Inference ➔ Wiki ➔ Proposer 串起来展示) ---
st.markdown("---")
with st.container():
    st.markdown(
        f"### {t('unified_pipeline_title', iteration=st.session_state.iteration)}"
    )
    pipeline_overall_status = st.empty()

    # Visual Stepper Bar: 3 steps chained with arrows
    col_s1, col_a1, col_s2, col_a2, col_s3 = st.columns([3, 1, 3, 1, 3])
    with col_s1:
        s1_card = st.empty()
    with col_a1:
        st.markdown(
            "<div style='text-align: center; font-size: 22px; color: #8b949e; line-height: 48px;'>➔</div>",
            unsafe_allow_html=True,
        )
    with col_s2:
        s2_card = st.empty()
    with col_a2:
        st.markdown(
            "<div style='text-align: center; font-size: 22px; color: #8b949e; line-height: 48px;'>➔</div>",
            unsafe_allow_html=True,
        )
    with col_s3:
        s3_card = st.empty()

    # Initial render of step cards based on session state and stored elapsed times
    s1_card.markdown(
        render_step_card_html(
            1,
            t("step1_name"),
            st.session_state.step_states["step1"],
            elapsed=st.session_state.step_times["step1"],
        ),
        unsafe_allow_html=True,
    )
    s2_card.markdown(
        render_step_card_html(
            2,
            t("step2_name"),
            st.session_state.step_states["step2"],
            elapsed=st.session_state.step_times["step2"],
        ),
        unsafe_allow_html=True,
    )
    s3_card.markdown(
        render_step_card_html(
            3,
            t("step3_name"),
            st.session_state.step_states["step3"],
            elapsed=st.session_state.step_times["step3"],
        ),
        unsafe_allow_html=True,
    )

    if st.session_state.logs.get("unified"):
        if all(
            st.session_state.step_states[k] == "done"
            for k in ["step1", "step2", "step3"]
        ):
            pipeline_overall_status.success(t("pipeline_all_done"))
    else:
        pipeline_overall_status.info(t("waiting_exec"))

# --- Floating Terminal Drawer Popover (Fixed Bottom-Left, Highest Layer, As in light_chat.py) ---
with st.popover("", icon="🖥️", help=t("unified_pipeline_logs")):
    st.markdown(f"#### {t('unified_pipeline_logs')}")
    st.caption(t("terminal_popover_caption"))

    unified_log_box = st.empty()
    active_logs = st.session_state.logs.get("unified", "")
    if active_logs:
        unified_log_box.code(active_logs, language="bash")
    else:
        unified_log_box.code(t("waiting_exec"), language="bash")

    # Smart auto-scroll inside popover
    components.html(
        """
        <script>
        (function() {
            function updateTerminalScroll() {
                try {
                    const popover = window.parent.document.querySelector('[data-testid="stPopoverBody"]');
                    if (!popover) return;
                    const pre = popover.querySelector('pre');
                    if (!pre) return;

                    if (!pre.__scrollListenerAttached) {
                        pre.__userScrolledUp = false;
                        pre.addEventListener('scroll', function() {
                            const distanceToBottom = pre.scrollHeight - pre.scrollTop - pre.clientHeight;
                            // If user scrolled up > 60px, pause auto-scroll to let them read history in peace
                            pre.__userScrolledUp = distanceToBottom > 60;
                        });
                        pre.__scrollListenerAttached = true;
                    }

                    if (!pre.__userScrolledUp) {
                        pre.scrollTop = pre.scrollHeight;
                    }
                } catch(e) {}
            }

            updateTerminalScroll();
            const root = window.parent.document.querySelector('[data-testid="stPopoverBody"]');
            if (root && !root.__mutationObserved) {
                const observer = new MutationObserver(updateTerminalScroll);
                observer.observe(root, { childList: true, subtree: true, characterData: true });
                root.__mutationObserved = true;
            }
        })();
        </script>
        """,
        height=0,
    )


# --- Execution Controller Logic ---
if st.session_state.pipeline_status == "running":
    task_id_str = str(st.session_state.widget_task_id)
    task_name_str = st.session_state.widget_task_name or "default_task"
    query_str = (
        st.session_state.get("active_query")
        or st.session_state.get("widget_query")
        or ""
    ).strip()
    if not query_str:
        pipeline_overall_status.error(t("query_empty_error"))
        st.session_state.pipeline_status = "idle"
        st.stop()
    engine_file = f"trainer/{st.session_state.widget_engine}.py"
    output_dir = os.path.join(CURRENT_DIR, "output")
    skills_dir = os.path.join(CURRENT_DIR, "workspace", "skills")
    wiki_dir = os.path.join(CURRENT_DIR, "workspace", "wiki")
    workspace_dir = os.path.join(CURRENT_DIR, "workspace")

    # Step 1: Execute Inference
    st.session_state.step_states = {
        "step1": "running",
        "step2": "waiting",
        "step3": "waiting",
    }
    st.session_state.step_times = {"step1": 0.0, "step2": None, "step3": None}
    s1_card.markdown(
        render_step_card_html(1, t("step1_name"), "running"), unsafe_allow_html=True
    )
    s2_card.markdown(
        render_step_card_html(2, t("step2_name"), "waiting"), unsafe_allow_html=True
    )
    s3_card.markdown(
        render_step_card_html(3, t("step3_name"), "waiting"), unsafe_allow_html=True
    )
    pipeline_overall_status.warning(f"🏃‍♂️ [1/3] {t('stage1_running')}")

    h1 = f"============================================================\n▶ [1/3] {t('step1_name')} ({st.session_state.widget_engine}.py)\n============================================================\n"
    inf_cmd = [
        PYTHON_BIN,
        engine_file,
        "--task_id",
        task_id_str,
        "--task_name",
        task_name_str,
        "--query",
        query_str,
        "--system_prompt",
        "Answer user question and finish task. Your answers must be based on true and reality, avoid answering that you do not know",
        "--skills_dir",
        skills_dir,
        "--output_dir",
        output_dir,
        "--stream_mode",
    ]

    t1_start = time.time()
    ret1, out1 = run_streaming_process(inf_cmd, unified_log_box, prefix_text=h1)
    t1_elapsed = time.time() - t1_start
    st.session_state.step_times["step1"] = t1_elapsed
    st.session_state.logs["inference"] = out1
    if ret1 != 0:
        st.session_state.step_states["step1"] = "failed"
        s1_card.markdown(
            render_step_card_html(1, t("step1_name"), "failed", elapsed=t1_elapsed),
            unsafe_allow_html=True,
        )
        pipeline_overall_status.error(t("stage1_failed", code=ret1))
        st.session_state.pipeline_status = "idle"
        st.stop()
    st.session_state.step_states["step1"] = "done"
    s1_card.markdown(
        render_step_card_html(1, t("step1_name"), "done", elapsed=t1_elapsed),
        unsafe_allow_html=True,
    )
    acc_logs = h1 + out1

    # Capture session_id
    session_id = extract_session_id(out1)
    if not session_id:
        pipeline_overall_status.error(t("session_id_parse_failed"))
        st.session_state.pipeline_status = "idle"
        st.stop()

    # Update session_id everywhere immediately upon capture (3 UIs: Top card, Sidebar, Toast)
    st.session_state.session_id = session_id
    update_top_status_card(session_id)
    update_sidebar_session(session_id)
    st.toast(t("session_id_toast", sid=session_id), icon="🔑")

    # Persist latest_session.txt
    os.makedirs(output_dir, exist_ok=True)
    with open(
        os.path.join(output_dir, "latest_session.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(session_id)

    traces_dir = os.path.join(output_dir, session_id, task_id_str)

    # Step 2: Execute Wiki Maintainer
    st.session_state.step_states["step2"] = "running"
    s2_card.markdown(
        render_step_card_html(2, t("step2_name"), "running"), unsafe_allow_html=True
    )
    pipeline_overall_status.warning(f"🏃‍♂️ [2/3] {t('stage2_running')}")

    h2 = f"\n\n============================================================\n▶ [2/3] {t('step2_name')} (wiki_maintainer.py)\n============================================================\n"
    wm_cmd = [
        PYTHON_BIN,
        "trainer/wiki_maintainer.py",
        "--traces_dir",
        traces_dir,
        "--wiki_dir",
        wiki_dir,
        "--stream_mode",
    ]

    t2_start = time.time()
    ret2, out2 = run_streaming_process(
        wm_cmd, unified_log_box, prefix_text=acc_logs + h2
    )
    t2_elapsed = time.time() - t2_start
    st.session_state.step_times["step2"] = t2_elapsed
    st.session_state.logs["wiki_maintainer"] = out2
    if ret2 != 0:
        st.session_state.step_states["step2"] = "failed"
        s2_card.markdown(
            render_step_card_html(2, t("step2_name"), "failed", elapsed=t2_elapsed),
            unsafe_allow_html=True,
        )
        pipeline_overall_status.error(t("stage2_failed", code=ret2))
        st.session_state.pipeline_status = "idle"
        st.stop()
    st.session_state.step_states["step2"] = "done"
    s2_card.markdown(
        render_step_card_html(2, t("step2_name"), "done", elapsed=t2_elapsed),
        unsafe_allow_html=True,
    )
    acc_logs += h2 + out2

    # Step 3: Execute Skill Proposer
    st.session_state.step_states["step3"] = "running"
    s3_card.markdown(
        render_step_card_html(3, t("step3_name"), "running"), unsafe_allow_html=True
    )
    pipeline_overall_status.warning(f"🏃‍♂️ [3/3] {t('stage3_running')}")

    h3 = f"\n\n============================================================\n▶ [3/3] {t('step3_name')} (skill_proposer.py)\n============================================================\n"
    sp_cmd = [
        PYTHON_BIN,
        "trainer/skill_proposer.py",
        "--session_id",
        session_id,
        "--task_id",
        task_id_str,
        "--traces_dir",
        traces_dir,
        "--workspace_dir",
        workspace_dir,
        "--output_dir",
        output_dir,
        "--stream_mode",
    ]

    t3_start = time.time()
    ret3, out3 = run_streaming_process(
        sp_cmd, unified_log_box, prefix_text=acc_logs + h3
    )
    t3_elapsed = time.time() - t3_start
    st.session_state.step_times["step3"] = t3_elapsed
    st.session_state.logs["skill_proposer"] = out3
    if ret3 != 0:
        st.session_state.step_states["step3"] = "failed"
        s3_card.markdown(
            render_step_card_html(3, t("step3_name"), "failed", elapsed=t3_elapsed),
            unsafe_allow_html=True,
        )
        pipeline_overall_status.error(t("stage3_failed", code=ret3))
        st.session_state.pipeline_status = "idle"
        st.stop()
    st.session_state.step_states["step3"] = "done"
    s3_card.markdown(
        render_step_card_html(3, t("step3_name"), "done", elapsed=t3_elapsed),
        unsafe_allow_html=True,
    )
    acc_logs += h3 + out3

    st.session_state.logs["unified"] = acc_logs
    pipeline_overall_status.success(t("pipeline_all_done"))

    # Step 4: Auto Execute Harness apply and get_diff
    pipeline_overall_status.warning(t("stage4_applying"))
    proposal_path = os.path.join(traces_dir, "proposal.json")
    if not os.path.exists(proposal_path):
        pipeline_overall_status.error(t("proposal_not_found", path=proposal_path))
        st.session_state.pipeline_status = "idle"
        st.stop()

    harness = Harness()
    harness.apply(proposal_path=proposal_path, skills_dir=skills_dir)
    diff = harness.get_diff(workspace_dir=workspace_dir)

    st.session_state.harness_instance = harness
    st.session_state.diff_text = diff
    st.session_state.pipeline_status = "awaiting_decision"
    st.session_state.auto_popup = True
    st.rerun()


# --- Modal Dialog: Harness Evaluation & Decision (@st.dialog) ---
@st.dialog(t("harness_modal_title"), width="large")
def evaluation_dialog():
    st.caption(t("human_review_prompt"))

    # Git Diff Side-by-Side Comparison (GitHub style)
    st.markdown(f"#### {t('diff_title')}")
    st.caption(t("diff_caption"))
    diff_html = parse_git_diff_to_html(
        st.session_state.diff_text, lang=st.session_state.selected_lang
    )
    st.markdown(diff_html, unsafe_allow_html=True)

    with st.form(
        f"dialog_decision_form_{st.session_state.iteration}", clear_on_submit=False
    ):
        # Human feedback input inside dialog
        feedback_input = st.text_area(
            t("feedback_input_label"),
            placeholder=t("feedback_placeholder"),
            height=90,
            key=f"dlg_feedback_{st.session_state.iteration}",
        )

        col_acc, col_rej = st.columns([1, 1])

        with col_acc:
            st.markdown('<div class="green-accept-container">', unsafe_allow_html=True)
            acc_submitted = st.form_submit_button(
                t("accept_btn"), use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_rej:
            st.markdown('<div class="orange-reject-container">', unsafe_allow_html=True)
            rej_submitted = st.form_submit_button(
                t("reject_btn"), use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if acc_submitted:
            h = st.session_state.harness_instance
            workspace_dir = os.path.join(CURRENT_DIR, "workspace")
            skills_dir = os.path.join(workspace_dir, "skills")
            wiki_dir = os.path.join(workspace_dir, "wiki")
            fb_text = (feedback_input or "").strip()

            h.accept_or_reject(
                workspace_dir=workspace_dir, skill_dir=skills_dir, reject=False
            )
            h.update(
                wiki_dir=wiki_dir,
                feedback=fb_text,
                iteration=st.session_state.iteration,
            )

            st.session_state.decision = "ACCEPTED"
            st.session_state.feedback = fb_text
            st.session_state.pipeline_status = "decision_made"
            st.session_state.auto_popup = False
            st.rerun()

        elif rej_submitted:
            h = st.session_state.harness_instance
            workspace_dir = os.path.join(CURRENT_DIR, "workspace")
            skills_dir = os.path.join(workspace_dir, "skills")
            wiki_dir = os.path.join(workspace_dir, "wiki")
            fb_text = (feedback_input or "").strip()

            h.accept_or_reject(
                workspace_dir=workspace_dir, skill_dir=skills_dir, reject=True
            )
            h.update(
                wiki_dir=wiki_dir,
                feedback=fb_text,
                iteration=st.session_state.iteration,
            )

            st.session_state.decision = "REJECTED"
            st.session_state.feedback = fb_text
            st.session_state.pipeline_status = "decision_made"
            st.session_state.auto_popup = False
            st.rerun()


# Auto-popup modal dialog for the first time after Step 4 completes
if (
    st.session_state.get("auto_popup")
    and st.session_state.pipeline_status == "awaiting_decision"
):
    st.session_state.auto_popup = False
    evaluation_dialog()


# --- Section C: Stage 4 Harness Decision & Human Interaction ---
if st.session_state.pipeline_status in ("awaiting_decision", "decision_made"):
    st.markdown("---")
    with st.container():
        st.markdown(f"### {t('stage4_title')}")
        s4_status = st.empty()

        if st.session_state.pipeline_status == "awaiting_decision":
            # Dialog closed via 'X' without decision: prompt to evaluate result
            st.info(t("review_pending_notice"))
            st.markdown('<div class="blue-btn-container">', unsafe_allow_html=True)
            if st.button(
                t("review_results_btn"),
                key="btn_open_evaluation_modal",
                type="primary",
                use_container_width=True,
            ):
                evaluation_dialog()
            st.markdown("</div>", unsafe_allow_html=True)

        elif st.session_state.pipeline_status == "decision_made":
            # Option 1: Lightweight clean outcome view
            if st.session_state.decision == "ACCEPTED":
                s4_status.success(
                    t("decision_accepted_banner", iteration=st.session_state.iteration)
                )
            else:
                s4_status.warning(
                    t("decision_rejected_banner", iteration=st.session_state.iteration)
                )

            if st.session_state.feedback:
                st.markdown(
                    f"**{t('recorded_feedback_label')}** `{st.session_state.feedback}`"
                )

            with st.expander(t("view_diff_expander"), expanded=False):
                diff_html = parse_git_diff_to_html(
                    st.session_state.diff_text, lang=st.session_state.selected_lang
                )
                st.markdown(diff_html, unsafe_allow_html=True)

            st.markdown("---")
            col_cont, col_rst = st.columns([1, 1])

            with col_cont:
                st.markdown('<div class="blue-btn-container">', unsafe_allow_html=True)
                st.button(
                    t("continue_btn", iteration=st.session_state.iteration + 1),
                    key="btn_continue_after_decision",
                    use_container_width=True,
                    on_click=perform_continue,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col_rst:
                st.markdown(
                    '<div class="green-new-query-container">', unsafe_allow_html=True
                )
                st.button(
                    t("new_query_btn"),
                    key="btn_new_query_after_decision",
                    use_container_width=True,
                    on_click=perform_new_query,
                )
                st.markdown("</div>", unsafe_allow_html=True)
