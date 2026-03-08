"""
services/repo_analyzer_service.py
─────────────────────────────────────────────────────────────────────────────
Repository ZIP Analyzer — Upload any project as a ZIP, and the agent will:

  1. Parse the repo structure (files, dirs, languages, frameworks)
  2. Detect what Azure AI / agentic patterns are already present
  3. Identify which Claude Code SKILLS can be added
  4. Suggest what new files should be created
  5. Generate a prioritized "nudge" list of next actions
  6. Optionally auto-generate the suggested files

Powered by OpenRouter + Qwen3-VL-235B-Thinking.
No Ollama. No GPU. Works on any machine.
"""

import os
import io
import json
import zipfile
import pathlib
from typing import Optional

from services.openrouter_service import chat, simple_prompt, DEFAULT_MODEL


# ── File type classification ────────────────────────────────────────────────

LANG_MAP = {
    ".py": "Python", ".ts": "TypeScript", ".js": "JavaScript",
    ".cs": "C#", ".java": "Java", ".go": "Go", ".rs": "Rust",
    ".bicep": "Bicep", ".tf": "Terraform", ".yml": "YAML",
    ".yaml": "YAML", ".json": "JSON", ".md": "Markdown",
    ".toml": "TOML", ".env": "Env", ".sh": "Shell",
    ".dockerfile": "Docker", ".txt": "Text", ".html": "HTML",
    ".css": "CSS", ".tsx": "TypeScript/React",
}

SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".nuxt",
    "coverage", ".pytest_cache", ".mypy_cache",
}

MAX_FILE_PREVIEW = 3_000   # chars per file sent to LLM
MAX_FILES_INLINE = 25      # max files to send full content for
MAX_ZIP_SIZE_MB  = 50


# ── ZIP parsing ─────────────────────────────────────────────────────────────

def parse_zip(zip_bytes: bytes) -> dict:
    """
    Extract structure and key file contents from a ZIP archive.
    Returns a dict with file tree, language stats, and preview content.
    """
    if len(zip_bytes) > MAX_ZIP_SIZE_MB * 1024 * 1024:
        return {"error": f"ZIP file too large. Max {MAX_ZIP_SIZE_MB}MB."}

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return {"error": "Invalid ZIP file. Please upload a valid .zip archive."}

    all_names    = zf.namelist()
    file_tree    = []
    lang_counts  = {}
    key_files    = {}   # filename → content (for important files)
    inline_count = 0
    total_files  = 0

    # Priority files to read fully regardless of count
    priority_names = {
        "package.json", "requirements.txt", "pyproject.toml", "setup.py",
        "CLAUDE.md", "README.md", "readme.md", ".env.example", "Dockerfile",
        "docker-compose.yml", "docker-compose.yaml",
        "bicep/main.bicep", "infra/main.tf", "main.py", "app.py",
        "index.ts", "index.js", "tsconfig.json",
    }

    for name in all_names:
        # Skip directories and hidden/build dirs
        parts = pathlib.PurePosixPath(name).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if name.endswith("/"):
            continue

        total_files += 1
        ext  = pathlib.PurePosixPath(name).suffix.lower()
        lang = LANG_MAP.get(ext, "Other")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

        basename = pathlib.PurePosixPath(name).name
        file_tree.append(name)

        # Read content for priority / important files
        is_priority = basename in priority_names or ext in (".md", ".py", ".ts", ".json", ".bicep", ".tf")
        if is_priority and inline_count < MAX_FILES_INLINE:
            try:
                raw = zf.read(name)
                text = raw.decode("utf-8", errors="replace")[:MAX_FILE_PREVIEW]
                key_files[name] = text
                inline_count += 1
            except Exception:
                pass

    return {
        "total_files": total_files,
        "file_tree": file_tree,
        "language_stats": lang_counts,
        "key_files": key_files,
        "files_previewed": inline_count,
    }


# ── Repo Analysis prompt ─────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are an expert Agentic AI Engineer specializing in:
- Azure AI Services (AI-102 level)
- NVIDIA NIM / NeMo Guardrails agentic patterns
- Claude Code best practices (CLAUDE.md, SKILL.md, hooks)
- LangChain, OpenAI SDK, RAG pipelines
- Production-grade agentic AI systems

You will analyze a developer's repository and produce a structured JSON response.
Be specific, actionable, and practical. Think like a senior engineer reviewing a PR."""

_ANALYSIS_SCHEMA = """{
  "project_summary": "one paragraph describing what this repo does",
  "detected_tech_stack": ["list of detected technologies"],
  "detected_patterns": ["list of AI/agentic patterns already present"],
  "missing_skills": [
    {
      "skill_name": "kebab-case-name",
      "trigger": "when this skill should be used",
      "priority": "high|medium|low",
      "reason": "why this skill is missing / useful"
    }
  ],
  "files_to_create": [
    {
      "filename": "relative/path/to/file.ext",
      "purpose": "what this file does",
      "priority": "high|medium|low",
      "template_hint": "brief content outline or template"
    }
  ],
  "nudges": [
    {
      "action": "short action title",
      "detail": "specific actionable recommendation",
      "priority": "high|medium|low",
      "category": "security|agentic|azure-ai|code-quality|devops|responsible-ai"
    }
  ],
  "strengths": ["things the repo already does well"],
  "quick_wins": ["3-5 things that can be done in under 30 minutes"]
}"""


def analyze_repo(zip_bytes: bytes, extra_context: str = "") -> dict:
    """
    Full repo analysis pipeline:
    1. Parse ZIP → extract structure + key file contents
    2. Build LLM prompt with file tree + contents
    3. Get Qwen3-VL-235B structured analysis
    4. Return parsed nudges, skills, and file suggestions
    """
    parsed = parse_zip(zip_bytes)
    if "error" in parsed:
        return parsed

    # Build the analysis prompt
    file_tree_str = "\n".join(parsed["file_tree"][:200])  # cap at 200 paths
    lang_str = ", ".join(f"{lang}: {cnt}" for lang, cnt in sorted(
        parsed["language_stats"].items(), key=lambda x: -x[1]
    ))

    key_files_str = ""
    for fname, content in list(parsed["key_files"].items())[:MAX_FILES_INLINE]:
        key_files_str += f"\n\n### {fname}\n```\n{content}\n```"

    prompt = f"""Analyze this repository and return ONLY valid JSON matching the schema below.

## Repository Stats
- Total files: {parsed['total_files']}
- Languages: {lang_str}
- Files previewed: {parsed['files_previewed']}

## File Tree
```
{file_tree_str}
```

## Key File Contents
{key_files_str}

{f"## Additional Context from Developer\n{extra_context}" if extra_context.strip() else ""}

## Required JSON Schema
{_ANALYSIS_SCHEMA}

Return ONLY the JSON object. No markdown, no explanation."""

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user",   "content": prompt},
    ]

    result = chat(messages, model=DEFAULT_MODEL, temperature=0.2, max_tokens=4096)
    if "error" in result:
        return {"error": result["error"], "parsed_zip": parsed}

    raw = result["content"].strip()

    # Strip markdown code fences if model wrapped JSON
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    # Strip <think>...</think> blocks that Qwen3-Thinking emits
    import re
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON object from surrounding text
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            try:
                analysis = json.loads(match.group())
            except Exception:
                analysis = {"raw_response": raw}
        else:
            analysis = {"raw_response": raw}

    return {
        "status": "✅ Analysis complete",
        "repo_stats": {
            "total_files": parsed["total_files"],
            "language_stats": parsed["language_stats"],
            "files_previewed": parsed["files_previewed"],
        },
        "analysis": analysis,
        "tokens_used": result.get("usage", {}).get("total_tokens", "?"),
        "model_used": result.get("model", DEFAULT_MODEL),
    }


# ── Auto-generate a suggested file ──────────────────────────────────────────

def generate_suggested_file(
    filename: str,
    purpose: str,
    template_hint: str,
    repo_context: str = "",
    file_type: str = "auto",
) -> dict:
    """
    Generate the actual content for a file suggested by the repo analysis.
    Uses OpenRouter + Qwen3 to produce production-ready content.
    """
    ext = pathlib.PurePosixPath(filename).suffix.lower()
    lang_hint = LANG_MAP.get(ext, "text")

    system = f"""You are an expert {lang_hint} developer and Azure AI engineer.
Generate complete, production-ready file content. Include helpful comments.
Do not wrap in markdown code fences — return raw file content only."""

    prompt = f"""Generate the content for this file:

Filename: {filename}
Purpose: {purpose}
Template hint: {template_hint}
Language: {lang_hint}
{f"Repo context: {repo_context[:500]}" if repo_context else ""}

Return only the file content, ready to save."""

    content = simple_prompt(prompt, system=system, max_tokens=3000)
    return {
        "filename": filename,
        "content": content,
        "language": lang_hint,
    }


# ── Generate a SKILL.md for a missing skill ──────────────────────────────────

def generate_missing_skill(skill: dict, repo_summary: str = "") -> dict:
    """Auto-generate a SKILL.md for a skill identified as missing from the repo."""
    system = """You are an expert in Claude Code skills. 
Generate a complete SKILL.md. Return only the raw markdown, no code fences."""

    prompt = f"""Generate a SKILL.md for Claude Code:

Skill Name: {skill.get('skill_name', 'custom-skill')}
Trigger: {skill.get('trigger', '')}
Priority: {skill.get('priority', 'medium')}
Reason needed: {skill.get('reason', '')}
{f"Repo context: {repo_summary[:300]}" if repo_summary else ""}

Format:
---
name: {skill.get('skill_name', 'custom-skill')}
description: >
  Use this skill when... Triggers: ...
---

## Context
## Prerequisites  
## Steps
## Constraints
## Expected Output"""

    content = simple_prompt(prompt, system=system, max_tokens=1500)
    return {
        "skill_name": skill.get("skill_name"),
        "content": content,
    }
