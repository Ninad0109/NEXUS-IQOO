"""Tests for VerificationEngine."""

from nexus.android.screen.observer import CompactScreenState, CompactScreenElement
from nexus.android.verification.verifier import VerificationEngine


def test_verification_open_app():
    verifier = VerificationEngine()
    
    pre_state = CompactScreenState(app="Home", package="com.android.launcher", elements=[], visible_text=[])
    post_state = CompactScreenState(app="WhatsApp", package="com.whatsapp", elements=[
        CompactScreenElement(node_id="1", text="Chats", element_type="tab", clickable=True)
    ], visible_text=["Chats", "Mom"])

    result = verifier.verify_action(
        action="OPEN_APP",
        params={"package": "com.whatsapp", "app_name": "WhatsApp"},
        pre_state=pre_state,
        post_state=post_state
    )

    assert result.success is True
    assert "WhatsApp is now foreground" in result.message
