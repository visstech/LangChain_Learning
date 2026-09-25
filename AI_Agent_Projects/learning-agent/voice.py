"""
voice.py
--------
Converts text to spoken audio using gTTS (Google Text-to-Speech).

Unlike everything else in this project, gTTS needs NO API key and
NO signup at all — it's a free Python library that talks to Google
Translate's TTS endpoint directly. It does need an internet
connection to work, same as everything else here.
"""

import io
from gtts import gTTS


def text_to_speech(text: str) -> io.BytesIO:
    """
    Converts `text` to speech and returns it as in-memory MP3 bytes
    (no temp files on disk needed).
    """
    tts = gTTS(text=text, lang="en")
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)  # rewind so it can be read from the start
    return audio_buffer
