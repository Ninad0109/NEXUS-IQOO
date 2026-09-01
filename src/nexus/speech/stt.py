"""Local Speech-to-Text abstraction supporting faster-whisper, Vosk, and mock input."""

import io
import logging
from typing import Any, Optional

logger = logging.getLogger("nexus.speech.stt")


class LocalSTTEngine:
    """Provides low-latency local speech transcription."""

    def __init__(self, engine_type: str = "whisper_local", model_size: str = "tiny.en"):
        self.engine_type = engine_type.lower()
        self.model_size = model_size
        self._model = None

    def _init_whisper(self) -> None:
        if self._model is None and self.engine_type in ("whisper", "whisper_local", "faster_whisper"):
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info(f"Loaded faster-whisper model ({self.model_size})")
            except Exception as e:
                logger.warning(f"Could not load faster-whisper ({e}), falling back to mock/text mode")

    def transcribe(self, audio_input: bytes | str | Any) -> str:
        """Transcribes audio bytes or returns clean text command."""
        if isinstance(audio_input, str):
            return audio_input.strip()

        if self.engine_type == "mock" or not audio_input:
            return "Open WhatsApp"

        self._init_whisper()
        if self._model and isinstance(audio_input, bytes):
            try:
                segments, _ = self._model.transcribe(io.BytesIO(audio_input), beam_size=1)
                text = " ".join([seg.text for seg in segments]).strip()
                return text if text else "What is on my screen?"
            except Exception as e:
                logger.error(f"Whisper transcription error: {e}")

        return "Open WhatsApp"
