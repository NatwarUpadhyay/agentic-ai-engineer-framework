"""
services/language_service.py
Azure AI Language — Sentiment, NER, Key Phrases, PII Detection
"""
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


def get_language_client():
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT", "")
    key = os.getenv("AZURE_LANGUAGE_KEY", "")
    if not endpoint or not key:
        return None
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def analyze_sentiment(text: str) -> dict:
    client = get_language_client()
    if not client:
        return {"error": "Azure Language credentials not configured. Add AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY to .env"}
    try:
        result = client.analyze_sentiment([text])[0]
        return {
            "overall_sentiment": result.sentiment,
            "confidence": {
                "positive": round(result.confidence_scores.positive, 3),
                "neutral": round(result.confidence_scores.neutral, 3),
                "negative": round(result.confidence_scores.negative, 3),
            },
            "sentences": [
                {
                    "text": s.text,
                    "sentiment": s.sentiment,
                    "confidence": {
                        "positive": round(s.confidence_scores.positive, 3),
                        "neutral": round(s.confidence_scores.neutral, 3),
                        "negative": round(s.confidence_scores.negative, 3),
                    },
                }
                for s in result.sentences
            ],
        }
    except Exception as e:
        return {"error": str(e)}


def extract_key_phrases(text: str) -> dict:
    client = get_language_client()
    if not client:
        return {"error": "Azure Language credentials not configured."}
    try:
        result = client.extract_key_phrases([text])[0]
        if result.is_error:
            return {"error": result.error.message}
        return {"key_phrases": list(result.key_phrases)}
    except Exception as e:
        return {"error": str(e)}


def detect_pii(text: str) -> dict:
    client = get_language_client()
    if not client:
        return {"error": "Azure Language credentials not configured."}
    try:
        result = client.recognize_pii_entities([text])[0]
        if result.is_error:
            return {"error": result.error.message}
        entities = [
            {"text": e.text, "category": e.category, "confidence": round(e.confidence_score, 3)}
            for e in result.entities
        ]
        return {
            "redacted_text": result.redacted_text,
            "pii_entities": entities,
        }
    except Exception as e:
        return {"error": str(e)}


def recognize_entities(text: str) -> dict:
    client = get_language_client()
    if not client:
        return {"error": "Azure Language credentials not configured."}
    try:
        result = client.recognize_entities([text])[0]
        if result.is_error:
            return {"error": result.error.message}
        entities = [
            {"text": e.text, "category": e.category, "confidence": round(e.confidence_score, 3)}
            for e in result.entities
        ]
        return {"entities": entities}
    except Exception as e:
        return {"error": str(e)}


def detect_language(text: str) -> dict:
    client = get_language_client()
    if not client:
        return {"error": "Azure Language credentials not configured."}
    try:
        result = client.detect_language([text])[0]
        if result.is_error:
            return {"error": result.error.message}
        return {
            "detected_language": result.primary_language.name,
            "iso_code": result.primary_language.iso6391_name,
            "confidence": round(result.primary_language.confidence_score, 3),
        }
    except Exception as e:
        return {"error": str(e)}
