#!/bin/bash
# ─────────────────────────────────────────────────────────────
# push_to_github.sh — One-shot git init + push to GitHub
# Run from inside agentic-ai-engineer-framework/
# ─────────────────────────────────────────────────────────────

set -e

REPO_URL="https://github.com/NatwarUpadhyay/agentic-ai-engineer-framework.git"

echo "🔍 Verifying no API keys leaked..."
if grep -r "sk-or-v1-fe884d" --include="*.py" --include="*.md" --include="*.txt" --include=".env.example" . 2>/dev/null; then
  echo "❌ API key found in tracked files! Aborting."
  exit 1
fi
echo "✅ No API keys in tracked files."

echo ""
echo "🗂️  Initializing git..."
git init
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo ""
echo "📦 Staging all files..."
git add .

echo ""
echo "📋 Files to be committed:"
git status --short

echo ""
echo "💾 Committing..."
git commit -m "🧠 Initial release — Agentic AI Engineer Framework

Features:
- 🔍 ZIP Repo Analyzer (OpenRouter + Qwen3-VL-235B-Thinking)
- ⚡ ReAct Agent with persistent memory
- 🏭 Multi-Agent Pipeline (ChatDev 2.0 style)
- 🗺️ Planner Agent (Tree-of-Thought)
- 💬 Azure AI Language / NLP services
- 🌍 Azure AI Translator
- 👁️ Azure AI Vision
- 🔍 Azure Cognitive Search
- 🛡️ Azure Content Safety + RAI checklist
- ⚙️ CLAUDE.md & SKILL.md generators
- 🧠 NVIDIA Agentic AI ecosystem reference

No Ollama. No GPU. Runs on any laptop via OpenRouter cloud."

echo ""
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main --force

echo ""
echo "✅ Done! Your repo is live at:"
echo "   https://github.com/NatwarUpadhyay/agentic-ai-engineer-framework"
