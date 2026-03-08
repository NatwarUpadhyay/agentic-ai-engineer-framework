"""
services/openai_service.py
Azure OpenAI — Chat completions, RAG pattern, prompt engineering
"""
import os
from openai import AzureOpenAI


def get_openai_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    key = os.getenv("AZURE_OPENAI_KEY", "")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    if not endpoint or not key:
        return None
    return AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version=api_version)


def chat_completion(system_prompt: str, user_message: str, temperature: float = 0.7, max_tokens: int = 1024) -> dict:
    client = get_openai_client()
    if not client:
        return {"error": "Azure OpenAI credentials not configured. Add AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY to .env"}

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "response": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }
    except Exception as e:
        return {"error": str(e)}


def rag_completion(user_query: str, context_documents: list[str], temperature: float = 0.3) -> dict:
    """RAG pattern: ground the model response with retrieved context."""
    client = get_openai_client()
    if not client:
        return {"error": "Azure OpenAI credentials not configured."}

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    context = "\n\n---\n\n".join(context_documents) if context_documents else "No context provided."

    system_prompt = f"""You are a helpful AI assistant. Answer the user's question using ONLY the context below.
If the answer cannot be found in the context, say "I don't have enough information in the provided context to answer that."

CONTEXT:
{context}
"""
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=temperature,
            max_tokens=1024,
        )
        return {
            "query": user_query,
            "answer": response.choices[0].message.content,
            "context_used": len(context_documents),
            "tokens_used": response.usage.total_tokens,
        }
    except Exception as e:
        return {"error": str(e)}


def generate_skill_template(skill_name: str, description: str, tech_stack: str) -> dict:
    """Generate a Claude Code SKILL.md template using Azure OpenAI."""
    client = get_openai_client()
    if not client:
        return {"error": "Azure OpenAI credentials not configured."}

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    system_prompt = """You are an expert AI engineer specializing in Claude Code skills and Azure AI.
Generate a complete SKILL.md file for Claude Code. Follow this exact format:

---
name: <skill-name-kebab-case>
description: >
  Use this skill when... Triggers: <comma-separated trigger words>
---

## Context
<What the AI needs to know about the tech/environment>

## Steps
<Numbered list of what the AI should do>

## Constraints
<Bullet list of what the AI must never do>

## Example Output
<Brief example of expected output>
"""
    user_message = f"""Create a SKILL.md for:
Skill Name: {skill_name}
Description: {description}
Tech Stack: {tech_stack}"""

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=1024,
        )
        return {
            "skill_template": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
        }
    except Exception as e:
        return {"error": str(e)}


def generate_claude_md(project_name: str, tech_stack: str, conventions: str, forbidden_actions: str) -> dict:
    """Generate a CLAUDE.md project instruction file."""
    client = get_openai_client()
    if not client:
        return {"error": "Azure OpenAI credentials not configured."}

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    system_prompt = """You are an expert AI engineer. Generate a complete CLAUDE.md file.
CLAUDE.md is the most important file in a Claude Code project - it's the AI's brain for the session.
Make it detailed, practical, and production-ready. Include all sections."""

    user_message = f"""Generate a CLAUDE.md for:
Project: {project_name}
Tech Stack: {tech_stack}
Conventions: {conventions}
Forbidden Actions: {forbidden_actions}
"""
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return {
            "claude_md": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
        }
    except Exception as e:
        return {"error": str(e)}
