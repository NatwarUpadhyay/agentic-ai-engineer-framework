"""
tabs/tab_home.py — Home / Overview tab
"""
import gradio as gr


HERO_MARKDOWN = """
# 🧠 AI Engineer's Peak Potential Framework

**A complete Agentic AI Engineering toolkit** — combining Azure AI Services (AI-102),
NVIDIA's agentic ecosystem (NIM, NeMo Guardrails), and Claude Code patterns into one hands-on platform.

> *"I built this to bridge the gap between certification knowledge and production-grade AI engineering —
> from LLM-powered agents with memory, planning, and tool use, to multi-agent workflows and Azure AI pipelines."*

---

## 🗺️ What's Inside

| Section | What You Get |
|---|---|
| 🤖 **Agentic AI** | ReAct agent, multi-agent pipeline, planner, persistent memory, self-extending skills |
| 💬 **NLP / Language** | Sentiment, NER, key phrases, PII detection, language detection |
| 🌍 **Translation** | Multilingual translation (100+ languages), language detection |
| 🔍 **Cognitive Search** | Azure AI Search integration, RAG pipeline reference |
| 👁️ **Computer Vision** | Image analysis, OCR, vision pipeline architecture |
| 🛡️ **Content Safety** | Harm detection, Responsible AI checklist |
| ⚙️ **Claude Toolkit** | SKILL.md generator, CLAUDE.md generator, hook templates |
| 📚 **Reference** | NVIDIA ecosystem, agentic patterns, AI-102 concepts |

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/ai-engineer-framework
cd ai-engineer-framework
pip install -r requirements.txt
cp .env.example .env    # Add your Azure keys
python app.py
```

---

## 🤖 Agentic AI Patterns Covered

```
ReAct Loop:          Reason → Tool Call → Observe → Repeat → Answer
Planner Agent:       Goal → Decompose → Task Graph → Execute
Multi-Agent:         Architect → Developer → QA → DevOps  (ChatDev 2.0)
Persistent Memory:   Working → Episodic → Semantic  (NVIDIA 3-tier model)
Self-Extending:      Agent writes its own SKILL.md files (OpenClaw pattern)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Gradio UI (this app)                    │
├─────────────────────────────────────────────────────┤
│  Agentic Engine   │  Azure AI Services              │
│  ─────────────    │  ───────────────────            │
│  ReAct Agent      │  Azure OpenAI (GPT-4o)          │
│  Multi-Agent      │  Azure AI Language              │
│  Planner          │  Azure AI Translator            │
│  Memory Store     │  Azure AI Vision                │
│  Skill Generator  │  Azure Cognitive Search         │
│                   │  Azure Content Safety           │
└─────────────────────────────────────────────────────┘
│         NVIDIA Ecosystem (reference + integration)   │
│  NIM Inference  │  NeMo Guardrails  │  cuVS Search   │
└─────────────────────────────────────────────────────┘
```

---

*Aligned with: Azure AI-102 · NVIDIA AI Associate Agentic Certification · Microsoft Responsible AI*
*Inspired by: OpenClaw · ChatDev 2.0 · Claude CoWork · Anthropic Agent SDK*
"""


def build_home_tab():
    with gr.Tab("🏠 Home"):
        gr.Markdown(HERO_MARKDOWN)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("""### 📋 Learning Roadmap
```
Week 1-2:  Azure AI fundamentals + private networking
Week 3-4:  Cognitive Search + skillset pipelines
Week 5-6:  Azure OpenAI + RAG patterns
Week 7-8:  Agentic AI — ReAct, planners, memory
Week 9-10: Multi-agent orchestration (ChatDev 2.0)
Week 11:   NVIDIA NIM / NeMo Guardrails integration
Week 12:   Responsible AI + governance + exam prep
```""")
            with gr.Column(scale=1):
                gr.Markdown("""### 🔗 Key Resources
- [Azure AI-102 Exam Page](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/)
- [NVIDIA AI Associate Certification](https://www.nvidia.com/en-us/training/)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Azure Cognitive Search](https://azure.microsoft.com/en-us/products/search)
- [LangChain Docs](https://python.langchain.com/docs/)""")
