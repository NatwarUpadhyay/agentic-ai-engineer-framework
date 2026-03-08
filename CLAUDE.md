# CLAUDE.md — AI Engineer's Peak Potential Framework
# This file is auto-loaded by Claude Code at session start.

## Project Overview
This is an **Agentic AI Engineering Framework** — a production-grade toolkit for building, deploying, and operating AI systems using Azure AI Services, NVIDIA's agentic ecosystem, and Claude Code patterns.

Covers: AI-102 Azure AI Engineer + NVIDIA AI Associate agentic certification concepts.

## Tech Stack
- **Runtime:** Python 3.11+
- **UI:** Gradio 4.x
- **Azure AI:** OpenAI (GPT-4o), AI Language, Translator, Vision, Cognitive Search, Content Safety
- **Agentic:** ReAct agents, multi-agent orchestration, persistent memory (JSON), tool use
- **NVIDIA Ecosystem:** NIM inference, NeMo Guardrails (reference), cuVS vector search (reference)
- **Libraries:** LangChain, FAISS, OpenAI SDK, Azure SDKs

## Conventions
- All secrets in `.env` — never in code
- Services live in `services/` — one file per Azure service
- Gradio tabs live in `tabs/` — one file per UI section
- Data/memory persists in `data/` directory
- Generated skills saved to `03-claude-code-toolkit/skills/`
- Use `python -m` to run from project root

## Environment Variables (see .env.example)
- AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT
- AZURE_LANGUAGE_ENDPOINT, AZURE_LANGUAGE_KEY
- AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_REGION
- AZURE_VISION_ENDPOINT, AZURE_VISION_KEY
- AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX
- AZURE_CONTENT_SAFETY_ENDPOINT, AZURE_CONTENT_SAFETY_KEY

## Running the App
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your Azure keys
python app.py
```

## Forbidden Actions
- Never hardcode API keys or secrets
- Never commit `.env` files
- Never call `az resource delete` without user confirmation
- Never push to `main` directly — use feature branches

## Agent Patterns in This Repo
1. ReAct Agent (reason + act loop with tool use)
2. Planner Agent (goal → structured task plan)
3. Multi-Agent Pipeline (Architect → Developer → QA → DevOps)
4. Self-Extending Agent (agent writes its own SKILL.md files)
5. Persistent Memory (JSON-backed cross-session agent memory)

## Useful Commands
- `python app.py` — launch Gradio app
- `python -c "from services.agentic_service import run_react_agent; print(run_react_agent('test'))"` — test agent
