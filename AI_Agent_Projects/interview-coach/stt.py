"""
stt.py
------
Converts recorded speech to text using Groq's Whisper API.

Groq hosts OpenAI's open-source Whisper model and offers a genuinely
free tier — no credit card, generous limits, and very fast responses
(Groq is known for speed, which matters here so the conversation
doesn't feel laggy).
"""

from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    audio_bytes: raw audio bytes (from the browser mic recorder).

    Returns the transcribed text.
    """
    # Groq's SDK expects a (filename, bytes) tuple — the filename's
    # extension just needs to match the actual audio format.
    transcription = client.audio.transcriptions.create(
        file=("answer.wav", audio_bytes),
        model="whisper-large-v3",
    )
    return transcription.text
