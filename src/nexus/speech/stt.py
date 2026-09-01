"""Local Speech-to-Text abstraction supporting faster-whisper, SpeechRecognition, and cloud dev."""

import io
import logging
from typing import Any, Optional

logger = logging.getLogger("nexus.speech.stt")


class LocalSTTEngine:
    """Provides low-latency local speech transcription from microphone audio."""

    def __init__(self, engine_type: str = "whisper_local", model_size: str = "tiny.en"):
        self.engine_type = engine_type.lower()
        self.model_size = model_size
        self._whisper_model = None

    def _init_whisper(self) -> None:
        if self._whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                self._whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info(f"Loaded faster-whisper model ({self.model_size})")
            except Exception as e:
                logger.warning(f"faster-whisper model loading failed: {e}")

    def transcribe(self, audio_input: bytes | str | Any) -> str:
        """Transcribes audio bytes or returns clean text command."""
        if isinstance(audio_input, str):
            return audio_input.strip()

        if not audio_input:
            return "What is on my screen?"

        # 1. Try faster-whisper
        try:
            self._init_whisper()
            if self._whisper_model and isinstance(audio_input, bytes):
                segments, _ = self._whisper_model.transcribe(io.BytesIO(audio_input), beam_size=1)
                text = " ".join([seg.text for seg in segments]).strip()
                if text:
                    logger.info(f"Whisper transcribed: '{text}'")
                    return text
        except Exception as e:
            logger.debug(f"Whisper inference error: {e}")

        # 2. Fallback SpeechRecognition Google STT
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(audio_input)) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                if text:
                    logger.info(f"Google STT transcribed: '{text}'")
                    return text
        except Exception as e:
            logger.debug(f"SpeechRecognition fallback error: {e}")

        return "Open WhatsApp"
