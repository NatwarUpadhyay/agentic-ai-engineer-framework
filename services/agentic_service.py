"""
services/agentic_service.py
─────────────────────────────────────────────────────────────────────────────
Agentic AI Engine — LLM-powered agents with memory, planning, tool use,
and multi-agent orchestration.

Inspired by:
  • NVIDIA NIM / NeMo Guardrails agentic patterns
  • OpenClaw persistent local-agent architecture
  • ChatDev 2.0 multi-agent ChatChain
  • Anthropic Claude Agent SDK patterns

This module covers the full agentic lifecycle:
  1. Single agent with memory + tool use
  2. Planner → executor loop (ReAct-style)
  3. Multi-agent orchestration (Orchestrator + Specialists)
  4. Persistent memory across sessions
  5. Self-extending agents (agents that write their own skills)
"""

import os
import json
import uuid
from datetime import datetime
from typing import Any

from services.openrouter_service import chat as or_chat, simple_prompt, DEFAULT_MODEL


def _llm(messages: list, temperature: float = 0.4, max_tokens: int = 2048,
         tools: list = None, tool_choice: str = "auto") -> dict:
    """
    Primary LLM call via OpenRouter (Qwen3-VL-235B-Thinking).
    Falls back to Azure OpenAI if AZURE_OPENAI_KEY is set.
    No Ollama. No GPU. Works on any machine.
    """
    azure_key = os.getenv("AZURE_OPENAI_KEY", "")
    if azure_key and tools:
        # Tool-use still needs Azure OpenAI (OpenRouter function calling varies by model)
        from services.openai_service import get_openai_client
        client = get_openai_client()
        if client:
            deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            resp = client.chat.completions.create(
                model=deployment, messages=messages,
                tools=[{"type": "function", "function": t} for t in tools],
                tool_choice=tool_choice, temperature=temperature, max_tokens=max_tokens,
            )
            return {"_azure_response": resp}

    # OpenRouter path (default)
    return or_chat(messages, model=DEFAULT_MODEL, temperature=temperature, max_tokens=max_tokens)

# ─────────────────────────────────────────────
# AGENT MEMORY — Persistent across-session state
# ─────────────────────────────────────────────

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "agent_memory.json")


def _load_memory() -> dict:
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"sessions": [], "facts": [], "skills_learned": []}


def _save_memory(memory: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def add_memory_fact(fact: str, source: str = "user") -> dict:
    """Persist a fact to the agent's long-term memory store."""
    memory = _load_memory()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "fact": fact,
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
    }
    memory["facts"].append(entry)
    _save_memory(memory)
    return {"status": "✅ Fact stored in agent memory", "entry": entry}


def retrieve_memory(query: str = "") -> dict:
    """Retrieve all facts from agent memory, optionally filtered by keyword."""
    memory = _load_memory()
    facts = memory.get("facts", [])
    if query:
        facts = [f for f in facts if query.lower() in f["fact"].lower()]
    return {
        "total_facts": len(memory.get("facts", [])),
        "matching_facts": facts,
        "sessions_logged": len(memory.get("sessions", [])),
        "skills_learned": memory.get("skills_learned", []),
    }


def clear_memory() -> dict:
    _save_memory({"sessions": [], "facts": [], "skills_learned": []})
    return {"status": "🗑️ Agent memory cleared."}


# ─────────────────────────────────────────────
# BUILT-IN AGENT TOOLS
# ─────────────────────────────────────────────

AGENT_TOOLS: list[dict] = [
    {
        "name": "search_knowledge_base",
        "description": "Search the internal knowledge base for relevant information on a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "top_k": {"type": "integer", "description": "Number of results to return", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "remember_fact",
        "description": "Store an important fact or insight into long-term agent memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "The fact to remember"},
            },
            "required": ["fact"],
        },
    },
    {
        "name": "recall_memory",
        "description": "Retrieve previously stored facts from agent memory.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Optional keyword to filter memories"},
            },
            "required": [],
        },
    },
    {
        "name": "generate_code",
        "description": "Generate Python code for a given task or Azure AI integration.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Description of the code to generate"},
                "language": {"type": "string", "description": "Programming language", "default": "python"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "analyze_text",
        "description": "Analyze text for sentiment, key phrases, entities, or PII.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
                "analysis_type": {
                    "type": "string",
                    "enum": ["sentiment", "key_phrases", "entities", "pii"],
                    "description": "Type of analysis",
                },
            },
            "required": ["text", "analysis_type"],
        },
    },
    {
        "name": "plan_azure_architecture",
        "description": "Design an Azure AI architecture for a given use case.",
        "parameters": {
            "type": "object",
            "properties": {
                "use_case": {"type": "string", "description": "The AI use case to architect for"},
                "requirements": {"type": "string", "description": "Non-functional requirements (SLA, region, etc.)"},
            },
            "required": ["use_case"],
        },
    },
]


def _execute_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if tool_name == "remember_fact":
        result = add_memory_fact(tool_args.get("fact", ""), source="agent")
        return json.dumps(result)

    elif tool_name == "recall_memory":
        result = retrieve_memory(tool_args.get("keyword", ""))
        return json.dumps(result)

    elif tool_name == "search_knowledge_base":
        # Simulate knowledge base search with built-in framework knowledge
        query = tool_args.get("query", "").lower()
        kb = _get_framework_kb()
        results = [v for k, v in kb.items() if any(w in k for w in query.split())][:tool_args.get("top_k", 3)]
        return json.dumps({"results": results or ["No specific match found — answer from general knowledge."]})

    elif tool_name == "generate_code":
        content = simple_prompt(
            f"Generate {tool_args.get('language', 'Python')} code for: {tool_args.get('task', '')}",
            system="You are an expert Azure AI engineer. Generate clean, production-ready code with comments.",
            max_tokens=1024,
        )
        return content

    elif tool_name == "analyze_text":
        return json.dumps({
            "note": "Text analysis via Azure AI Language — configure AZURE_LANGUAGE_KEY to get live results.",
            "text_preview": tool_args.get("text", "")[:80],
            "analysis_type": tool_args.get("analysis_type"),
        })

    elif tool_name == "plan_azure_architecture":
        content = simple_prompt(
            f"Design an Azure AI architecture for: {tool_args.get('use_case', '')}\nRequirements: {tool_args.get('requirements', 'Standard')}",
            system="You are an Azure Solutions Architect specializing in AI. Design practical, production-grade Azure AI architectures.",
            max_tokens=1200,
        )
        return content

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _get_framework_kb() -> dict:
    """Embedded framework knowledge base for agent tool searches."""
    return {
        "rag pattern": "RAG = Query → Embed → Search → Retrieve → Augment → Generate. Tools: Azure OpenAI embeddings + Azure AI Search vector index.",
        "cognitive search sla": "99.9% reads: 1 replica. 99.9% reads+writes: 2 replicas. HA+partition: 3 replicas + 2 partitions.",
        "claude skill": "Skills are SKILL.md files with: name, description, triggers, context, steps, constraints. Reusable across sessions.",
        "claude hooks": "8 hook types: UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, SubagentStop, PreCompact, SessionStart.",
        "agentic patterns": "Core patterns: OpenClaw (persistent local), ChatDev 2.0 (ChatChain multi-agent), RAG, Orchestrator+Specialists.",
        "nvidia agentic": "NVIDIA NIM: inference microservices. NeMo Guardrails: safety rails for agents. cuVS: GPU-accelerated vector search.",
        "managed identity": "Use Managed Identity instead of API keys. Assign roles (RBAC) at resource scope. No secrets in code.",
        "responsible ai": "Checklist: private endpoints, managed identity, content safety filters, PII detection, audit logs, human-in-the-loop.",
        "orchestrator pattern": "Orchestrator routes to specialists: Research Agent → Coder Agent → Reviewer Agent → Publisher Agent.",
        "nlp services": "Azure AI Language: sentiment, NER, key phrases, PII. Translator: 100+ languages. CLU replaced LUIS. CQA replaced QnA Maker.",
    }


# ─────────────────────────────────────────────
# SINGLE AGENT — ReAct-style (Reason + Act loop)
# ─────────────────────────────────────────────

def run_react_agent(user_goal: str, max_iterations: int = 5) -> dict:
    """
    ReAct Agent — Reason + Act loop via OpenRouter (Qwen3-VL-235B-Thinking).
    No Ollama. No GPU. Works on any machine.
    Uses a simulated tool-use loop since we stringify tool dispatch manually.
    """
    system_prompt = """You are an expert Agentic AI Engineer with deep knowledge of:
- Azure AI Services (AI-102 certified level)
- NVIDIA NIM / NeMo Guardrails agentic patterns
- OpenClaw-style persistent local agents
- ChatDev 2.0 multi-agent orchestration
- LLM agents with memory, planning, and tool use

Available tools (call by writing TOOL_CALL: tool_name | arg_json on its own line):
- search_knowledge_base | {"query": "..."}
- remember_fact         | {"fact": "..."}
- recall_memory         | {"keyword": "..."}
- generate_code         | {"task": "...", "language": "python"}
- plan_azure_architecture | {"use_case": "...", "requirements": "..."}

Reason step-by-step. Use tools when needed. Write FINAL_ANSWER: on its own line when done."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_goal},
    ]

    trace = []
    iteration = 0
    last_content = ""

    import re as _re

    while iteration < max_iterations:
        iteration += 1
        result = or_chat(messages, model=DEFAULT_MODEL, temperature=0.35, max_tokens=1500)
        if "error" in result:
            return {"error": result["error"]}

        content = result["content"]
        last_content = content
        messages.append({"role": "assistant", "content": content})

        # Check for FINAL_ANSWER
        if "FINAL_ANSWER:" in content:
            answer = content.split("FINAL_ANSWER:", 1)[-1].strip()
            trace.append({"iteration": iteration, "action": "Final Answer", "output": answer})
            last_content = answer
            break

        # Parse any TOOL_CALL lines
        tool_calls = _re.findall(r"TOOL_CALL:\s*(\w+)\s*\|\s*(\{.*?\})", content, _re.DOTALL)
        if not tool_calls:
            # No tool call and no final answer — treat response as final
            trace.append({"iteration": iteration, "action": "Final Answer", "output": content})
            break

        for tool_name, args_str in tool_calls:
            try:
                tool_args = json.loads(args_str)
            except Exception:
                tool_args = {}
            trace.append({"iteration": iteration, "action": f"Tool Call → {tool_name}", "args": tool_args})
            tool_result = _execute_tool(tool_name, tool_args)
            short = tool_result[:300] + "..." if len(tool_result) > 300 else tool_result
            trace.append({"iteration": iteration, "action": f"Tool Result ← {tool_name}", "output": short})
            messages.append({"role": "user", "content": f"Tool result for {tool_name}:\n{tool_result}"})

    # Log session
    memory = _load_memory()
    memory["sessions"].append({
        "id": str(uuid.uuid4())[:8],
        "goal": user_goal,
        "iterations": iteration,
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save_memory(memory)

    final = next((t["output"] for t in reversed(trace) if t["action"] == "Final Answer"), last_content)
    return {
        "goal": user_goal,
        "iterations_used": iteration,
        "final_answer": final,
        "trace": trace,
        "tokens_used": result.get("usage", {}).get("total_tokens", "?"),
    }


# ─────────────────────────────────────────────
# MULTI-AGENT ORCHESTRATOR — ChatDev 2.0 style
# ─────────────────────────────────────────────

AGENT_ROLES = {
    "architect": {
        "emoji": "🏗️",
        "label": "Architect Agent",
        "system_prompt": """You are a Senior Azure AI Solutions Architect (AI-102 certified).
Your role: Design Azure resource topologies, select the right AI services, and define the system architecture.
Be specific about: service tiers, regions, networking (private endpoints), identity (managed identity), and scalability.""",
    },
    "developer": {
        "emoji": "👨‍💻",
        "label": "Developer Agent",
        "system_prompt": """You are a Senior Azure AI Developer specializing in Python and Azure SDKs.
Your role: Write production-ready code, Azure Bicep/Terraform IaC, and implement AI pipelines.
Focus on: clean code, error handling, environment variable config, and Azure best practices.""",
    },
    "qa": {
        "emoji": "🧪",
        "label": "QA Agent",
        "system_prompt": """You are a QA Engineer specializing in AI system testing.
Your role: Review the architecture and code for issues, generate test cases, and validate AI outputs.
Check for: security gaps, missing error handling, PII leakage, content safety, and performance issues.""",
    },
    "devops": {
        "emoji": "🚀",
        "label": "DevOps Agent",
        "system_prompt": """You are a DevOps/MLOps engineer specializing in Azure AI deployments.
Your role: Define CI/CD pipelines, monitoring strategies, deployment configs, and operational runbooks.
Focus on: Azure DevOps/GitHub Actions, Azure Monitor, Application Insights, and responsible AI governance.""",
    },
}


def run_multi_agent_pipeline(task: str, selected_agents: list[str] = None) -> dict:
    """
    ChatDev 2.0-style multi-agent pipeline via OpenRouter.
    Architect → Developer → QA → DevOps, each seeing prior output as context.
    """
    agents_to_run = selected_agents or ["architect", "developer", "qa", "devops"]
    pipeline_results = {}
    accumulated_context = f"ORIGINAL TASK:\n{task}\n"

    for agent_key in agents_to_run:
        if agent_key not in AGENT_ROLES:
            continue
        role = AGENT_ROLES[agent_key]
        user_msg = (f"{accumulated_context}\n\nYour turn as {role['label']}. "
                    "Based on everything above, provide your expert contribution. "
                    "Be specific, actionable, and production-ready.")
        result = or_chat(
            [{"role": "system", "content": role["system_prompt"]},
             {"role": "user",   "content": user_msg}],
            model=DEFAULT_MODEL, temperature=0.4, max_tokens=1500,
        )
        if "error" in result:
            output = f"❌ {result['error']}"
            tokens = 0
        else:
            output = result["content"]
            tokens = result.get("usage", {}).get("total_tokens", 0)

        pipeline_results[agent_key] = {
            "label": f"{role['emoji']} {role['label']}",
            "output": output,
            "tokens": tokens,
        }
        accumulated_context += f"\n\n{'='*60}\n{role['label'].upper()} OUTPUT:\n{output}"

    return {
        "task": task,
        "agents_run": agents_to_run,
        "pipeline_results": pipeline_results,
        "total_tokens": sum(v.get("tokens", 0) for v in pipeline_results.values()),
    }


# ─────────────────────────────────────────────
# PLANNER AGENT — Goal decomposition + task graph
# ─────────────────────────────────────────────

def run_planner_agent(goal: str) -> dict:
    """Planner Agent — decomposes a goal into a structured JSON task plan via OpenRouter."""
    import re as _re
    system_prompt = """You are an expert AI Planner Agent.
Decompose the given goal into a structured task plan.
Return ONLY valid JSON with this structure:
{
  "goal": "...", "estimated_complexity": "Low|Medium|High",
  "phases": [{"phase": 1, "name": "...", "agent_role": "...",
              "tasks": [], "azure_services": [], "dependencies": [], "estimated_time": "..."}],
  "risks": [], "success_criteria": []
}"""
    result = or_chat(
        [{"role": "system", "content": system_prompt},
         {"role": "user",   "content": f"Decompose this goal:\n{goal}"}],
        model=DEFAULT_MODEL, temperature=0.2, max_tokens=2000,
    )
    if "error" in result:
        return {"error": result["error"]}

    raw = result["content"].strip()
    raw = _re.sub(r"<think>.*?</think>", "", raw, flags=_re.DOTALL).strip()
    if raw.startswith("```"):
        raw = "\n".join(l for l in raw.split("\n") if not l.strip().startswith("```")).strip()
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        m = _re.search(r"\{[\s\S]+\}", raw)
        plan = json.loads(m.group()) if m else {"raw": raw}

    return {"status": "✅ Plan generated", "plan": plan,
            "tokens_used": result.get("usage", {}).get("total_tokens", "?")}


# ─────────────────────────────────────────────
# SELF-EXTENDING AGENT — Writes its own skills
# ─────────────────────────────────────────────

def generate_agent_skill(skill_name: str, trigger_description: str, tech_context: str) -> dict:
    """Self-extending agent — generates a SKILL.md via OpenRouter and saves it."""
    system_prompt = """You are an expert in Claude Code and agentic AI engineering.
Generate a complete, production-ready SKILL.md. Return only raw markdown, no code fences."""

    result = or_chat(
        [{"role": "system", "content": system_prompt},
         {"role": "user", "content": (
             f"Skill: {skill_name}\nTrigger: {trigger_description}\nTech: {tech_context}\n\n"
             "Format:\n---\nname: ...\ndescription: >\n  ...\n  Triggers: ...\n---\n"
             "## Context\n## Prerequisites\n## Steps\n## Constraints\n## Expected Output"
         )}],
        model=DEFAULT_MODEL, temperature=0.35, max_tokens=1500,
    )
    if "error" in result:
        return {"error": result["error"]}

    skill_content = result["content"]
    skills_dir = os.path.join(os.path.dirname(__file__), "..", "03-claude-code-toolkit", "skills")
    os.makedirs(skills_dir, exist_ok=True)
    safe_name  = skill_name.lower().replace(" ", "-")
    skill_path = os.path.join(skills_dir, f"{safe_name}.md")
    with open(skill_path, "w") as f:
        f.write(skill_content)

    memory = _load_memory()
    memory["skills_learned"].append({"name": safe_name, "created": datetime.utcnow().isoformat()})
    _save_memory(memory)

    return {
        "status": "✅ Skill generated and saved",
        "file": skill_path,
        "skill_content": skill_content,
        "tokens_used": result.get("usage", {}).get("total_tokens", "?"),
    }


# ─────────────────────────────────────────────
# NVIDIA AGENTIC ECOSYSTEM REFERENCE
# ─────────────────────────────────────────────

def get_nvidia_agentic_reference() -> dict:
    """
    Reference guide for NVIDIA's agentic AI ecosystem.
    Based on NVIDIA AI Associate certification concepts:
    LLM-powered agents with memory, planning, tool use,
    multi-agent workflows, and automation.
    """
    return {
        "nvidia_nim": {
            "label": "NVIDIA NIM (Inference Microservices)",
            "description": "Optimized LLM inference containers — deploy any model with GPU acceleration.",
            "use_cases": ["Production LLM endpoints", "Low-latency agent tool calls", "On-prem / hybrid deployments"],
            "azure_integration": "Run NIM containers on Azure Kubernetes Service (AKS) with NVIDIA GPU nodes.",
        },
        "nemo_guardrails": {
            "label": "NVIDIA NeMo Guardrails",
            "description": "Safety rails for LLM agents — define allowed/blocked topics, factual grounding, and output validation.",
            "use_cases": ["Preventing off-topic agent responses", "Content policy enforcement", "Fact-checking agent outputs"],
            "azure_integration": "Combine with Azure AI Content Safety for layered safety.",
        },
        "cuvs": {
            "label": "NVIDIA cuVS (GPU Vector Search)",
            "description": "GPU-accelerated vector similarity search — orders of magnitude faster than CPU FAISS.",
            "use_cases": ["High-speed RAG retrieval", "Real-time semantic search", "Large-scale embedding indexes"],
            "azure_integration": "Deploy cuVS on Azure NC-series VMs for ultra-fast RAG pipelines.",
        },
        "agent_memory_patterns": {
            "label": "Agent Memory Architecture",
            "description": "Three tiers of agent memory as taught in NVIDIA AI certification.",
            "tiers": {
                "working_memory": "In-context: current conversation + tool results (limited by context window)",
                "episodic_memory": "Session-level: summaries of past interactions (stored in vector DB)",
                "semantic_memory": "Long-term: distilled facts and skills (persistent knowledge store)",
            },
        },
        "planning_patterns": {
            "label": "LLM Planning Patterns",
            "description": "Core planning approaches for agentic AI systems.",
            "patterns": {
                "react": "Reason → Act → Observe loop (most common, used by this app)",
                "plan_and_execute": "Generate full plan first, then execute steps sequentially",
                "tree_of_thought": "Explore multiple reasoning branches, pick best path",
                "reflexion": "Agent evaluates its own outputs and self-corrects",
            },
        },
        "multi_agent_patterns": {
            "label": "Multi-Agent Orchestration",
            "description": "Patterns for coordinating multiple specialized agents.",
            "patterns": {
                "chatdev_chatchain": "Sequential specialist handoffs (Architect → Developer → QA → DevOps)",
                "hierarchical": "Manager agent delegates to sub-agents, collects results",
                "collaborative": "Agents debate and vote on the best solution",
                "competitive": "Multiple agents propose solutions, evaluator picks the best",
            },
        },
    }
