# Learning Agent — Document Q&A with Voice

Upload a PDF or text document — a textbook chapter, lecture notes,
an article — and ask questions about it. The agent explains concepts
grounded in your actual material, in both text and spoken audio.

## Architecture

```
Upload PDF/txt (app.py)
        │
        ▼
Chunk + embed (ingest.py) ──► Chroma vector store (in-memory, per session)
        │
        ▼
Ask a question (Streamlit chat)
        │
        ▼
Agent (agent.py) ──► decides whether to call search_document
        │                    │
        │                    ▼
        │           Chroma similarity search ──► most relevant chunks
        │                    │
        ◄────────────────────┘
        │
        ▼
Gemini writes an explanation grounded in what was retrieved
        │
        ▼
gTTS converts the answer to speech ──► played inline in the chat
```

## Why this design

- **RAG (Retrieval-Augmented Generation)**: instead of pasting the
  whole document into every prompt (expensive, and models get worse
  at using very long context), the document is chunked and embedded
  once. Each question only retrieves the few most relevant chunks —
  this is the same core technique real production Q&A systems use.
- **Tool-calling, not a fixed pipeline**: `search_document` is a tool
  the agent chooses to call, same as your bank agent's tools. Ask it
  something unrelated to the document and it can say so honestly
  instead of forcing a bad answer out of irrelevant chunks.
- **No API key needed for voice**: gTTS talks directly to Google's
  free TTS endpoint — the only key you need for the whole project is
  your existing Gemini key.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Set up your .env file

```bash
cp .env.example .env
```

Paste in your Gemini key (same one from your other projects works fine).

## 3. Run it

```bash
streamlit run app.py
```

Upload a PDF or .txt file, wait for indexing to finish, then start asking questions.

## Things to try

- "Explain the main idea of this document in simple terms"
- "What does [specific term from the document] mean?"
- Ask something NOT in the document — it should say so rather than
  making something up
- Ask a follow-up without repeating context — memory should carry it
- Click play on the audio player under any answer

## Next steps to go further

- **Persist the vector store to disk** so you don't have to re-upload
  and re-embed the same document every session
- **Support multiple documents at once**, with the agent citing which
  one an answer came from
- **Add a quiz mode**: after explaining a concept, generate a quick
  multiple-choice question to check understanding (this is exactly
  the quiz_display pattern from earlier tutor project ideas)
- **Voice input too**, not just output — use the browser's speech
  recognition API so you can ask questions out loud
- **Swap gTTS for a more natural-sounding TTS** (e.g. ElevenLabs) once
  you're past the free-and-simple learning stage

## Project structure

```
learning-agent/
├── config.py       # loads Gemini API key
├── ingest.py         # loads, chunks, and embeds an uploaded document
├── tools.py            # search_document tool for the agent
├── voice.py               # text-to-speech via gTTS
├── agent.py                 # the tutor agent + system prompt
├── app.py                     # Streamlit UI
├── .env.example                 # template for your API key
└── requirements.txt              # Python dependencies
```
