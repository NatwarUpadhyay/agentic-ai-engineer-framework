"""
tabs/tab_claude_toolkit.py — Claude Code Toolkit tab
"""
import gradio as gr
from services.openrouter_service import simple_prompt, DEFAULT_MODEL


HOOK_TEMPLATES = {
    "Stop — Auto-summary on session end": """{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python ~/.claude/hooks/summarize_session.py >> ~/.claude/logs/session-summary.md"
      }]
    }]
  }
}""",
    "PreToolUse — Block dangerous commands": """{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "if [[ \\"$CLAUDE_TOOL_INPUT\\" == *\\"rm -rf\\"* || \\"$CLAUDE_TOOL_INPUT\\" == *\\"DROP TABLE\\"* ]]; then echo 'BLOCKED: destructive command' && exit 1; fi"
      }]
    }]
  }
}""",
    "SessionStart — Load Azure context": """{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "az account show > /tmp/azure-context.json && echo 'Azure context loaded'"
      }]
    }]
  }
}""",
    "PostToolUse — Auto-format Python": """{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "if [[ \\"$CLAUDE_FILE_PATHS\\" =~ \\.py$ ]]; then ruff format \\"$CLAUDE_FILE_PATHS\\"; fi"
      }]
    }]
  }
}""",
}


def gen_claude_md_fn(project: str, stack: str, conventions: str, forbidden: str):
    if not project.strip():
        return "⚠️ Enter a project name."
    system = "You are an expert AI engineer. Generate a complete, production-ready CLAUDE.md file. Return only the raw markdown."
    prompt = f"""Generate a CLAUDE.md for:
Project: {project}
Tech Stack: {stack}
Conventions: {conventions}
Forbidden Actions: {forbidden}

Include: Project Overview, Tech Stack, Conventions, Environment Variables, Useful Commands, Forbidden Actions, Agent Patterns (if applicable)."""
    return simple_prompt(prompt, system=system, max_tokens=2000)


def gen_skill_md_fn(name: str, trigger: str, tech: str):
    if not name.strip():
        return "⚠️ Enter a skill name."
    system = "You are an expert in Claude Code. Generate a complete SKILL.md. Return only raw markdown, no code fences."
    prompt = (f"Skill Name: {name}\nTrigger: {trigger}\nTech: {tech}\n\n"
              "Format with: ---frontmatter---, ## Context, ## Prerequisites, ## Steps, ## Constraints, ## Expected Output")
    return simple_prompt(prompt, system=system, max_tokens=1500)


def hook_template_fn(template_name: str):
    return HOOK_TEMPLATES.get(template_name, "Select a template above.")


def gen_custom_hook_fn(event: str, description: str):
    if not event or not description:
        return "⚠️ Fill in event type and description."
    system = "You are an expert in Claude Code hooks. Generate a hook settings.json snippet. Return only valid JSON."
    prompt = f"Generate a Claude Code hook for:\nEvent: {event}\nBehavior: {description}"
    return simple_prompt(prompt, system=system, max_tokens=800)


def build_claude_toolkit_tab():
    with gr.Tab("⚙️ Claude Toolkit"):
        gr.Markdown("""## ⚙️ Claude Code Toolkit
Generate `CLAUDE.md` project files, `SKILL.md` skill definitions, and hook configurations.
*All generation powered by OpenRouter + Qwen3-VL-235B — no Ollama, no GPU needed.*""")

        with gr.Tabs():

            with gr.Tab("📄 CLAUDE.md Generator"):
                gr.Markdown("""### Generate your `CLAUDE.md`
This is the most important file in any Claude Code project — loaded automatically at session start.""")
                with gr.Row():
                    with gr.Column():
                        p_name  = gr.Textbox(label="Project Name", placeholder="e.g. Azure RAG Chatbot")
                        p_stack = gr.Textbox(label="Tech Stack", placeholder="e.g. Python 3.11, Azure OpenAI, FastAPI, Azure AI Search")
                        p_conv  = gr.Textbox(label="Conventions", placeholder="e.g. All resources use prefix prod-ai-, use ruff for linting", lines=2)
                        p_forb  = gr.Textbox(label="Forbidden Actions", placeholder="e.g. Never delete resources without confirmation, never hardcode keys", lines=2)
                        claude_btn = gr.Button("✨ Generate CLAUDE.md", variant="primary")
                    with gr.Column():
                        claude_out = gr.Code(label="Generated CLAUDE.md", language="markdown")

                claude_btn.click(gen_claude_md_fn, [p_name, p_stack, p_conv, p_forb], claude_out)

            with gr.Tab("🔧 SKILL.md Generator"):
                gr.Markdown("""### Generate a Claude Code Skill
Skills are reusable instruction sets — define once, invoke anywhere.""")
                with gr.Row():
                    with gr.Column():
                        s_name    = gr.Textbox(label="Skill Name", placeholder="e.g. azure-rag-pipeline")
                        s_trigger = gr.Textbox(label="Trigger", placeholder="e.g. when user wants to build a RAG system on Azure")
                        s_tech    = gr.Textbox(label="Tech Context", placeholder="e.g. Azure OpenAI, Azure AI Search, Python SDK, vector index", lines=2)
                        skill_btn = gr.Button("✨ Generate SKILL.md", variant="primary")
                    with gr.Column():
                        skill_out = gr.Code(label="Generated SKILL.md", language="markdown")

                skill_btn.click(gen_skill_md_fn, [s_name, s_trigger, s_tech], skill_out)

            with gr.Tab("🪝 Hook Templates"):
                gr.Markdown("""### Claude Code Hooks
**8 Hook Events:** `UserPromptSubmit` · `PreToolUse` · `PostToolUse` · `PermissionRequest` · `Stop` · `SubagentStop` · `PreCompact` · `SessionStart`

> 💡 Hooks don't cost tokens — they're shell commands. Use them for logging, validation, formatting, and safety.""")

                hook_select = gr.Dropdown(
                    choices=list(HOOK_TEMPLATES.keys()),
                    label="Select a hook template",
                    value=list(HOOK_TEMPLATES.keys())[0],
                )
                hook_out = gr.Code(label="Hook JSON", language="json", value=list(HOOK_TEMPLATES.values())[0])
                hook_select.change(hook_template_fn, hook_select, hook_out)

                gr.Markdown("---\n### 🔧 Generate a Custom Hook")
                with gr.Row():
                    h_event = gr.Dropdown(
                        choices=["UserPromptSubmit", "PreToolUse", "PostToolUse", "PermissionRequest",
                                 "Stop", "SubagentStop", "PreCompact", "SessionStart"],
                        label="Hook Event",
                    )
                    h_desc = gr.Textbox(label="What should this hook do?", placeholder="e.g. Log all file edits to a CSV audit file")
                custom_hook_btn = gr.Button("✨ Generate Hook", variant="secondary")
                custom_hook_out = gr.Code(label="Custom Hook JSON", language="json")
                custom_hook_btn.click(gen_custom_hook_fn, [h_event, h_desc], custom_hook_out)

            with gr.Tab("📚 Reference"):
                gr.Markdown("""### Claude Code Skills Reference

| Skill | Purpose |
|---|---|
| `azure-vision-indexer` | Process images through Computer Vision + store insights |
| `adaptive-card-builder` | Generate Bot Framework Adaptive Cards from JSON |
| `multilingual-translator` | Language detect → translate → store all language variants |
| `rag-pipeline` | Chunk, embed, and index documents for RAG on Azure OpenAI |
| `cognitive-search-setup` | Scaffold end-to-end indexer + skillset pipeline |
| `content-safety-guard` | Add Azure AI Content Safety to any AI pipeline |
| `managed-identity-setup` | Replace API keys with Managed Identity across the project |

---

### Skill File Structure
```
03-claude-code-toolkit/
└── skills/
    ├── azure-rag-pipeline.md      ← generated skills appear here
    ├── cognitive-search-setup.md
    └── ...
```

### Installation to Claude Code
```bash
cp -r 03-claude-code-toolkit/skills/ ~/.claude/skills/
cp 03-claude-code-toolkit/hooks/settings.json ~/.claude/settings.json
claude   # CLAUDE.md is auto-loaded
```""")
