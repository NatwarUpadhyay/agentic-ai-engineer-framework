"""
tabs/tab_repo_analyzer.py
─────────────────────────────────────────────────────────────────────────────
Repo Analyzer tab — Upload a ZIP, get AI-powered nudges:
  • Which Claude Code skills to add
  • Which files to create
  • Prioritized next-action recommendations
  • Auto-generate suggested files / skills on demand

Powered by OpenRouter + Qwen3-VL-235B-Thinking.
No Ollama. No GPU required.
"""

import json
import os
import gradio as gr

from services.repo_analyzer_service import (
    analyze_repo, generate_suggested_file, generate_missing_skill
)


# ── helpers ─────────────────────────────────────────────────────────────────

def _priority_emoji(p: str) -> str:
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(str(p).lower(), "⚪")


def _category_emoji(c: str) -> str:
    return {
        "security": "🔒", "agentic": "🤖", "azure-ai": "☁️",
        "code-quality": "🧹", "devops": "🚀", "responsible-ai": "🛡️",
    }.get(str(c).lower(), "💡")


def _render_analysis(result: dict) -> tuple[str, str, str, str, list]:
    """Convert analysis result into 4 markdown panels + skills list."""
    if "error" in result:
        err = f"❌ **Error:** {result['error']}"
        return err, "", "", "", []

    stats   = result.get("repo_stats", {})
    model   = result.get("model_used", "?")
    tokens  = result.get("tokens_used", "?")
    ana     = result.get("analysis", {})

    if "raw_response" in ana:
        return f"⚠️ Model returned non-JSON:\n```\n{ana['raw_response'][:2000]}\n```", "", "", "", []

    # ── Panel 1: Summary + stats ──────────────────────────────────────────
    lang_str = " · ".join(
        f"**{lang}**: {cnt}"
        for lang, cnt in sorted(stats.get("language_stats", {}).items(), key=lambda x: -x[1])
    )
    summary_md = f"""## 📊 Repository Report
*Model: `{model}` | Tokens used: {tokens}*

**Files scanned:** {stats.get('total_files', '?')} &nbsp;·&nbsp; **Files previewed:** {stats.get('files_previewed', '?')}

**Languages:** {lang_str or 'N/A'}

---

### 🧠 Project Summary
{ana.get('project_summary', 'N/A')}

---

### 🛠️ Detected Tech Stack
{chr(10).join(f'- `{t}`' for t in ana.get('detected_tech_stack', []))}

---

### ✅ Strengths
{chr(10).join(f'- {s}' for s in ana.get('strengths', []))}

---

### ⚡ Quick Wins (< 30 min each)
{chr(10).join(f'- {q}' for q in ana.get('quick_wins', []))}

---

### 🔍 Detected Patterns
{chr(10).join(f'- {p}' for p in ana.get('detected_patterns', []))}
"""

    # ── Panel 2: Nudges ───────────────────────────────────────────────────
    nudges = ana.get("nudges", [])
    nudge_md = "## 💡 Prioritized Nudges — What To Do Next\n\n"
    if not nudges:
        nudge_md += "*No nudges generated.*"
    else:
        for i, n in enumerate(nudges, 1):
            pe = _priority_emoji(n.get("priority", ""))
            ce = _category_emoji(n.get("category", ""))
            nudge_md += (
                f"### {pe} {i}. {n.get('action', 'Action')}\n"
                f"{ce} *{n.get('category', '').replace('-', ' ').title()}* · Priority: **{n.get('priority', '?').title()}**\n\n"
                f"{n.get('detail', '')}\n\n---\n\n"
            )

    # ── Panel 3: Files to create ──────────────────────────────────────────
    files = ana.get("files_to_create", [])
    files_md = "## 📁 Suggested Files to Create\n\n"
    if not files:
        files_md += "*No file suggestions.*"
    else:
        for f in files:
            pe = _priority_emoji(f.get("priority", ""))
            files_md += (
                f"### {pe} `{f.get('filename', '?')}`\n"
                f"**Priority:** {f.get('priority', '?').title()}\n\n"
                f"**Purpose:** {f.get('purpose', '')}\n\n"
                f"**Template hint:** *{f.get('template_hint', '')}*\n\n---\n\n"
            )

    # ── Panel 4: Missing skills ───────────────────────────────────────────
    skills = ana.get("missing_skills", [])
    skills_md = "## 🔧 Missing Claude Code Skills\n\n"
    if not skills:
        skills_md += "*No skill gaps detected.*"
    else:
        for s in skills:
            pe = _priority_emoji(s.get("priority", ""))
            skills_md += (
                f"### {pe} `{s.get('skill_name', '?')}`\n"
                f"**Priority:** {s.get('priority', '?').title()}\n\n"
                f"**Trigger:** {s.get('trigger', '')}\n\n"
                f"**Why needed:** {s.get('reason', '')}\n\n---\n\n"
            )

    return summary_md, nudge_md, files_md, skills_md, skills


# ── main analyze function ────────────────────────────────────────────────────

_last_analysis: dict = {}  # session cache


def analyze_fn(zip_file, extra_context: str):
    global _last_analysis
    if zip_file is None:
        return "⚠️ Please upload a ZIP file of your repository.", "", "", "", gr.update(choices=[])

    with open(zip_file.name, "rb") as f:
        zip_bytes = f.read()

    result = analyze_repo(zip_bytes, extra_context=extra_context)
    _last_analysis = result

    summary_md, nudge_md, files_md, skills_md, skills = _render_analysis(result)

    skill_choices = [
        f"{_priority_emoji(s.get('priority',''))} {s.get('skill_name','?')} — {s.get('trigger','')[:60]}"
        for s in skills
    ]
    file_choices = [
        f"{_priority_emoji(f.get('priority',''))} {f.get('filename','?')}"
        for f in result.get("analysis", {}).get("files_to_create", [])
    ]

    return summary_md, nudge_md, files_md, skills_md, gr.update(choices=skill_choices), gr.update(choices=file_choices)


def gen_skill_fn(selected_skill_label: str):
    if not selected_skill_label or not _last_analysis:
        return "⚠️ Run an analysis first, then select a skill."
    # Extract skill name from label
    raw_name = selected_skill_label.split(" ", 1)[-1].split(" — ")[0].strip()
    skills = _last_analysis.get("analysis", {}).get("missing_skills", [])
    skill = next((s for s in skills if s.get("skill_name", "") in raw_name), None)
    if not skill:
        return f"⚠️ Could not find skill: `{raw_name}`"
    summary = _last_analysis.get("analysis", {}).get("project_summary", "")
    result = generate_missing_skill(skill, repo_summary=summary)
    if "error" in result:
        return f"❌ {result['error']}"
    return result["content"]


def gen_file_fn(selected_file_label: str):
    if not selected_file_label or not _last_analysis:
        return "⚠️ Run an analysis first, then select a file."
    raw_name = selected_file_label.split(" ", 1)[-1].strip()
    files = _last_analysis.get("analysis", {}).get("files_to_create", [])
    file_info = next((f for f in files if f.get("filename", "") in raw_name), None)
    if not file_info:
        return f"⚠️ Could not find file info for: `{raw_name}`"
    result = generate_suggested_file(
        filename=file_info.get("filename", ""),
        purpose=file_info.get("purpose", ""),
        template_hint=file_info.get("template_hint", ""),
        repo_context=_last_analysis.get("analysis", {}).get("project_summary", ""),
    )
    if "error" in result:
        return f"❌ {result['error']}"
    return result["content"]


# ── tab builder ──────────────────────────────────────────────────────────────

def build_repo_analyzer_tab():
    with gr.Tab("🔍 Repo Analyzer"):
        gr.Markdown("""## 🔍 AI Repo Analyzer
Upload **any project as a ZIP file**. The AI will analyze your codebase and tell you:
- 🔧 **Which Claude Code skills** are missing and should be added
- 📁 **Which files** should be created (CLAUDE.md, skill templates, CI configs, etc.)
- 💡 **Prioritized nudges** — exactly what to do next and why
- ✅ **Strengths** — what your repo already does well

> ⚡ **Powered by OpenRouter + Qwen3-VL-235B-Thinking — no Ollama, no GPU, works on any laptop**
""")

        with gr.Row():
            with gr.Column(scale=2):
                zip_input = gr.File(
                    label="📦 Upload Repository ZIP",
                    file_types=[".zip"],
                    type="filepath",
                )
                extra_ctx = gr.Textbox(
                    label="💬 Extra Context (optional)",
                    placeholder="e.g. This is a FastAPI backend for an Azure AI chatbot. We want to add RAG and a CLAUDE.md.",
                    lines=3,
                )
                analyze_btn = gr.Button("🚀 Analyze Repository", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown("""### 💡 Tips
- ZIP your entire project folder
- Include `requirements.txt`, `package.json`, or `pyproject.toml`
- Include any existing `README.md` or `CLAUDE.md`
- Max size: **50 MB**

### 🔒 Privacy
Your files are analyzed in-memory only.
Nothing is stored permanently except the AI's summary.

### 🤖 Model
`qwen/qwen3-vl-235b-a22b-thinking`
via OpenRouter — **no GPU needed**""")

        with gr.Tabs():
            with gr.Tab("📊 Summary & Strengths"):
                summary_out = gr.Markdown(value="*Upload a ZIP and click Analyze to get started.*")

            with gr.Tab("💡 Nudges (What To Do Next)"):
                nudges_out = gr.Markdown(value="*Run analysis to see prioritized recommendations.*")

            with gr.Tab("📁 Files to Create"):
                files_out = gr.Markdown(value="*Run analysis to see file suggestions.*")
                gr.Markdown("---")
                gr.Markdown("### ⚡ Auto-Generate a Suggested File")
                file_dropdown = gr.Dropdown(label="Select a file to generate", choices=[], interactive=True)
                gen_file_btn  = gr.Button("✨ Generate File Content", variant="secondary")
                gen_file_out  = gr.Code(label="Generated File Content", language="python")
                gen_file_btn.click(gen_file_fn, file_dropdown, gen_file_out)

            with gr.Tab("🔧 Missing Skills"):
                skills_out = gr.Markdown(value="*Run analysis to see missing Claude Code skills.*")
                gr.Markdown("---")
                gr.Markdown("### ⚡ Auto-Generate a Missing SKILL.md")
                skill_dropdown = gr.Dropdown(label="Select a skill to generate", choices=[], interactive=True)
                gen_skill_btn  = gr.Button("✨ Generate SKILL.md", variant="secondary")
                gen_skill_out  = gr.Code(label="Generated SKILL.md", language="markdown")
                gen_skill_btn.click(gen_skill_fn, skill_dropdown, gen_skill_out)

        analyze_btn.click(
            analyze_fn,
            inputs=[zip_input, extra_ctx],
            outputs=[summary_out, nudges_out, files_out, skills_out, skill_dropdown, file_dropdown],
        )
