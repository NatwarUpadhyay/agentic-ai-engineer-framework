"""
tabs/tab_agentic.py — Agentic AI tab (ReAct, Multi-Agent, Planner, Memory, Skill Generator)
"""
import json
import gradio as gr

from services.agentic_service import (
    run_react_agent,
    run_multi_agent_pipeline,
    run_planner_agent,
    generate_agent_skill,
    add_memory_fact,
    retrieve_memory,
    clear_memory,
    get_nvidia_agentic_reference,
    AGENT_ROLES,
)


# ── helpers ────────────────────────────────────────────────────────────────

def _fmt_json(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _trace_to_md(trace: list) -> str:
    lines = []
    for step in trace:
        action = step.get("action", "")
        if "Tool Call" in action:
            lines.append(f"### 🔧 {action}")
            args = step.get("args", {})
            if args:
                lines.append(f"```json\n{json.dumps(args, indent=2)}\n```")
        elif "Tool Result" in action:
            lines.append(f"**Result:** `{step.get('output', '')}`\n")
        elif action == "Final Answer":
            lines.append(f"### ✅ Final Answer\n\n{step.get('output', '')}")
        else:
            lines.append(f"**{action}**")
    return "\n".join(lines)


# ── React Agent ─────────────────────────────────────────────────────────────

def react_agent_fn(goal: str, max_iter: int):
    if not goal.strip():
        return "⚠️ Please enter a goal.", ""
    result = run_react_agent(goal.strip(), max_iterations=int(max_iter))
    if "error" in result:
        return f"❌ {result['error']}", ""
    answer = result.get("final_answer", "No answer produced.")
    trace_md = _trace_to_md(result.get("trace", []))
    meta = f"\n\n---\n*Iterations: {result['iterations_used']} | Tokens: {result.get('tokens_used', '?')}*"
    return answer + meta, trace_md


# ── Multi-Agent Pipeline ─────────────────────────────────────────────────────

def multi_agent_fn(task: str, use_architect: bool, use_developer: bool, use_qa: bool, use_devops: bool):
    if not task.strip():
        return "⚠️ Please enter a task."
    selected = []
    if use_architect: selected.append("architect")
    if use_developer: selected.append("developer")
    if use_qa:        selected.append("qa")
    if use_devops:    selected.append("devops")
    if not selected:
        return "⚠️ Please select at least one agent."

    result = run_multi_agent_pipeline(task.strip(), selected_agents=selected)
    if "error" in result:
        return f"❌ {result['error']}"

    md = []
    for key, data in result["pipeline_results"].items():
        md.append(f"## {data['label']}\n\n{data['output']}\n\n---")
    md.append(f"*Total tokens used: {result['total_tokens']}*")
    return "\n\n".join(md)


# ── Planner Agent ────────────────────────────────────────────────────────────

def planner_fn(goal: str):
    if not goal.strip():
        return "⚠️ Please enter a goal.", ""
    result = run_planner_agent(goal.strip())
    if "error" in result:
        return f"❌ {result['error']}", ""

    plan = result.get("plan", {})
    raw_json = _fmt_json(plan)

    md = [f"# 📋 Plan: {plan.get('goal', goal)}\n"]
    md.append(f"**Complexity:** {plan.get('estimated_complexity', '?')}\n")

    for phase in plan.get("phases", []):
        md.append(f"## Phase {phase.get('phase')}: {phase.get('name', '')}")
        md.append(f"**Agent Role:** {phase.get('agent_role', '')} | **Est. Time:** {phase.get('estimated_time', '?')}")
        md.append("**Tasks:**")
        for t in phase.get("tasks", []):
            md.append(f"- {t}")
        svcs = phase.get("azure_services", [])
        if svcs:
            md.append(f"**Azure Services:** {', '.join(svcs)}")
        md.append("")

    risks = plan.get("risks", [])
    if risks:
        md.append("## ⚠️ Risks")
        for r in risks:
            md.append(f"- {r}")

    criteria = plan.get("success_criteria", [])
    if criteria:
        md.append("\n## ✅ Success Criteria")
        for c in criteria:
            md.append(f"- {c}")

    md.append(f"\n*Tokens used: {result.get('tokens_used', '?')}*")
    return "\n".join(md), raw_json


# ── Memory ──────────────────────────────────────────────────────────────────

def memory_add_fn(fact: str):
    if not fact.strip():
        return "⚠️ Enter a fact to remember.", memory_view_fn("")
    result = add_memory_fact(fact.strip(), source="user")
    return f"✅ {result['status']}", memory_view_fn("")


def memory_view_fn(query: str):
    result = retrieve_memory(query.strip())
    facts = result.get("matching_facts", [])
    if not facts:
        return f"*No facts stored yet. Total sessions logged: {result['sessions_logged']}*"
    lines = [f"**Total facts:** {result['total_facts']} | **Sessions:** {result['sessions_logged']}\n"]
    for f in facts:
        lines.append(f"- **[{f['id']}]** {f['fact']} *(source: {f['source']}, {f['timestamp'][:10]})*")
    skills = result.get("skills_learned", [])
    if skills:
        lines.append(f"\n**🔧 Skills generated:** {', '.join(s['name'] for s in skills)}")
    return "\n".join(lines)


def memory_clear_fn():
    result = clear_memory()
    return result["status"], "*Memory cleared.*"


# ── Skill Generator ──────────────────────────────────────────────────────────

def skill_gen_fn(name: str, trigger: str, tech: str):
    if not name.strip():
        return "⚠️ Enter a skill name."
    result = generate_agent_skill(name.strip(), trigger.strip(), tech.strip())
    if "error" in result:
        return f"❌ {result['error']}"
    saved = f"\n\n---\n*Saved to: `{result.get('file', '03-claude-code-toolkit/skills/')}`*"
    return result.get("skill_content", "") + saved


# ── NVIDIA Reference ──────────────────────────────────────────────────────────

def nvidia_ref_fn():
    data = get_nvidia_agentic_reference()
    md = ["# 🟢 NVIDIA Agentic AI Ecosystem Reference\n"]
    for key, section in data.items():
        md.append(f"## {section.get('label', key)}")
        md.append(f"*{section.get('description', '')}*\n")

        if "use_cases" in section:
            md.append("**Use Cases:**")
            for uc in section["use_cases"]:
                md.append(f"- {uc}")

        if "azure_integration" in section:
            md.append(f"\n**Azure Integration:** {section['azure_integration']}")

        if "tiers" in section:
            md.append("**Memory Tiers:**")
            for tier, desc in section["tiers"].items():
                md.append(f"- **{tier.replace('_', ' ').title()}:** {desc}")

        if "patterns" in section:
            md.append("**Patterns:**")
            for pname, desc in section["patterns"].items():
                md.append(f"- **{pname.replace('_', ' ').title()}:** {desc}")

        md.append("")

    md.append("""---
## 🔗 Why NVIDIA + Azure AI?

> *"This certification helped me build a strong foundation in designing and deploying
> Agentic AI systems using NVIDIA's ecosystem. I learned to create LLM-powered agents
> with memory, planning, and tool use, and explored multi-agent workflows and automation.
> I have been applying these concepts in my Agentic AI projects to build more practical,
> scalable solutions and continue improving my skills through hands-on implementation
> and experimentation."*

| NVIDIA Component | Azure Counterpart | Combined Benefit |
|---|---|---|
| NIM Inference | Azure OpenAI | GPU-optimized LLM endpoints |
| NeMo Guardrails | Azure Content Safety | Layered AI safety |
| cuVS Vector Search | Azure AI Search | Ultra-fast RAG retrieval |
| NeMo Framework | Azure ML | Custom model training |
| Triton Inference | AKS + GPU nodes | Scalable model serving |
""")
    return "\n".join(md)


# ── Tab Builder ──────────────────────────────────────────────────────────────

def build_agentic_tab():
    with gr.Tab("🤖 Agentic AI"):
        gr.Markdown("""## 🤖 Agentic AI Engine
LLM-powered agents with **memory**, **planning**, **tool use**, and **multi-agent orchestration**.
Patterns from NVIDIA AI certification + OpenClaw + ChatDev 2.0 + Anthropic Agent SDK.""")

        with gr.Tabs():

            # ── ReAct Agent ──────────────────────────────────────────────
            with gr.Tab("⚡ ReAct Agent"):
                gr.Markdown("""### ⚡ ReAct Agent (Reason + Act Loop)
Give the agent a goal. It will **think → use tools → observe → repeat** until it has a complete answer.
Tools available: `search_knowledge_base`, `remember_fact`, `recall_memory`, `generate_code`, `analyze_text`, `plan_azure_architecture`""")
                with gr.Row():
                    with gr.Column(scale=3):
                        react_goal = gr.Textbox(
                            label="🎯 Agent Goal",
                            placeholder="e.g. Design a RAG pipeline for a multilingual e-commerce chatbot using Azure AI",
                            lines=3,
                        )
                    with gr.Column(scale=1):
                        react_max_iter = gr.Slider(1, 8, value=4, step=1, label="Max Iterations")

                react_btn = gr.Button("🚀 Run ReAct Agent", variant="primary")
                with gr.Row():
                    with gr.Column():
                        react_answer = gr.Markdown(label="✅ Final Answer")
                    with gr.Column():
                        react_trace = gr.Markdown(label="🔍 Agent Trace (Tool Calls)")

                react_btn.click(react_agent_fn, [react_goal, react_max_iter], [react_answer, react_trace])

                gr.Markdown("""---
**📌 Try these goals:**
- *"Design an Azure RAG pipeline with private endpoints and managed identity"*
- *"What are the SLA requirements for Azure Cognitive Search high availability?"*
- *"Generate Python code for calling Azure AI Language sentiment analysis"*
- *"Remember that our Azure resources use the prefix prod-ai- in eastus region"*
""")

            # ── Multi-Agent Pipeline ──────────────────────────────────────
            with gr.Tab("🏭 Multi-Agent Pipeline"):
                gr.Markdown("""### 🏭 Multi-Agent Pipeline (ChatDev 2.0 Style)
Specialist agents tackle your task in sequence: **Architect → Developer → QA → DevOps**.
Each agent sees the previous agent's output as context — just like a real engineering team.""")

                multi_task = gr.Textbox(
                    label="📋 Task / Project Brief",
                    placeholder="e.g. Build a multilingual product search chatbot using Azure OpenAI + Cognitive Search with 99.9% SLA",
                    lines=4,
                )
                with gr.Row():
                    use_arch = gr.Checkbox(value=True, label="🏗️ Architect Agent")
                    use_dev  = gr.Checkbox(value=True, label="👨‍💻 Developer Agent")
                    use_qa   = gr.Checkbox(value=True, label="🧪 QA Agent")
                    use_ops  = gr.Checkbox(value=True, label="🚀 DevOps Agent")

                multi_btn = gr.Button("▶️ Run Pipeline", variant="primary")
                multi_out = gr.Markdown(label="Pipeline Output")

                multi_btn.click(multi_agent_fn, [multi_task, use_arch, use_dev, use_qa, use_ops], multi_out)

            # ── Planner Agent ─────────────────────────────────────────────
            with gr.Tab("🗺️ Planner Agent"):
                gr.Markdown("""### 🗺️ Planner Agent
Decomposes a high-level goal into a **structured, phased task plan** with agent roles, Azure services, dependencies, and success criteria.
Inspired by NVIDIA's LLM planning research and tree-of-thought prompting.""")

                plan_goal = gr.Textbox(
                    label="🎯 High-Level Goal",
                    placeholder="e.g. Build and deploy a production RAG system for a legal document Q&A chatbot on Azure",
                    lines=3,
                )
                plan_btn = gr.Button("📋 Generate Plan", variant="primary")
                with gr.Row():
                    with gr.Column(scale=2):
                        plan_md = gr.Markdown(label="Structured Plan")
                    with gr.Column(scale=1):
                        plan_json = gr.Code(label="Raw JSON Plan", language="json")

                plan_btn.click(planner_fn, plan_goal, [plan_md, plan_json])

            # ── Persistent Memory ─────────────────────────────────────────
            with gr.Tab("🧠 Agent Memory"):
                gr.Markdown("""### 🧠 Persistent Agent Memory
Three-tier memory model (NVIDIA AI certified pattern):
- **Working memory** — current context window
- **Episodic memory** — session logs (auto-saved after each agent run)
- **Semantic memory** — long-term facts stored below (persists across restarts)""")

                with gr.Row():
                    with gr.Column():
                        mem_fact_input = gr.Textbox(
                            label="💾 Store a Fact",
                            placeholder="e.g. Our Azure resources use prefix prod-ai- in eastus region",
                            lines=2,
                        )
                        mem_add_btn = gr.Button("💾 Remember", variant="primary")
                        mem_status = gr.Markdown()

                    with gr.Column():
                        mem_query = gr.Textbox(label="🔎 Search Memory", placeholder="keyword filter (optional)")
                        mem_view_btn = gr.Button("📖 Recall Memory")
                        mem_clear_btn = gr.Button("🗑️ Clear All Memory", variant="stop")

                mem_view = gr.Markdown(label="Memory Contents", value="*Click 'Recall Memory' to view stored facts.*")

                mem_add_btn.click(memory_add_fn, mem_fact_input, [mem_status, mem_view])
                mem_view_btn.click(memory_view_fn, mem_query, mem_view)
                mem_clear_btn.click(memory_clear_fn, outputs=[mem_status, mem_view])

            # ── Skill Generator ───────────────────────────────────────────
            with gr.Tab("🔧 Skill Generator"):
                gr.Markdown("""### 🔧 Self-Extending Agent — Skill Generator
Generate Claude Code `SKILL.md` files automatically (OpenClaw-inspired pattern).
The agent writes its own skills — saved to `03-claude-code-toolkit/skills/`.""")

                with gr.Row():
                    skill_name = gr.Textbox(label="Skill Name", placeholder="e.g. azure-rag-pipeline")
                    skill_trigger = gr.Textbox(label="Trigger Description", placeholder="e.g. when user wants to build a RAG system on Azure")

                skill_tech = gr.Textbox(
                    label="Tech Context",
                    placeholder="e.g. Azure OpenAI GPT-4o, Azure AI Search, Python SDK, vector index",
                )
                skill_btn = gr.Button("✨ Generate SKILL.md", variant="primary")
                skill_out = gr.Code(label="Generated SKILL.md", language="markdown")
                skill_btn.click(skill_gen_fn, [skill_name, skill_trigger, skill_tech], skill_out)

            # ── NVIDIA Reference ──────────────────────────────────────────
            with gr.Tab("🟢 NVIDIA Ecosystem"):
                gr.Markdown("### 🟢 NVIDIA Agentic AI Ecosystem Reference")
                nvidia_btn = gr.Button("Load NVIDIA Reference", variant="secondary")
                nvidia_out = gr.Markdown()
                nvidia_btn.click(nvidia_ref_fn, outputs=nvidia_out)
                # Auto-load on render
                nvidia_out.value = nvidia_ref_fn()
