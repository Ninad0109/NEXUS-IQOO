"""NEXUS — iQOO On-Device Phone AI Agent.

Phone-native agentic AI system designed for Snapdragon/iQOO mobile devices.
Architecture: HEAR -> OBSERVE -> PLAN -> ACT -> VERIFY -> RESPOND.
"""

__version__ = "0.1.0"
__app_name__ = "NEXUS"

from nexus.config import NexusConfig, get_config

__all__ = ["NexusConfig", "get_config", "__version__", "__app_name__"]
