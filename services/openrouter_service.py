"""
services/openrouter_service.py
─────────────────────────────────────────────────────────────────────────────
OpenRouter API — Cloud LLM inference, no Ollama, no GPU required.
Default model: qwen/qwen3-vl-235b-a22b-thinking (235B parameter multimodal model)

This means ANY developer — on any laptop, anywhere — can run this framework.
No NVIDIA GPU, no Ollama install, no heavy local setup needed.
"""

import os
import json
import requests

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")   # Set OPENROUTER_API_KEY in your .env file
DEFAULT_MODEL       = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-vl-235b-a22b-thinking")

APP_HEADERS = {
    "HTTP-Referer": "https://github.com/agentic-ai-engineer-framework",
    "X-Title": "Agentic AI Engineer Framework",
}


def _headers() -> dict:
    return {
        **APP_HEADERS,
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }


def chat(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.4,
    max_tokens: int = 4096,
    stream: bool = False,
) -> dict:
    """
    Send a chat completion request to OpenRouter.
    Works with any model on OpenRouter — defaults to Qwen3-VL-235B-Thinking.
    """
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=_headers(),
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage   = data.get("usage", {})
        return {
            "content": content,
            "model":   data.get("model", model or DEFAULT_MODEL),
            "usage": {
                "prompt_tokens":     usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens":      usage.get("total_tokens", 0),
            },
        }
    except requests.HTTPError as e:
        try:
            detail = resp.json()
        except Exception:
            detail = {}
        return {"error": f"HTTP {resp.status_code}: {detail.get('error', {}).get('message', str(e))}"}
    except Exception as e:
        return {"error": str(e)}


def simple_prompt(prompt: str, system: str = "", model: str = None, max_tokens: int = 4096) -> str:
    """Convenience wrapper — returns just the text content or an error string."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = chat(messages, model=model, max_tokens=max_tokens)
    if "error" in result:
        return f"❌ OpenRouter error: {result['error']}"
    return result["content"]


def list_available_models() -> dict:
    """Fetch the list of available models from OpenRouter."""
    try:
        resp = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        models = resp.json().get("data", [])
        return {
            "count": len(models),
            "models": [
                {
                    "id": m["id"],
                    "name": m.get("name", m["id"]),
                    "context_length": m.get("context_length", "?"),
                    "pricing": m.get("pricing", {}),
                }
                for m in models[:50]  # top 50
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def get_model_info() -> dict:
    return {
        "model": DEFAULT_MODEL,
        "provider": "OpenRouter",
        "description": "Qwen3-VL 235B Thinking — Alibaba's 235B multimodal model with chain-of-thought reasoning",
        "capabilities": [
            "Text generation & reasoning",
            "Code generation (Python, TypeScript, Bicep, etc.)",
            "Vision / multimodal understanding",
            "Chain-of-thought 'thinking' traces",
            "Long context (128K tokens)",
        ],
        "why_openrouter": [
            "✅ No Ollama required",
            "✅ No GPU required — runs entirely in the cloud",
            "✅ Works on any laptop, any OS",
            "✅ Access 300+ models with one API key",
            "✅ Pay-per-token — no expensive subscriptions needed",
        ],
        "base_url": OPENROUTER_BASE_URL,
    }
