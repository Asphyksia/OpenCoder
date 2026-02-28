"""
OpenCoder API - FastAPI Application

REST API for the OpenCoder agentic coding tool.
Provides endpoints for chat interaction and repository status.

Endpoints:
    - POST /chat: Send a message and receive agent response
    - GET /status: Get current repository status
    - GET /health: Health check endpoint
    - GET /models: List available models
"""

import os
import uuid
from typing import Dict, Optional
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from opencoder.models import (
    ChatRequest,
    ChatResponse,
    StatusResponse,
    HealthResponse,
    EventSchema,
    FileChangeSchema,
)
from opencoder.core import OpenGPUAdapter, AiderOpenGPUModel
from opencoder.core.agent_engine import AgentEngine, SimpleAgentEngine, AiderCLIEngine
from opencoder.core.aider_bridge import AiderBridge, AiderResult


# Global state management
class AgentState:
    """Manages the state of the agent engine and AiderBridge."""
    
    def __init__(self) -> None:
        self.engines: Dict[str, AgentEngine] = {}
        self.bridges: Dict[str, AiderBridge] = {}  # AiderBridge for subprocess execution
        self.adapter: Optional[OpenGPUAdapter] = None
        self.session_id: Optional[str] = None
    
    def get_or_create_bridge(
        self,
        session_id: str,
        repo_path: str,
        model_name: str,
        read_only: bool = False
    ) -> AiderBridge:
        """Get existing bridge or create new one for session."""
        if session_id not in self.bridges:
            # Use AiderBridge - executes Aider CLI as subprocess
            # This bypasses Python version compatibility issues
            self.bridges[session_id] = AiderBridge(
                repo_path=repo_path,
                model=model_name,
                read_only=read_only,
            )
        
        return self.bridges[session_id]
    
    def get_or_create_engine(
        self,
        session_id: str,
        repo_path: str,
        model_name: str,
        read_only: bool = False
    ) -> AgentEngine:
        """Get existing engine or create new one for session."""
        if session_id not in self.engines:
            # Use SimpleAgentEngine - it's more reliable and works with OpenGPU directly
            # SimpleAgentEngine uses litellm directly without Aider CLI dependencies
            from opencoder.core.opengpu_adapter import OpenGPUAdapter, AiderOpenGPUModel
            
            # Create adapter and model for OpenGPU
            adapter = OpenGPUAdapter()
            open_gpu_model = AiderOpenGPUModel(model_name, adapter)
            
            self.engines[session_id] = SimpleAgentEngine(
                repo_path=repo_path,
                model=open_gpu_model
            )
        
        return self.engines[session_id]
    
    def get_engine(self, session_id: str) -> Optional[AgentEngine]:
        """Get engine for session if exists."""
        return self.engines.get(session_id)
    
    def get_bridge(self, session_id: str) -> Optional[AiderBridge]:
        """Get bridge for session if exists."""
        return self.bridges.get(session_id)
    
    def close_session(self, session_id: str) -> None:
        """Close and remove session."""
        if session_id in self.engines:
            del self.engines[session_id]
        if session_id in self.bridges:
            del self.bridges[session_id]


# Global state instance
agent_state = AgentState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting OpenCoder API...")
    yield
    # Shutdown
    logger.info("Shutting down OpenCoder API...")
    if agent_state.adapter:
        await agent_state.adapter.close()


# Create FastAPI app
app = FastAPI(
    title="OpenCoder API",
    description="Agentic Coding Tool powered by Aider and OpenGPU Relay",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware - restrict to allowed origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def get_repo_path() -> str:
    """Get repository path from environment or use default."""
    return os.getenv("OPENCODER_REPO_PATH", "./workspace")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "OpenCoder API",
        "version": "0.1.0",
        "description": "Agentic Coding Tool powered by Aider and OpenGPU Relay"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )


@app.get("/models", tags=["Models"])
async def list_models():
    """List available models from OpenGPU Relay.
    
    Returns:
        List of available model identifiers with details.
    """
    try:
        if agent_state.adapter is None:
            agent_state.adapter = OpenGPUAdapter()
        
        models = await agent_state.adapter.get_available_models()
        return {"models": models, "count": len(models)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}"
        )


@app.get("/pricing", tags=["Models"])
async def list_pricing():
    """Get pricing information from OpenGPU Relay.
    
    Returns:
        List of pricing information for all models.
    """
    try:
        if agent_state.adapter is None:
            agent_state.adapter = OpenGPUAdapter()
        
        pricing = await agent_state.adapter.get_pricing()
        return {"pricing": pricing, "count": len(pricing)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pricing: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, session_id: Optional[str] = None):
    """Send a message to the agent and receive a response.
    
    This endpoint orchestrates the interaction between the user,
    the OpenGPU model, and Aider's coding engine via AiderBridge.
    
    Args:
        request: Chat request with message and optional model.
        session_id: Optional session identifier for continuity.
    
    Returns:
        ChatResponse with events, file changes, and diffs.
    """
    # Use provided session_id or generate new one
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get configuration
    repo_path = get_repo_path()
    model_name = request.model or os.getenv("OPENGPU_MODEL", "")
    
    try:
        # Get or create AiderBridge for session
        # AiderBridge uses subprocess to run Aider CLI, bypassing Python version issues
        bridge = agent_state.get_or_create_bridge(
            session_id=session_id,
            repo_path=repo_path,
            model_name=model_name,
            read_only=request.read_only
        )
        
        # Execute the user's message via AiderBridge
        result = await bridge.execute(request.message)
        
        # Convert AiderResult to ChatResponse format
        return ChatResponse(
            success=result.success,
            message=result.message,
            events=[
                EventSchema(
                    event_type='aider_output',
                    content=result.output[:1000] if result.output else '',  # Limit output length
                    timestamp=""
                )
            ],
            file_changes=[
                FileChangeSchema(
                    filename=fc,
                    diff=result.diffs,
                    operation='modified'
                )
                for fc in result.files_changed
            ],
            diffs=result.diffs,
            error=result.error
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status(session_id: Optional[str] = None):
    """Get the status of the repository.
    
    Returns information about the current working repository,
    including file changes and event counts.
    
    Args:
        session_id: Optional session identifier.
    
    Returns:
        StatusResponse with repository information.
    """
    repo_path = get_repo_path()
    
    # Try to get engine for session
    engine = None
    if session_id:
        engine = agent_state.get_engine(session_id)
    
    # Get available models
    available_models = []
    try:
        if agent_state.adapter is None:
            agent_state.adapter = OpenGPUAdapter()
        models = await agent_state.adapter.get_available_models()
        # Extract model names from the list of dicts
        available_models = [m.get("name", str(m)) for m in models]
    except Exception:
        pass
    
    # Build status response
    status_info = {
        "status": "ready" if engine else "no_session",
        "repo_path": repo_path,
        "read_only": False,
        "events_count": 0,
        "file_changes_count": 0,
        "available_models": available_models,
        "error": None
    }
    
    if engine:
        engine_status = engine.get_status()
        status_info["events_count"] = engine_status.get("events_count", 0)
        status_info["file_changes_count"] = engine_status.get("file_changes_count", 0)
        status_info["read_only"] = engine_status.get("read_only", False)
    
    return StatusResponse(**status_info)


@app.delete("/session/{session_id}", tags=["Session"])
async def close_session(session_id: str):
    """Close a session and cleanup resources.
    
    Args:
        session_id: Session identifier to close.
    
    Returns:
        Confirmation message.
    """
    agent_state.close_session(session_id)
    return {"message": f"Session {session_id} closed", "success": True}


# ============================================================================
# Run instructions (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    OpenCoder API                          ║
    ║              Agentic Coding Tool v0.1.0                   ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  To run the server:                                         ║
    ║                                                             ║
    ║    uvicorn opencoder.api.main:app --reload --port 8000    ║
    ║                                                             ║
    ║  Or with Python:                                            ║
    ║    python -m uvicorn opencoder.api.main:app --reload       ║
    ║                                                             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
