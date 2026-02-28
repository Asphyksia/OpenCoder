"""
OpenCoder Core Module

This module contains the core functionality for the OpenCoder agentic coding tool,
including the OpenGPU adapter and Agent Engine.
"""

from opencoder.core.opengpu_adapter import (
    OpenGPUAdapter,
    OpenGPUConfig,
    AiderOpenGPUModel,
)

# Import AiderBridge - works via subprocess, no Python version issues
from opencoder.core.aider_bridge import (
    AiderBridge,
    AiderResult,
    create_aider_bridge,
)

# Import AgentEngine - may fail if Aider is not available
try:
    from opencoder.core.agent_engine import AgentEngine, SimpleAgentEngine
    __all__ = [
        "OpenGPUAdapter",
        "OpenGPUConfig", 
        "AiderOpenGPUModel",
        "AiderBridge",
        "AiderResult",
        "create_aider_bridge",
        "AgentEngine",
        "SimpleAgentEngine",
    ]
except ImportError:
    AgentEngine = None
    SimpleAgentEngine = None
    __all__ = [
        "OpenGPUAdapter",
        "OpenGPUConfig", 
        "AiderOpenGPUModel",
        "AiderBridge",
        "AiderResult",
        "create_aider_bridge",
    ]
