"""Tests for SafetyGate guardrails."""

from nexus.agent.tools.safety import SafetyGate, SafetyCheckResult


def test_safety_gate_blocked_actions():
    gate = SafetyGate(interactive=False)

    # High-risk actions requiring confirmation
    res_send = gate.check("SEND_MESSAGE", {"to": "John", "text": "Hello"})
    assert res_send.requires_confirmation is True
    assert res_send.allowed is False

    res_pay = gate.check("PAYMENT", {"amount": 500})
    assert res_pay.requires_confirmation is True

    res_del = gate.check("DELETE", {"item": "chat"})
    assert res_del.requires_confirmation is True

    # Safe read/nav actions allowed immediately
    res_open = gate.check("OPEN_APP", {"package": "com.whatsapp"})
    assert res_open.requires_confirmation is False
    assert res_open.allowed is True

    res_back = gate.check("BACK", {})
    assert res_back.requires_confirmation is False
    assert res_back.allowed is True
