"""
tabs/tab_translation.py — Translation tab
tabs/tab_vision.py — Vision tab
tabs/tab_search.py — Cognitive Search tab
tabs/tab_safety.py — Content Safety + Responsible AI tab
"""
import json
import gradio as gr
from services.translator_service import translate_text
from services.vision_service import analyze_image_url, ocr_image_url, get_vision_pipeline_info
from services.search_service import search_documents, list_indexes, get_search_pipeline_diagram
from services.content_safety_service import analyze_content_safety, get_responsible_ai_checklist


# ── TRANSLATION ──────────────────────────────────────────────────────────────

LANGUAGES = {
    "English (en)": "en", "Spanish (es)": "es", "French (fr)": "fr",
    "German (de)": "de", "Portuguese (pt)": "pt", "Italian (it)": "it",
    "Dutch (nl)": "nl", "Japanese (ja)": "ja", "Chinese Simplified (zh-Hans)": "zh-Hans",
    "Arabic (ar)": "ar", "Hindi (hi)": "hi", "Russian (ru)": "ru",
    "Korean (ko)": "ko", "Turkish (tr)": "tr", "Polish (pl)": "pl",
}


def translate_fn(text: str, target_langs: list):
    if not text.strip():
        return "⚠️ Enter text to translate.", ""
    codes = [LANGUAGES[l] for l in target_langs if l in LANGUAGES]
    if not codes:
        return "⚠️ Select at least one target language.", ""
    result = translate_text(text, target_languages=codes)
    if "error" in result:
        return f"❌ {result['error']}", ""
    md = [f"**Detected Language:** {result.get('detected_language', '?')}\n"]
    for lang_code, translation in result.get("translations", {}).items():
        flag = {"en": "🇬🇧", "es": "🇪🇸", "fr": "🇫🇷", "de": "🇩🇪", "pt": "🇧🇷",
                "ja": "🇯🇵", "zh-Hans": "🇨🇳", "ar": "🇸🇦", "hi": "🇮🇳"}.get(lang_code, "🌐")
        md.append(f"**{flag} {lang_code}:**\n> {translation}\n")
    return "\n".join(md), json.dumps(result, indent=2, ensure_ascii=False)


def build_translation_tab():
    with gr.Tab("🌍 Translation"):
        gr.Markdown("""## 🌍 Azure AI Translator
Real-time multilingual translation across 100+ languages.
*Powered by Azure AI Translator (AI-102 Section 4.5)*""")
        txt = gr.Textbox(label="Text to Translate", lines=4, placeholder="Enter text in any language...")
        langs = gr.CheckboxGroup(
            choices=list(LANGUAGES.keys()),
            value=["Spanish (es)", "French (fr)", "German (de)"],
            label="Target Languages",
        )
        btn = gr.Button("🌍 Translate", variant="primary")
        with gr.Row():
            out_md   = gr.Markdown(label="Translations")
            out_json = gr.Code(label="Raw JSON", language="json")
        btn.click(translate_fn, [txt, langs], [out_md, out_json])
        gr.Examples(
            examples=[["The quick brown fox jumps over the lazy dog."],
                      ["Azure AI services provide powerful capabilities for building intelligent applications."]],
            inputs=txt,
        )


# ── VISION ───────────────────────────────────────────────────────────────────

def vision_fn(url: str):
    if not url.strip():
        return "⚠️ Enter an image URL."
    r = analyze_image_url(url)
    if "error" in r:
        return f"❌ {r['error']}"
    md = [f"### 🏷️ Caption\n> {r.get('caption', 'N/A')} *(confidence: {r.get('caption_confidence', '?')})*\n"]
    tags = r.get("tags", [])
    if tags:
        md.append(f"**Tags:** {', '.join(f'`{t}`' for t in tags)}\n")
    objs = r.get("objects", [])
    if objs:
        md.append("**Objects Detected:**")
        for o in objs:
            md.append(f"- {o['name']} ({o['confidence']})")
    text = r.get("text_extracted", "")
    if text:
        md.append(f"\n**📄 Text (OCR):**\n```\n{text}\n```")
    return "\n".join(md)


def ocr_fn(url: str):
    if not url.strip():
        return "⚠️ Enter an image URL."
    r = ocr_image_url(url)
    if "error" in r:
        return f"❌ {r['error']}"
    return f"**Extracted Text ({r.get('char_count', 0)} chars):**\n```\n{r.get('extracted_text', '')}\n```"


def build_vision_tab():
    with gr.Tab("👁️ Computer Vision"):
        gr.Markdown("## 👁️ Azure AI Vision\nImage analysis, OCR, and alt-text generation.")
        with gr.Tabs():
            with gr.Tab("🔍 Image Analysis"):
                url = gr.Textbox(label="Image URL", placeholder="https://example.com/image.jpg")
                btn = gr.Button("Analyze Image", variant="primary")
                out = gr.Markdown()
                btn.click(vision_fn, url, out)
                gr.Examples(
                    examples=[["https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"]],
                    inputs=url,
                )
            with gr.Tab("📄 OCR (Text Extraction)"):
                url2 = gr.Textbox(label="Image URL", placeholder="https://example.com/document.jpg")
                btn2 = gr.Button("Extract Text", variant="primary")
                out2 = gr.Markdown()
                btn2.click(ocr_fn, url2, out2)
            with gr.Tab("🏗️ Pipeline Reference"):
                gr.Markdown(f"```\n{get_vision_pipeline_info()}\n```")


# ── COGNITIVE SEARCH ─────────────────────────────────────────────────────────

def search_fn(query: str, top: int):
    if not query.strip():
        return "⚠️ Enter a search query."
    r = search_documents(query, top=int(top))
    if "error" in r:
        return f"❌ {r['error']}"
    if not r.get("results"):
        return f"*No results found for '{query}'*"
    md = [f"**{r['count']} results for:** `{query}`\n"]
    for i, doc in enumerate(r["results"], 1):
        md.append(f"### Result {i}\n```json\n{json.dumps(doc, indent=2)[:400]}\n```")
    return "\n".join(md)


def list_indexes_fn():
    r = list_indexes()
    if "error" in r:
        return f"❌ {r['error']}"
    idxs = r.get("indexes", [])
    if not idxs:
        return "*No indexes found. Configure AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY.*"
    return "**Indexes:**\n" + "\n".join(f"- `{i}`" for i in idxs)


def build_search_tab():
    with gr.Tab("🔍 Cognitive Search"):
        gr.Markdown("## 🔍 Azure Cognitive Search\nSearch documents, list indexes, and explore the RAG pipeline.")
        with gr.Tabs():
            with gr.Tab("🔎 Search"):
                with gr.Row():
                    q = gr.Textbox(label="Search Query", placeholder="e.g. Azure AI services overview")
                    top = gr.Slider(1, 20, value=5, step=1, label="Top Results")
                btn = gr.Button("Search", variant="primary")
                out = gr.Markdown()
                btn.click(search_fn, [q, top], out)

            with gr.Tab("📋 List Indexes"):
                btn2 = gr.Button("List Indexes", variant="secondary")
                out2 = gr.Markdown(value="*Click to list all indexes in your search service.*")
                btn2.click(list_indexes_fn, outputs=out2)

            with gr.Tab("🏗️ Pipeline Diagram"):
                gr.Markdown(f"```\n{get_search_pipeline_diagram()}\n```")
                gr.Markdown("""### RAG Pattern
```
Query → Embed (text-embedding-3-large) → Search (Azure AI Search vector index)
     → Retrieve (top-k chunks) → Augment (ground GPT-4o prompt) → Generate → Respond
```""")


# ── CONTENT SAFETY + RESPONSIBLE AI ─────────────────────────────────────────

def safety_fn(text: str):
    if not text.strip():
        return "⚠️ Enter text to analyze."
    r = analyze_content_safety(text)
    if "error" in r:
        return f"❌ {r['error']}"
    assessment = r.get("overall_assessment", "?")
    md = [f"## {assessment}\n", f"*Text analyzed: \"{r.get('text_analyzed', '')}\"*\n", "### Category Scores\n"]
    for cat, data in r.get("categories", {}).items():
        severity = data.get("severity", 0)
        label    = data.get("severity_label", "?")
        bar      = "█" * (severity // 2 + 1) if severity > 0 else "░"
        md.append(f"- **{cat}**: {bar} Severity {severity} ({label})")
    return "\n".join(md)


def checklist_fn():
    data = get_responsible_ai_checklist()
    md   = ["# 📋 Responsible AI Checklist\n"]
    for section, items in data.items():
        md.append(f"## {section}")
        for item in items:
            md.append(f"- [ ] {item}")
        md.append("")
    return "\n".join(md)


def build_safety_tab():
    with gr.Tab("🛡️ Content Safety & RAI"):
        gr.Markdown("## 🛡️ Content Safety & Responsible AI\nAnalyze text for harmful content and track your Responsible AI compliance checklist.")
        with gr.Tabs():
            with gr.Tab("🚨 Content Safety Analyzer"):
                gr.Markdown("> Azure AI Content Safety — detect Hate, SelfHarm, Sexual, and Violence with severity levels.")
                txt = gr.Textbox(label="Text to Analyze", lines=4, placeholder="Enter text to check for harmful content...")
                btn = gr.Button("Analyze Safety", variant="primary")
                out = gr.Markdown()
                btn.click(safety_fn, txt, out)

            with gr.Tab("📋 Responsible AI Checklist"):
                btn2 = gr.Button("Load Checklist", variant="secondary")
                out2 = gr.Markdown(value="*Click to load the Responsible AI checklist.*")
                btn2.click(checklist_fn, outputs=out2)
                out2.value = checklist_fn()
