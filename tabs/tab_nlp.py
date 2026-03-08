"""
tabs/tab_nlp.py — NLP / Language Services tab
"""
import json
import gradio as gr
from services.language_service import (
    analyze_sentiment, extract_key_phrases,
    detect_pii, recognize_entities, detect_language,
)


def _fmt(obj): return json.dumps(obj, indent=2, ensure_ascii=False)


def sentiment_fn(text):
    if not text.strip(): return "⚠️ Enter some text."
    r = analyze_sentiment(text)
    if "error" in r: return f"❌ {r['error']}"
    score = r["confidence"]
    emoji = {"positive": "😊", "neutral": "😐", "negative": "😟"}.get(r["overall_sentiment"], "🤔")
    md = [f"## {emoji} Overall: **{r['overall_sentiment'].title()}**\n"]
    md.append(f"| Positive | Neutral | Negative |\n|---|---|---|\n| {score['positive']} | {score['neutral']} | {score['negative']} |\n")
    md.append("### Sentence Breakdown")
    for s in r.get("sentences", []):
        e = {"positive": "😊", "neutral": "😐", "negative": "😟"}.get(s["sentiment"], "")
        md.append(f"- {e} *\"{s['text']}\"* → **{s['sentiment']}** (pos:{s['confidence']['positive']} neg:{s['confidence']['negative']})")
    return "\n".join(md)


def key_phrases_fn(text):
    if not text.strip(): return "⚠️ Enter some text."
    r = extract_key_phrases(text)
    if "error" in r: return f"❌ {r['error']}"
    phrases = r.get("key_phrases", [])
    if not phrases: return "*No key phrases detected.*"
    return "### 🔑 Key Phrases\n" + "\n".join(f"- `{p}`" for p in phrases)


def pii_fn(text):
    if not text.strip(): return "⚠️ Enter some text.", ""
    r = detect_pii(text)
    if "error" in r: return f"❌ {r['error']}", ""
    entities = r.get("pii_entities", [])
    redacted = r.get("redacted_text", text)
    md = [f"### 🔒 Redacted Text\n```\n{redacted}\n```\n", "### 🚨 PII Detected"]
    if entities:
        for e in entities:
            md.append(f"- **{e['category']}**: `{e['text']}` (confidence: {e['confidence']})")
    else:
        md.append("*No PII detected.*")
    return "\n".join(md), _fmt(r)


def ner_fn(text):
    if not text.strip(): return "⚠️ Enter some text."
    r = recognize_entities(text)
    if "error" in r: return f"❌ {r['error']}"
    entities = r.get("entities", [])
    if not entities: return "*No named entities detected.*"
    category_emoji = {
        "Person": "👤", "Organization": "🏢", "Location": "📍",
        "DateTime": "📅", "Quantity": "🔢", "URL": "🔗", "Email": "📧",
    }
    md = ["### 🏷️ Named Entities\n"]
    for e in entities:
        emoji = category_emoji.get(e["category"], "🔹")
        md.append(f"- {emoji} **{e['category']}**: `{e['text']}` (confidence: {e['confidence']})")
    return "\n".join(md)


def lang_detect_fn(text):
    if not text.strip(): return "⚠️ Enter some text."
    r = detect_language(text)
    if "error" in r: return f"❌ {r['error']}"
    return (f"### 🌐 Detected Language\n\n"
            f"**{r['detected_language']}** (`{r['iso_code']}`) — confidence: **{r['confidence']}**")


def build_nlp_tab():
    with gr.Tab("💬 NLP / Language"):
        gr.Markdown("""## 💬 Azure AI Language Services
Sentiment analysis, Named Entity Recognition (NER), Key Phrase Extraction, PII Detection, and Language Detection.
*Powered by Azure AI Language (AI-102 Section 4.5)*""")

        with gr.Tabs():

            with gr.Tab("😊 Sentiment Analysis"):
                txt = gr.Textbox(label="Input Text", lines=4, placeholder="Enter text to analyze sentiment...")
                btn = gr.Button("Analyze Sentiment", variant="primary")
                out = gr.Markdown()
                btn.click(sentiment_fn, txt, out)
                gr.Examples(
                    examples=[
                        ["Azure AI services are incredibly powerful for building enterprise solutions!"],
                        ["The deployment failed again. This is really frustrating."],
                        ["The model performed adequately. Results were acceptable."],
                    ],
                    inputs=txt,
                )

            with gr.Tab("🔑 Key Phrases"):
                txt2 = gr.Textbox(label="Input Text", lines=4, placeholder="Enter text to extract key phrases...")
                btn2 = gr.Button("Extract Key Phrases", variant="primary")
                out2 = gr.Markdown()
                btn2.click(key_phrases_fn, txt2, out2)

            with gr.Tab("🔒 PII Detection"):
                gr.Markdown("> Detects and redacts Personally Identifiable Information — essential for GDPR/CCPA compliance.")
                txt3 = gr.Textbox(label="Input Text", lines=4, placeholder="e.g. My name is John Smith, email john@example.com, SSN 123-45-6789")
                btn3 = gr.Button("Detect PII", variant="primary")
                with gr.Row():
                    out3_md = gr.Markdown()
                    out3_json = gr.Code(label="Raw JSON", language="json")
                btn3.click(pii_fn, txt3, [out3_md, out3_json])

            with gr.Tab("🏷️ Named Entities (NER)"):
                txt4 = gr.Textbox(label="Input Text", lines=4, placeholder="e.g. Microsoft was founded by Bill Gates in Albuquerque in 1975")
                btn4 = gr.Button("Recognize Entities", variant="primary")
                out4 = gr.Markdown()
                btn4.click(ner_fn, txt4, out4)

            with gr.Tab("🌐 Language Detection"):
                txt5 = gr.Textbox(label="Input Text", lines=3, placeholder="Enter text in any language...")
                btn5 = gr.Button("Detect Language", variant="primary")
                out5 = gr.Markdown()
                btn5.click(lang_detect_fn, txt5, out5)
                gr.Examples(
                    examples=[
                        ["Hola, ¿cómo estás? Me llamo Carlos."],
                        ["Bonjour, je m'appelle Marie."],
                        ["こんにちは、元気ですか？"],
                        ["Olá, como vai você?"],
                    ],
                    inputs=txt5,
                )

            with gr.Tab("📖 Service Reference"):
                gr.Markdown("""### Azure AI Language — Service Reference (AI-102)

| Service | Use Case | Status |
|---|---|---|
| **Azure AI Language** | Sentiment, key phrases, NER, PII | ✅ Live in this app |
| **Azure AI Translator** | Real-time translation (100+ languages) | ✅ Live in Translation tab |
| **Azure AI Speech** | STT/TTS for voice-enabled chatbots | 🔧 Add AZURE_SPEECH_KEY |
| **CLU** (Conversational Language Understanding) | Intent + entity recognition (replaced LUIS) | 🔧 Configure in Language Studio |
| **Custom Question Answering** | FAQ chatbots (replaced QnA Maker) | 🔧 Configure in Language Studio |
| **Orchestration Workflow** | Routes between CLU + CQA in one endpoint | 🔧 Advanced setup |

> 🎯 **AI-102 Exam Tip:** QnA Maker → **Custom Question Answering** · LUIS → **CLU** · Orchestrator connects them.

### NLP Pipeline Pattern
```
User Input
    ↓
Language Detection (detect source lang)
    ↓
Text Translation (→ EN for processing)
    ↓
├── Sentiment Analysis
├── Key Phrase Extraction
├── Named Entity Recognition
└── PII Detection + Redaction
    ↓
Processed Output (stored in Cognitive Search Index)
```""")
