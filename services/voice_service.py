import speech_recognition as sr
import io
import base64
import wave
import tempfile
import os


def speech_to_text(audio_base64: str) -> str:
    try:
        audio_bytes = base64.b64decode(audio_base64)
        recognizer = sr.Recognizer()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with sr.AudioFile(tmp_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        finally:
            os.unlink(tmp_path)

    except sr.UnknownValueError:
        raise ValueError("Could not understand audio. Please speak clearly and try again.")
    except sr.RequestError as e:
        raise RuntimeError(f"Speech recognition service error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Audio processing error: {str(e)}")


def validate_audio(audio_base64: str) -> bool:
    try:
        audio_bytes = base64.b64decode(audio_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            with wave.open(tmp_path, "rb") as wf:
                return wf.getnframes() > 0
        finally:
            os.unlink(tmp_path)
    except Exception:
        return False
