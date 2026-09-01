"""Push-to-Talk audio recording controller supporting live microphone capture."""

import io
import logging
import time
from typing import Optional

logger = logging.getLogger("nexus.speech.ptt")


class PushToTalkController:
    """Controls push-to-talk audio recording from physical microphone."""

    def __init__(self, sample_rate: int = 16000, simulation: bool = False):
        self.sample_rate = sample_rate
        self.simulation = simulation

    def record_phrase(self, duration_sec: float = 3.5, simulated_text: Optional[str] = None) -> bytes | str:
        """Records a phrase while key is held or for duration, or returns simulated text."""
        if self.simulation:
            return simulated_text or "Open WhatsApp"

        # 1. Try SpeechRecognition Microphone
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                logger.info("Microphone open. Listening...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5.0, phrase_time_limit=duration_sec)
                return audio.get_wav_data()
        except Exception as e1:
            logger.debug(f"SpeechRecognition mic capture unavailable ({e1}), trying sounddevice...")

        # 2. Try sounddevice
        try:
            import sounddevice as sd
            import soundfile as sf
            import numpy as np

            logger.info(f"Recording {duration_sec}s from default sounddevice...")
            recording = sd.rec(
                int(duration_sec * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16"
            )
            sd.wait()
            
            buf = io.BytesIO()
            sf.write(buf, recording, self.sample_rate, format='WAV', subtype='PCM_16')
            buf.seek(0)
            return buf.read()
        except Exception as e2:
            logger.warning(f"Live microphone capture failed ({e2}). Using text input.")
            return simulated_text or "Open WhatsApp"
