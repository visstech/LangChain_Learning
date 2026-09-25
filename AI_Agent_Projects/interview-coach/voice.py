"""
voice.py
--------
Converts text to spoken audio using gTTS — no API key needed.
"""

import io
from gtts import gTTS


def text_to_speech(text: str) -> io.BytesIO:
    """Converts `text` to speech and returns it as in-memory MP3 bytes."""
    tts = gTTS(text=text, lang="en")
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer
