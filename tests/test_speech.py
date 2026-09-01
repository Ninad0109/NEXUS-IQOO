"""Tests for Push-to-Talk and Local STT engine."""

import pytest
from nexus.speech.stt import LocalSTTEngine
from nexus.speech.ptt import PushToTalkController


def test_stt_transcription():
    stt = LocalSTTEngine(engine_type="mock")
    
    # Test text passthrough & mock transcription
    res = stt.transcribe("Open WhatsApp")
    assert res == "Open WhatsApp"

    res_bytes = stt.transcribe(b"MOCK_AUDIO_DATA")
    assert res_bytes is not None
    assert len(res_bytes) > 0


def test_push_to_talk_mock():
    ptt = PushToTalkController(simulation=True)
    audio = ptt.record_phrase(simulated_text="Open Gmail")
    assert audio == "Open Gmail"
