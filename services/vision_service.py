"""
services/vision_service.py
Azure AI Vision — Image analysis, OCR, alt-text generation
"""
import os
import requests
from PIL import Image
import io


def analyze_image_url(image_url: str) -> dict:
    endpoint = os.getenv("AZURE_VISION_ENDPOINT", "")
    key = os.getenv("AZURE_VISION_KEY", "")
    if not endpoint or not key:
        return {"error": "Azure Vision credentials not configured. Add AZURE_VISION_ENDPOINT and AZURE_VISION_KEY to .env"}

    url = f"{endpoint.rstrip('/')}/computervision/imageanalysis:analyze"
    params = {
        "api-version": "2023-02-01-preview",
        "features": "caption,tags,objects,read",
        "language": "en",
    }
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
    }
    body = {"url": image_url}

    try:
        response = requests.post(url, params=params, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        result = response.json()

        return {
            "caption": result.get("captionResult", {}).get("text", ""),
            "caption_confidence": round(result.get("captionResult", {}).get("confidence", 0), 3),
            "tags": [t["name"] for t in result.get("tagsResult", {}).get("values", [])],
            "objects": [
                {"name": o["tags"][0]["name"], "confidence": round(o["tags"][0]["confidence"], 3)}
                for o in result.get("objectsResult", {}).get("values", [])
            ],
            "text_extracted": _flatten_read_result(result.get("readResult", {})),
        }
    except Exception as e:
        return {"error": str(e)}


def ocr_image_url(image_url: str) -> dict:
    endpoint = os.getenv("AZURE_VISION_ENDPOINT", "")
    key = os.getenv("AZURE_VISION_KEY", "")
    if not endpoint or not key:
        return {"error": "Azure Vision credentials not configured."}

    url = f"{endpoint.rstrip('/')}/computervision/imageanalysis:analyze"
    params = {"api-version": "2023-02-01-preview", "features": "read"}
    headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/json"}
    body = {"url": image_url}

    try:
        response = requests.post(url, params=params, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        result = response.json()
        text = _flatten_read_result(result.get("readResult", {}))
        return {"extracted_text": text, "char_count": len(text)}
    except Exception as e:
        return {"error": str(e)}


def _flatten_read_result(read_result: dict) -> str:
    lines = []
    for block in read_result.get("blocks", []):
        for line in block.get("lines", []):
            lines.append(line.get("text", ""))
    return "\n".join(lines)


def get_vision_pipeline_info() -> str:
    return """
Azure AI Vision Skillset Pipeline (AI-102 Pattern)
════════════════════════════════════════════════════

Blob Storage (images/videos)
        ↓ [Indexer triggers on new blobs]
        ├── 🔍 Image Analysis Skill    → Tags, objects, dense captions
        ├── 📄 OCR Skill               → Text extraction from images
        ├── 🎯 Custom Vision Skill     → Domain-specific classification
        └── 🔑 Key Phrase Extraction   → Summary from visual content
        ↓
Azure Cognitive Search Index
        ↓
Downstream: RAG / Chatbot / Product Search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Accessibility Pattern (AI-102 Exam Staple):
  1. Language Detection Skill   → detect source language
  2. Text Translation Skill     → translate to EN, ES, PT
  3. Image Analysis Skill       → generate alt-text descriptions
  4. Store per language         → altText["en"], altText["es"], altText["pt"]
"""
