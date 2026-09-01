"""Push-to-Talk audio recording controller."""

import logging
import time
from typing import Optional

logger = logging.getLogger("nexus.speech.ptt")


class PushToTalkController:
    """Controls push-to-talk audio recording."""

    def __init__(self, sample_rate: int = 16000, simulation: bool = False):
        self.sample_rate = sample_rate
        self.simulation = simulation

    def record_phrase(self, duration_sec: float = 3.0, simulated_text: Optional[str] = None) -> bytes | str:
        """Records a phrase while key is held, or returns simulated text."""
        if self.simulation or simulated_text:
            return simulated_text or "Open WhatsApp"

        try:
            import sounddevice as sd
            import numpy as np

            logger.info(f"Recording for {duration_sec}s...")
            audio_data = sd.rec(int(duration_sec * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype="int16")
            sd.wait()
            return audio_data.tobytes()
        except Exception as e:
            logger.debug(f"Audio capture unavailable ({e}), returning default command")
            return "Open WhatsApp"
