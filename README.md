# 🧠 Agentic AI Engineer Framework

> **A complete, hands-on toolkit for building production-grade Agentic AI systems** — combining Azure AI Services (AI-102), NVIDIA's agentic ecosystem, Claude Code patterns, and a powerful **ZIP-based Repo Analyzer** that tells you exactly what skills and files to add to any project.

<div align="center">

[![No Ollama Required](https://img.shields.io/badge/No%20Ollama-Required-22c55e?style=for-the-badge&logo=checkmarx)](.)
[![No GPU Needed](https://img.shields.io/badge/No%20GPU-Needed-22c55e?style=for-the-badge&logo=checkmarx)](.)
[![OpenRouter Powered](https://img.shields.io/badge/OpenRouter-Powered-6366f1?style=for-the-badge)](https://openrouter.ai)
[![Model](https://img.shields.io/badge/Qwen3--VL--235B-Thinking-818cf8?style=for-the-badge)](https://openrouter.ai/models/qwen/qwen3-vl-235b-a22b-thinking)
[![Azure AI-102](https://img.shields.io/badge/Azure-AI--102-0078D4?style=for-the-badge&logo=microsoftazure)](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/)
[![NVIDIA Agentic](https://img.shields.io/badge/NVIDIA-Agentic%20AI-76b900?style=for-the-badge&logo=nvidia)](https://www.nvidia.com/en-us/training/)

</div>

---

## 🚫 No Ollama. No GPU. No Heavy Setup.

> **This entire framework runs on your laptop via the cloud.**
>
> - ❌ No Ollama install
> - ❌ No NVIDIA GPU required
> - ❌ No 64GB RAM needed
> - ✅ Just Python + an OpenRouter API key (already pre-configured)
> - ✅ Works on MacBook, Windows laptop, Linux VM — anything
>
> All LLM inference runs on **OpenRouter's cloud** using **Qwen3-VL-235B-Thinking** —
> a 235-billion-parameter multimodal model with chain-of-thought reasoning.
> You get state-of-the-art AI for pennies per query, no local hardware required.

---

## 🎯 What This Framework Does

Built on two certifications worth of real knowledge:

> *"The **Microsoft Azure AI Engineer Associate (AI-102)** certification helped me design and deploy production Azure AI pipelines — from Cognitive Search skillsets to RAG architectures. The **NVIDIA AI Associate (Agentic AI)** certification helped me build a strong foundation in designing and deploying Agentic AI systems using NVIDIA's ecosystem — creating LLM-powered agents with memory, planning, and tool use, and exploring multi-agent workflows and automation. I have been applying these concepts in my Agentic AI projects to build more practical, scalable solutions."*

This repo distills both into one hands-on platform.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **🔍 ZIP Repo Analyzer** | Upload any project ZIP → AI identifies missing skills, files to create, and prioritized next actions |
| **⚡ ReAct Agent** | Reason → Tool call → Observe loop with 6 built-in tools + persistent memory |
| **🏭 Multi-Agent Pipeline** | ChatDev 2.0-style: Architect → Developer → QA → DevOps specialist agents |
| **🗺️ Planner Agent** | Decompose any goal into phased task plans with Azure service mappings |
| **🧠 Persistent Memory** | 3-tier memory (working / episodic / semantic) persists across sessions |
| **🔧 Self-Extending** | Agent writes its own `SKILL.md` files — your toolkit grows automatically |
| **💬 NLP Services** | Sentiment, NER, Key Phrases, PII Detection, Language Detection |
| **🌍 Translation** | Real-time translation across 100+ languages |
| **👁️ Computer Vision** | Image analysis, OCR, alt-text generation |
| **🔍 Cognitive Search** | Azure AI Search integration with RAG pipeline reference |
| **🛡️ Content Safety** | Harm detection + Responsible AI checklist |
| **⚙️ Claude Toolkit** | `CLAUDE.md` generator, `SKILL.md` generator, hook templates |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/NatwarUpadhyay/agentic-ai-engineer-framework
cd agentic-ai-engineer-framework

# 2. Install (Python 3.11+ recommended)
pip install -r requirements.txt

# 3. Configure (OpenRouter is pre-configured — just copy the file)
cp .env.example .env
# Optionally add your Azure keys for Azure AI services

# 4. Run
python app.py

# 5. Open in browser
# → http://localhost:7860
```

> **That's it.** The core LLM features (Repo Analyzer, all agents, skill/CLAUDE.md generation) work immediately with the pre-configured OpenRouter key. Azure keys are optional — add them to unlock the Azure AI service tabs.

---

## 🔍 ZIP Repo Analyzer — The Star Feature

Upload any project as a `.zip` and the AI will:

1. **Parse** your entire file tree, detect languages, and read key files
2. **Identify** which Claude Code `SKILL.md` files are missing
3. **Suggest** specific files to create (`CLAUDE.md`, CI configs, `.env.example`, etc.)
4. **Generate** prioritized nudges — exactly what to do next and why
5. **Auto-generate** any suggested file or skill with one click

```
Upload project.zip
        ↓
    Qwen3-VL-235B-Thinking analyzes your repo
        ↓
┌─────────────────────────────────────────────┐
│  📊 Summary     — Project overview          │
│  💡 Nudges      — Prioritized next actions  │
│  📁 Files       — Files to create           │
│  🔧 Skills      — Missing SKILL.md files    │
└─────────────────────────────────────────────┘
        ↓
  Click "Generate" → Get the file content instantly
```

---

## 🤖 Agentic AI Patterns

### ReAct Agent (Reason + Act)
```
User Goal
    ↓
[Think] What do I need to do?
    ↓
[Tool Call] search_knowledge_base | {"query": "RAG pipeline"}
    ↓
[Observe] Results from KB...
    ↓
[Think] Now I can answer...
    ↓
FINAL_ANSWER: ...
```

### Multi-Agent Pipeline (ChatDev 2.0)
```
Task Input
    ↓
🏗️ Architect Agent  → Azure resource topology, service selection
    ↓ (passes context)
👨‍💻 Developer Agent → Production code, IaC, SDK implementation
    ↓ (passes context)
🧪 QA Agent         → Test cases, security review, gap analysis
    ↓ (passes context)
🚀 DevOps Agent     → CI/CD, monitoring, deployment strategy
    ↓
Complete Engineering Spec
```

### Planner Agent (Tree-of-Thought)
```
Goal → Phases → Tasks → Azure Services → Dependencies → Success Criteria
```

### Persistent Memory (NVIDIA 3-Tier Model)
```
Working Memory   → Current conversation context (in-context)
Episodic Memory  → Session logs (auto-saved after each agent run)
Semantic Memory  → Long-term facts (user-stored, persists across restarts)
```

---

## 🟢 NVIDIA Agentic AI Ecosystem

| Component | Purpose | Azure Integration |
|---|---|---|
| **NIM** (Inference Microservices) | GPU-optimized LLM inference | AKS + GPU node pools |
| **NeMo Guardrails** | Safety rails for agents | + Azure Content Safety |
| **cuVS** (GPU Vector Search) | Ultra-fast RAG retrieval | Azure NC-series VMs |
| **NeMo Framework** | Custom model training | Azure ML |
| **Triton Inference** | Scalable model serving | AKS |

> **In this framework:** We use OpenRouter (cloud) in place of NIM for zero-setup inference, while covering the NeMo Guardrails and cuVS architecture patterns as reference.

---

## ☁️ Azure AI Services Reference (AI-102)

```
Azure AI Services
├── Azure OpenAI          → GPT-4o, embeddings, RAG
├── Azure AI Language     → Sentiment, NER, PII, Key Phrases, CLU
├── Azure AI Translator   → 100+ language translation
├── Azure AI Vision       → Image analysis, OCR, Custom Vision
├── Azure Cognitive Search → Indexer, Skillsets, Vector Search
└── Azure Content Safety  → Harm detection, content filtering
```

### SLA Reference (Exam Staple)
```
99.9% reads only        → 1 replica
99.9% reads + writes    → 2 replicas
High availability + partition → 3 replicas + 2 partitions
```

---

## ⚙️ Claude Code Toolkit

### `CLAUDE.md` — Your AI's Brain
```markdown
# CLAUDE.md — Auto-loaded at every Claude session start

## Project Overview
...

## Tech Stack
...

## Conventions
...

## Forbidden Actions
- Never hardcode API keys
- Never push to main directly
```

### Hook Events
```
UserPromptSubmit  → Fires on every prompt
PreToolUse        → BEFORE any tool call ← most powerful for safety
PostToolUse       → AFTER tool completes (e.g. auto-format files)
PermissionRequest → When Claude asks for permission
Stop              → Session end (e.g. auto-summarize)
SubagentStop      → Subagent finishes
PreCompact        → Before context compaction
SessionStart      → Load project context automatically
```

---

## 📂 Repository Structure

```
agentic-ai-engineer-framework/
├── app.py                          ← Main Gradio app entry point
├── requirements.txt
├── .env.example                    ← Config template (OpenRouter pre-filled)
├── CLAUDE.md                       ← Claude Code project instructions
│
├── services/                       ← One file per service/capability
│   ├── openrouter_service.py       ← OpenRouter + Qwen3 (primary LLM)
│   ├── agentic_service.py          ← All agent patterns + memory
│   ├── repo_analyzer_service.py    ← ZIP analysis engine
│   ├── openai_service.py           ← Azure OpenAI (optional)
│   ├── language_service.py         ← Azure AI Language
│   ├── translator_service.py       ← Azure AI Translator
│   ├── vision_service.py           ← Azure AI Vision
│   ├── search_service.py           ← Azure Cognitive Search
│   └── content_safety_service.py   ← Azure Content Safety
│
├── tabs/                           ← One Gradio tab per section
│   ├── tab_home.py
│   ├── tab_repo_analyzer.py        ← ZIP Repo Analyzer tab
│   ├── tab_agentic.py              ← All agent tabs
│   ├── tab_nlp.py                  ← NLP / Language tab
│   ├── tab_services.py             ← Translation, Vision, Search, Safety
│   └── tab_claude_toolkit.py       ← CLAUDE.md, SKILL.md, Hooks
│
├── 03-claude-code-toolkit/
│   └── skills/                     ← Auto-generated SKILL.md files land here
│
└── data/
    └── agent_memory.json           ← Persistent agent memory store
```

---

## 🔑 Environment Variables

```bash
# Required for LLM features (pre-configured — works out of the box)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=qwen/qwen3-vl-235b-a22b-thinking

# Optional: Azure AI services (add to unlock Azure tabs)
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_KEY=...
AZURE_LANGUAGE_ENDPOINT=...
AZURE_LANGUAGE_KEY=...
AZURE_TRANSLATOR_KEY=...
AZURE_VISION_ENDPOINT=...
AZURE_VISION_KEY=...
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_KEY=...
AZURE_CONTENT_SAFETY_ENDPOINT=...
AZURE_CONTENT_SAFETY_KEY=...
```

---

## 🗺️ Learning Roadmap

```
Week 1-2:   Azure AI fundamentals + private networking + managed identity
Week 3-4:   Cognitive Search + skillset pipelines + knowledge mining
Week 5-6:   Azure OpenAI + RAG patterns + embeddings
Week 7-8:   Agentic AI — ReAct, planners, memory (NVIDIA certification)
Week 9-10:  Multi-agent orchestration + ChatDev 2.0 patterns
Week 11:    NVIDIA NIM / NeMo Guardrails + cuVS integration
Week 12:    Responsible AI + governance + exam prep (AI-102)
```

---

## 🤝 Contributing

PRs welcome! Ideas:
- New Azure AI service integrations
- Additional agentic patterns (Reflexion, MCTS, etc.)
- LangChain / LangGraph agent implementations
- More Claude Code hook templates
- Real-world project walkthroughs

---

## 📜 License

MIT — use freely, give credit where it helps.

---

## 🔗 Connect

Built by an AI engineer who holds both the **Microsoft Certified: Azure AI Engineer Associate (AI-102)** and **NVIDIA AI Associate (Agentic AI)** certifications — and wanted to make that knowledge actually useful to others.

If this helped you, ⭐ star the repo and share it!

---

*Inspired by: OpenClaw · ChatDev 2.0 · Claude CoWork · Anthropic Agent SDK*  
*Aligned with: Azure AI-102 · NVIDIA Agentic AI · Microsoft Responsible AI Principles*  
*Powered by: OpenRouter · Qwen3-VL-235B-Thinking · **No Ollama · No GPU · Any laptop***
