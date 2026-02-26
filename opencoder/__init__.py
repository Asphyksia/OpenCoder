"""
OpenCoder - Agentic Coding Tool

A tool for AI-powered code editing using Aider and OpenGPU Relay.
"""

__version__ = "0.1.0"
__author__ = "OpenCoder Team"

# Import core components
from opencoder.core import OpenGPUAdapter

# Import AgentEngine if available
try:
    from opencoder.core import AgentEngine
except ImportError:
    AgentEngine = None

# Import FastAPI app
from opencoder.api.main import app

__all__ = [
    "OpenGPUAdapter",
    "AgentEngine",
    "app",
]
