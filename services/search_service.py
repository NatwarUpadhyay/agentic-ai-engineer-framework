"""
services/search_service.py
Azure Cognitive Search — Index documents, run searches, RAG retrieval
"""
import os
import json
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential


def get_search_client(index_name: str = None):
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    key = os.getenv("AZURE_SEARCH_KEY", "")
    index = index_name or os.getenv("AZURE_SEARCH_INDEX", "ai-framework-index")
    if not endpoint or not key:
        return None
    return SearchClient(endpoint=endpoint, index_name=index, credential=AzureKeyCredential(key))


def get_index_client():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    key = os.getenv("AZURE_SEARCH_KEY", "")
    if not endpoint or not key:
        return None
    return SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def search_documents(query: str, top: int = 5, index_name: str = None) -> dict:
    client = get_search_client(index_name)
    if not client:
        return {
            "error": "Azure Search credentials not configured. "
                     "Add AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY to .env"
        }
    try:
        results = client.search(search_text=query, top=top)
        docs = []
        for r in results:
            docs.append({k: v for k, v in r.items() if not k.startswith("@")})
        return {"query": query, "results": docs, "count": len(docs)}
    except Exception as e:
        return {"error": str(e)}


def list_indexes() -> dict:
    client = get_index_client()
    if not client:
        return {"error": "Azure Search credentials not configured."}
    try:
        indexes = [idx.name for idx in client.list_indexes()]
        return {"indexes": indexes, "count": len(indexes)}
    except Exception as e:
        return {"error": str(e)}


def index_documents(documents: list[dict], index_name: str = None) -> dict:
    """Upload documents to an Azure Search index."""
    client = get_search_client(index_name)
    if not client:
        return {"error": "Azure Search credentials not configured."}
    try:
        result = client.upload_documents(documents=documents)
        succeeded = sum(1 for r in result if r.succeeded)
        failed = len(result) - succeeded
        return {
            "uploaded": succeeded,
            "failed": failed,
            "index": index_name or os.getenv("AZURE_SEARCH_INDEX", "ai-framework-index"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_search_pipeline_diagram() -> str:
    """Return an ASCII diagram of the full Cognitive Search pipeline."""
    return """
╔══════════════════════════════════════════════════════════════════╗
║         Azure Cognitive Search — Full Pipeline                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DATA SOURCES          SKILLSETS              INDEX              ║
║  ────────────          ──────────             ──────             ║
║  Blob Storage   →   Language Detection   →  products[]          ║
║  Cosmos DB      →   Text Translation     →  - name[en/es/pt]    ║
║  SQL Database   →   Key Phrase Extract   →  - altText[en/es/pt] ║
║  SharePoint     →   Entity Recognition  →  - stockLevel         ║
║                 →   Image Analysis       →  - transcripts        ║
║                 →   OCR                  →  - insights           ║
║                                                                  ║
║                         ↓                                        ║
║                   Knowledge Store                                ║
║               (raw insights: Blob / Table)                       ║
║                         ↓                                        ║
║         Query → Embed → Search → Retrieve → Generate            ║
║                   (RAG with Azure OpenAI)                        ║
║                                                                  ║
║  SLA Requirements:                                               ║
║  99.9% reads          → 1 replica                               ║
║  99.9% reads+writes   → 2 replicas                              ║
║  HA + partition       → 3 replicas + 2 partitions               ║
╚══════════════════════════════════════════════════════════════════╝
"""
