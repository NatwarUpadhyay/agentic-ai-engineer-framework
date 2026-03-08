"""
app.py — Agentic AI Engineer Framework
─────────────────────────────────────────────────────────────────────────────
Main Gradio application entry point.

  🚀 No Ollama required. No GPU required. Works on any laptop.
     Powered by OpenRouter + Qwen3-VL-235B-Thinking (cloud inference).

Usage:
    pip install -r requirements.txt
    cp .env.example .env        # fill in your keys (OpenRouter pre-configured)
    python app.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

import gradio as gr

from tabs.tab_home         import build_home_tab
from tabs.tab_repo_analyzer import build_repo_analyzer_tab
from tabs.tab_agentic      import build_agentic_tab
from tabs.tab_nlp          import build_nlp_tab
from tabs.tab_services     import (
    build_translation_tab,
    build_vision_tab,
    build_search_tab,
    build_safety_tab,
)
from tabs.tab_claude_toolkit import build_claude_toolkit_tab


# ── Custom CSS ───────────────────────────────────────────────────────────────

CUSTOM_CSS = """
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --surface: #1e1e2e;
    --surface-light: #2a2a3e;
    --text: #e2e8f0;
    --text-muted: #94a3b8;
    --border: #334155;
    --radius: 12px;
}

/* Global */
body, .gradio-container { background: #0f0f1a !important; color: var(--text) !important; }

/* Header banner */
.app-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #334155;
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
    text-align: center;
}
.app-banner h1 { font-size: 1.8rem; font-weight: 800; color: #818cf8; margin: 0; }
.app-banner p  { color: var(--text-muted); margin: 0.25rem 0 0; font-size: 0.9rem; }

/* Badge row */
.badge-row { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; margin-top: 0.75rem; }
.badge {
    background: #1e293b; border: 1px solid #334155; border-radius: 999px;
    padding: 0.2rem 0.75rem; font-size: 0.75rem; color: #94a3b8; font-weight: 500;
}
.badge.green  { border-color: #22c55e; color: #22c55e; background: #052e16; }
.badge.blue   { border-color: #3b82f6; color: #60a5fa; background: #0c1a3b; }
.badge.purple { border-color: #8b5cf6; color: #a78bfa; background: #1e1040; }

/* Tabs */
.tab-nav button {
    background: transparent !important; border: none !important;
    color: var(--text-muted) !important; font-weight: 500; font-size: 0.88rem;
    padding: 0.5rem 0.9rem; border-radius: 8px; transition: all 0.2s;
}
.tab-nav button:hover   { background: #1e293b !important; color: var(--text) !important; }
.tab-nav button.selected { background: #6366f1 !important; color: white !important; }

/* Buttons */
button.primary   { background: linear-gradient(135deg, #6366f1, #4f46e5) !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
button.secondary { background: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
button.stop      { background: linear-gradient(135deg, #ef4444, #dc2626) !important; border: none !important; border-radius: 8px !important; }

/* Inputs */
input, textarea, .input-text {
    background: var(--surface-light) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}
input:focus, textarea:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important; }

/* Code blocks */
.code-block, pre, code { background: #0d0d1a !important; border: 1px solid #1e293b !important; border-radius: 8px !important; }

/* Markdown */
.prose h1, .prose h2, .prose h3 { color: #818cf8 !important; }
.prose a { color: #60a5fa !important; }
.prose code { background: #1e293b !important; color: #a5b4fc !important; padding: 0.1rem 0.4rem; border-radius: 4px; }
.prose table { border-collapse: collapse; width: 100%; }
.prose th { background: #1e293b !important; color: #818cf8 !important; }
.prose td, .prose th { border: 1px solid #334155 !important; padding: 0.5rem 0.75rem; }
.prose tr:nth-child(even) { background: #0f172a !important; }

/* Status badge */
.model-badge {
    background: #052e16; border: 1px solid #22c55e;
    border-radius: 999px; padding: 0.15rem 0.6rem;
    font-size: 0.72rem; color: #22c55e; font-weight: 600;
    display: inline-block; margin-left: 0.5rem;
}
"""

BANNER_HTML = """
<div class="app-banner">
  <h1>🧠 Agentic AI Engineer Framework</h1>
  <p>Azure AI (AI-102) · NVIDIA Agentic Patterns · Claude Code Toolkit · OpenRouter LLM</p>
  <div class="badge-row">
    <span class="badge green">✅ No Ollama Required</span>
    <span class="badge green">✅ No GPU Needed</span>
    <span class="badge blue">☁️ OpenRouter Powered</span>
    <span class="badge purple">🤖 Qwen3-VL-235B-Thinking</span>
    <span class="badge">🔍 ZIP Repo Analyzer</span>
    <span class="badge">🏗️ Multi-Agent Pipeline</span>
    <span class="badge">🧠 Persistent Memory</span>
    <span class="badge">⚙️ Skill Generator</span>
  </div>
</div>
"""


# ── Build app ────────────────────────────────────────────────────────────────

def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="Agentic AI Engineer Framework",
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.indigo,
            secondary_hue=gr.themes.colors.slate,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Inter"),
        ),
        css=CUSTOM_CSS,
    ) as app:

        gr.HTML(BANNER_HTML)

        with gr.Tabs():
            build_home_tab()
            build_repo_analyzer_tab()
            build_agentic_tab()
            build_nlp_tab()
            build_translation_tab()
            build_vision_tab()
            build_search_tab()
            build_safety_tab()
            build_claude_toolkit_tab()

        # Footer
        gr.HTML("""
        <div style="text-align:center; padding:1.5rem; color:#475569; font-size:0.8rem; border-top:1px solid #1e293b; margin-top:1rem;">
          <strong style="color:#6366f1">Agentic AI Engineer Framework</strong>
          &nbsp;·&nbsp; Azure AI-102 &nbsp;·&nbsp; NVIDIA Agentic AI &nbsp;·&nbsp; Claude Code Toolkit
          <br/>
          <span style="color:#22c55e">✅ No Ollama &nbsp;·&nbsp; ✅ No GPU &nbsp;·&nbsp; ✅ Works on any laptop</span>
          &nbsp;·&nbsp; Powered by OpenRouter + Qwen3-VL-235B-Thinking
          <br/><br/>
          <em>Inspired by: OpenClaw · ChatDev 2.0 · Claude CoWork · NVIDIA AI Associate Certification</em>
        </div>
        """)

    return app


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False,
        show_error=True,
        favicon_path=None,
    )
