"""
services/translator_service.py
Azure AI Translator — Real-time multilingual translation
"""
import os
import requests
import uuid


TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"


def translate_text(text: str, target_languages: list, source_language: str = None) -> dict:
    key = os.getenv("AZURE_TRANSLATOR_KEY", "")
    region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
    endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", TRANSLATOR_ENDPOINT)

    if not key:
        return {"error": "Azure Translator credentials not configured. Add AZURE_TRANSLATOR_KEY to .env"}

    path = "/translate"
    constructed_url = endpoint.rstrip("/") + path

    params = {
        "api-version": "3.0",
        "to": target_languages,
    }
    if source_language:
        params["from"] = source_language

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    body = [{"text": text}]

    try:
        response = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=15)
        response.raise_for_status()
        result = response.json()
        translations = {}
        for translation in result[0].get("translations", []):
            translations[translation["to"]] = translation["text"]

        detected_lang = result[0].get("detectedLanguage", {})
        return {
            "original_text": text,
            "detected_language": detected_lang.get("language", source_language or "unknown"),
            "detection_score": detected_lang.get("score", None),
            "translations": translations,
        }
    except Exception as e:
        return {"error": str(e)}


def detect_language_translator(text: str) -> dict:
    key = os.getenv("AZURE_TRANSLATOR_KEY", "")
    region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
    endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", TRANSLATOR_ENDPOINT)

    if not key:
        return {"error": "Azure Translator credentials not configured."}

    path = "/detect"
    constructed_url = endpoint.rstrip("/") + path
    params = {"api-version": "3.0"}
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-type": "application/json",
    }
    body = [{"text": text}]

    try:
        response = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=15)
        response.raise_for_status()
        result = response.json()
        return {
            "language": result[0].get("language"),
            "score": result[0].get("score"),
            "is_translation_supported": result[0].get("isTranslationSupported"),
        }
    except Exception as e:
        return {"error": str(e)}
