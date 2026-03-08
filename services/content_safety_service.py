"""
services/content_safety_service.py
Azure AI Content Safety — Filter harmful content in inputs/outputs
"""
import os
import requests


def analyze_content_safety(text: str) -> dict:
    endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT", "")
    key = os.getenv("AZURE_CONTENT_SAFETY_KEY", "")

    if not endpoint or not key:
        return {
            "error": "Azure Content Safety credentials not configured. "
                     "Add AZURE_CONTENT_SAFETY_ENDPOINT and AZURE_CONTENT_SAFETY_KEY to .env"
        }

    url = f"{endpoint.rstrip('/')}/contentsafety/text:analyze?api-version=2023-10-01"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
    }
    body = {
        "text": text,
        "categories": ["Hate", "SelfHarm", "Sexual", "Violence"],
        "outputType": "FourSeverityLevels",
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=15)
        response.raise_for_status()
        result = response.json()

        categories = {}
        for item in result.get("categoriesAnalysis", []):
            categories[item["category"]] = {
                "severity": item["severity"],
                "severity_label": _severity_label(item["severity"]),
            }

        overall_safe = all(v["severity"] <= 1 for v in categories.values())
        return {
            "text_analyzed": text[:100] + "..." if len(text) > 100 else text,
            "overall_assessment": "✅ Safe" if overall_safe else "⚠️ Potentially Harmful",
            "categories": categories,
        }
    except Exception as e:
        return {"error": str(e)}


def _severity_label(severity: int) -> str:
    labels = {0: "Safe", 2: "Low", 4: "Medium", 6: "High"}
    return labels.get(severity, f"Level {severity}")


def get_responsible_ai_checklist() -> dict:
    """Return the Responsible AI checklist from the framework."""
    return {
        "Security": [
            "Private endpoints — no public internet access to AI services",
            "Managed Identity — no API keys stored in code",
            "Network isolation via VNet integration",
            "Azure Key Vault for all secrets",
        ],
        "Fairness & Safety": [
            "Content Safety filters enabled (Azure AI Content Safety)",
            "Bias evaluation run on model outputs",
            "PII detection enabled for user inputs",
        ],
        "Transparency": [
            "Model card documented for custom models",
            "Logging enabled — all AI calls traceable",
            "Human review loop defined for high-stakes decisions",
        ],
        "Compliance": [
            "Data residency confirmed (US datacenters for US clients)",
            "GDPR/CCPA controls applied where needed",
            "Audit logs retained per organizational policy",
        ],
    }
