"""Global runtime configuration for NEXUS agent."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Literal


@dataclass
class NexusConfig:
    """NEXUS Agent Configuration."""

    # Device & ADB Configuration
    device_id: str = field(default_factory=lambda: os.getenv("NEXUS_DEVICE_ID", ""))
    adb_path: str = field(default_factory=lambda: os.getenv("NEXUS_ADB_PATH", "adb"))
    adb_timeout_sec: float = 10.0
    use_simulation_mode: bool = field(
        default_factory=lambda: os.getenv("NEXUS_SIMULATION_MODE", "false").lower() in ("true", "1", "yes")
    )

    # Model & Inference Configuration
    model_mode: Literal["snapdragon_npu", "onnx", "openjarvis", "remote_fallback"] = field(
        default_factory=lambda: os.getenv("NEXUS_MODEL_MODE", "openjarvis")  # type: ignore
    )
    model_endpoint: str = field(default_factory=lambda: os.getenv("NEXUS_MODEL_ENDPOINT", "http://localhost:8000/v1"))
    model_name: str = field(default_factory=lambda: os.getenv("NEXUS_MODEL_NAME", "nexus-local-v1"))
    api_key: str = field(default_factory=lambda: os.getenv("NEXUS_API_KEY", ""))

    # Voice / STT Configuration
    stt_engine: Literal["whisper_local", "vosk", "mock", "cloud"] = field(
        default_factory=lambda: os.getenv("NEXUS_STT_ENGINE", "whisper_local")  # type: ignore
    )
    whisper_model_size: str = "tiny.en"  # Optimized for low-latency on-device/laptop inference

    # Safety Guardrails
    enable_safety_gates: bool = True
    auto_confirm_safe_actions: bool = True

    # Screen Observation
    max_screen_elements: int = 40
    screen_capture_interval_sec: float = 0.5

    # Storage paths
    artifact_dir: Path = field(default_factory=lambda: Path(os.getenv("NEXUS_ARTIFACT_DIR", "/tmp/nexus_artifacts")))

    def __post_init__(self):
        self.artifact_dir.mkdir(parents=True, exist_ok=True)


_GLOBAL_CONFIG: NexusConfig | None = None


def get_config() -> NexusConfig:
    """Returns the global active NexusConfig instance."""
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is None:
        _GLOBAL_CONFIG = NexusConfig()
    return _GLOBAL_CONFIG


def set_config(config: NexusConfig) -> None:
    """Sets the global NexusConfig instance."""
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = config
