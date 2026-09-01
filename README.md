<div align="center">

# ⚡ NEXUS — iQOO On-Device AI Agent ⚡

**Phone-Native Agentic AI Architecture for Snapdragon / Qualcomm AI Engine**

[![Tests](https://img.shields.io/badge/tests-43%20passed-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iQOO-blue.svg)]()
[![Inference](https://img.shields.io/badge/inference-Snapdragon%20NPU%20%7C%20ONNX%20%7C%20OpenJarvis-orange.svg)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-lightgrey.svg)]()

</div>

---

## 🚀 Overview

**NEXUS** is an on-device phone agent built for **iQOO and Snapdragon** smartphones. Inspired by computer-use agents and powered by a modular OpenJarvis foundation, NEXUS operates directly against Android OS primitives without requiring continuous transmission of high-resolution video/screenshots to cloud models.

### Execution Loop:
$$\text{HEAR} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{OBSERVE SCREEN} \longrightarrow \text{PLAN} \longrightarrow \text{ACT} \longrightarrow \text{VERIFY} \longrightarrow \text{RESPOND}$$

---

## 🏛️ System Architecture

```text
               ┌──────────────────────────────┐
               │    Push-to-Talk Voice / Mic   │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │    Local STT Engine (Whisper) │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │   AgentBackend / Planner     │◄────────────┐
               └──────────────┬───────────────┘             │
                              ▼                             │
               ┌──────────────────────────────┐             │
               │  LocalModelProvider Abstraction│           │
               │  • Snapdragon NPU (QNN/HTP)  │             │
               │  • ONNX Runtime (Local)      │             │
               │  • OpenJarvis Reasoning Core │             │
               │  • Remote Cloud Fallback     │             │
               └──────────────┬───────────────┘             │
                              ▼                             │
               ┌──────────────────────────────┐             │
               │   Safety Gate & Guardrails   │             │
               └──────────────┬───────────────┘             │
                              ▼                             │
               ┌──────────────────────────────┐             │
               │ Android Native Control Layer │             │
               │  (AccessibilityService/ADB)  │             │
               └──────────────┬───────────────┘             │
                              ▼                             │
               ┌──────────────────────────────┐             │
               │     ScreenObserver           │             │
               │   (Compact Screen JSON)      │─────────────┘
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │    Verification Engine       │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │   Futuristic Terminal HUD    │
               │  [LOCAL AI: Snapdragon NPU]  │
               └──────────────────────────────┘
```

---

## 🎯 5-Tier Semantic Interaction Priority

Instead of guessing raw screen coordinates, NEXUS prioritizes:
1. **Accessibility Node Reference** (`node_id`)
2. **Resource ID** (`com.whatsapp:id/...`)
3. **Visible Text / Semantic Match** (fuzzy & exact text centroid)
4. **Content Description / Accessibility Labels**
5. **OCR / Vision Fallback** (only when UI tree is sparse)

---

## 🛡️ Safety & Confirmation Guardrails

NEXUS enforces hard confirmation gates before executing high-risk phone operations:
* 🛑 `SEND_MESSAGE` (Prompts user before sending external text/message)
* 🛑 `PAYMENT` / `PURCHASE` (Strictly requires explicit confirmation)
* 🛑 `DELETE` (Requires approval before removing messages/emails)
* 🛑 `INSTALL_APP` / `CHANGE_SETTINGS` (Requires confirmation)

---

## 📦 Directory Structure

```text
NEXUS-IQOO/
├── nexus/
│   ├── android/
│   │   ├── accessibility/          # UI hierarchy parser, element selector, service interface
│   │   ├── screen/                 # Screen capture manager & ScreenObserver
│   │   ├── actions/                # ActionExecutor, AppLauncher, ADB dev bridge
│   │   └── verification/           # Post-action verification engine
│   ├── agent/
│   │   ├── interface/              # AgentBackend ABC
│   │   ├── planner/                # Structured JSON action planner
│   │   ├── memory/                 # Context and episodic memory
│   │   ├── tools/                  # Tool registry & SafetyGate
│   │   └── core.py                 # NexusAgent orchestrator
│   ├── speech/                     # Push-to-Talk controller & Local STT engine
│   ├── vision/                     # OCR fallback & visual screen descriptor
│   ├── models/                     # LocalModelProvider (Snapdragon NPU, ONNX, OpenJarvis, Remote)
│   ├── ui/                         # Futuristic terminal HUD with active badges
│   ├── cli.py                      # Main CLI entrypoint
│   └── config.py                   # Runtime configuration
├── tests/                          # 43 automated unit & integration tests
└── scripts/
    ├── run_demo.py                 # 6-step automated demo runner
    └── setup_device.sh             # ADB device connection verification script
```

---

## ⚡ Quick Start

### 1. Installation

```bash
git clone https://github.com/Ninad0109/NEXUS-IQOO.git
cd NEXUS-IQOO

# Install dependencies via uv or pip
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 2. Physical iQOO Device Setup (Optional)

1. Enable **Developer Options** on your iQOO phone (`Settings > About phone > Tap Build Number 7 times`).
2. Enable **USB Debugging** and **USB Debugging (Security settings)**.
3. Connect your phone via USB and run:
   ```bash
   ./scripts/setup_device.sh
   ```

### 3. Run the 6 Core Demos

```bash
# Run automated demo suite in simulation mode
python -m nexus demo

# Run live against connected iQOO device
python -m nexus demo --live
```

---

## 🎬 Demo Scenarios

| Demo | Spoken Command | Executed Action | Verification |
|---|---|---|---|
| **Demo 1** | *"Open WhatsApp"* | `OPEN_APP -> com.whatsapp` | Verified WhatsApp is foreground |
| **Demo 2** | *"Open Gmail and show me my latest emails"* | `OPEN_APP -> com.google.android.gm` | Verified Gmail is foreground |
| **Demo 3** | *"Open Chrome and search for Pune Metro"* | `OPEN_APP -> com.android.chrome` + `TYPE_TEXT` | Verified Chrome search query |
| **Demo 4** | *"What is currently on my screen?"* | `DESCRIBE_SCREEN` | Compact structured text summary |
| **Demo 5** | *"Go back"* | `BACK` (Keyevent 4) | Verified navigation |
| **Demo 6** | *"Take a screenshot"* | `TAKE_SCREENSHOT` | Screen frame buffer captured |

---

## 💻 Interactive Terminal HUD

Start an interactive push-to-talk session:

```bash
# Push-to-Talk with Snapdragon NPU inference mode
python -m nexus run --mode snapdragon_npu

# Push-to-Talk with Voice Microphone enabled
python -m nexus run --voice

# Dev mode with Cloud Fallback
python -m nexus run --mode remote_fallback
```

### Terminal Display Preview:
```text
╔════════════════════════════════════════════════════════════════╗
║  ⚡ NEXUS — iQOO On-Device AI Agent ⚡                         ║
║  Architecture: HEAR → OBSERVE → PLAN → ACT → VERIFY → RESPOND  ║
║  Active Engine: [LOCAL AI: Snapdragon NPU / QNN (Hexagon)]     ║
║  Hardware Target: iQOO / Snapdragon (Qualcomm Hexagon NPU)     ║
╚════════════════════════════════════════════════════════════════╝

[HEAR]     User Voice Input: "Open WhatsApp"
[OBSERVE]  Current Screen: Home (com.android.launcher)
[PLAN]     Plan: OPEN_APP -> com.whatsapp (WhatsApp)
[ACTION]   Dispatched OPEN_APP via Accessibility Layer
[VERIFY]   State verification: PASSED (WhatsApp is foreground)
[RESPOND]  Done — Opened WhatsApp
[DONE]     Turn completed in 34ms
```

---

## 🧪 Testing

Run the full test suite:

```bash
.venv/bin/pytest tests/test_*.py -v
```

---

## 📜 License

Apache-2.0.
