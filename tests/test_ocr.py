"""Tests for OCR fallback engine."""

from nexus.vision.ocr import OCREngine, OCRResult


def test_ocr_engine_mock():
    ocr = OCREngine(simulation=True)
    results = ocr.extract_text(b"SAMPLE_IMAGE_BYTES")
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0].text is not None
