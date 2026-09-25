# Voice Interview Coach

Paste your resume and a job posting, get tailored interview questions
asked aloud, answer out loud, and get real feedback on each answer —
plus an overall summary at the end.

## Architecture

```
Resume + job posting (pasted text)
        │
        ▼
generate_questions() ──► Gemini writes N tailored interview questions
        │
        ▼
For each question:
        │
        ├─► text_to_speech() ──► question read aloud
        ├─► mic_recorder() ──► you record your spoken answer
        ├─► transcribe_audio() ──► Groq Whisper converts speech to text
        ├─► evaluate_answer() ──► Gemini gives structured feedback
        └─► text_to_speech() ──► feedback read aloud
        │
        ▼
generate_summary() ──► overall patterns across all answers, read aloud
```

## Why this design is different from your other projects

Your bank agent and learning agent both use tool-calling agents —
the model decides which function to call. This project doesn't need
that: there's no external action to take or ambiguous tool choice,
just a clear sequence of steps. So this uses direct LLM calls
(`llm.invoke(prompt)`) instead of `create_agent`. Worth understanding
this distinction: **agents are for when the model needs to decide
what to do; a plain chain is for when you already know the steps**
and just need good prompts at each one. Using an agent framework
here would add complexity without adding capability.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Get your API keys

- **Gemini**: https://aistudio.google.com/app/apikey (same key from
  your other projects works fine)
- **Groq** (for speech-to-text): https://console.groq.com/keys —
  free, no credit card required

## 3. Set up your .env file

```bash
cp .env.example .env
```

Paste in both keys.

## 4. Run it

```bash
streamlit run app.py
```

## Using it

1. Paste your resume text and a job posting into the two boxes
2. Choose how many questions you want, click "Generate questions"
3. For each question: listen to it, click "Start recording", speak
   your answer, click "Stop" — you'll see the transcription and get
   feedback (text + spoken)
4. After the last question, you get an overall summary of patterns
   across your answers

## Things to try

- Answer one question really well (clear structure, specific
  example) and one vaguely — compare the feedback you get on each
- Try a technical question vs. a behavioral one — the evaluation
  prompt treats them differently
- Check the "Full transcript" expander after the summary to review
  everything at once

## Next steps to go further

- **Support PDF resume upload** instead of paste — reuse the
  `PyPDFLoader` pattern from your learning-agent project
- **Add a difficulty setting** — junior vs. senior-level questions
- **Score answers numerically** (1-5) in addition to written feedback,
  and chart progress across multiple practice sessions
- **Add follow-up questions**: if an answer is vague, let the agent
  ask a natural follow-up before moving on — this WOULD benefit from
  an agent/tool-calling approach, since the model needs to decide
  whether to follow up or move on
- **Deploy it** so friends could use it too — Streamlit Community
  Cloud hosts this free

## Project structure

```
interview-coach/
├── config.py         # loads API keys
├── stt.py              # speech-to-text via Groq Whisper
├── voice.py              # text-to-speech via gTTS
├── interview.py             # question generation + answer evaluation
├── app.py                     # Streamlit UI and session flow
├── .env.example                 # template for your API keys
└── requirements.txt               # Python dependencies
```
