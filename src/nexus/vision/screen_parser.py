"""Visual screen parser synthesizing accessibility and vision cues."""

from dataclasses import dataclass
from typing import Any
from nexus.android.screen.observer import CompactScreenState
from nexus.vision.ocr import OCREngine


class VisualScreenParser:
    """Synthesizes OCR and hierarchy to generate comprehensive screen descriptions."""

    def __init__(self, simulation: bool = False):
        self.ocr = OCREngine(simulation=simulation)

    def summarize_screen(self, screen_state: CompactScreenState, image_bytes: bytes = b"") -> str:
        """Returns a natural language description of what is currently on screen."""
        app = screen_state.app
        visible = screen_state.visible_text[:8]
        
        if not visible and image_bytes:
            ocr_results = self.ocr.extract_text(image_bytes)
            visible = [r.text for r in ocr_results]

        if visible:
            elements_str = ", ".join(visible)
            return f"Currently on {app} ({screen_state.screen} screen). Visible items: {elements_str}."
        
        return f"Currently displaying {app} home screen."
