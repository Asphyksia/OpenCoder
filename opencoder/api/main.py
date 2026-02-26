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

from opencoder.models import (
    ChatRequest,
    ChatResponse,
    StatusResponse,
    HealthResponse,
    EventSchema,
    FileChangeSchema,
)
from opencoder.core import OpenGPUAdapter, AiderOpenGPUModel
from opencoder.core.agent_engine import AgentEngine, SimpleAgentEngine


# Global state management
class AgentState:
    """Manages the state of the agent engine."""
    
    def __init__(self) -> None:
        self.engines: Dict[str, AgentEngine] = {}
        self.adapter: Optional[OpenGPUAdapter] = None
        self.session_id: Optional[str] = None
    
    def get_or_create_engine(
        self,
        session_id: str,
        repo_path: str,
        model_name: str,
        read_only: bool = False
    ) -> AgentEngine:
        """Get existing engine or create new one for session."""
        if session_id not in self.engines:
            # Create new model and engine
            if self.adapter is None:
                self.adapter = OpenGPUAdapter()
            
            model = AiderOpenGPUModel(model_name, self.adapter)
            self.engines[session_id] = AgentEngine(
                repo_path=repo_path,
                model=model,
                read_only=read_only
            )
        
        return self.engines[session_id]
    
    def get_engine(self, session_id: str) -> Optional[AgentEngine]:
        """Get engine for session if exists."""
        return self.engines.get(session_id)
    
    def close_session(self, session_id: str) -> None:
        """Close and remove session."""
        if session_id in self.engines:
            del self.engines[session_id]


# Global state instance
agent_state = AgentState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting OpenCoder API...")
    yield
    # Shutdown
    print("Shutting down OpenCoder API...")
    if agent_state.adapter:
        await agent_state.adapter.close()


# Create FastAPI app
app = FastAPI(
    title="OpenCoder API",
    description="Agentic Coding Tool powered by Aider and OpenGPU Relay",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
    the OpenGPU model, and Aider's coding engine.
    
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
    model_name = request.model or os.getenv("OPENGPU_MODEL", "gpt-4o")
    
    try:
        # Get or create engine for session
        engine = agent_state.get_or_create_engine(
            session_id=session_id,
            repo_path=repo_path,
            model_name=model_name,
            read_only=request.read_only
        )
        
        # Execute the user's message
        result = await engine.execute(request.message)
        
        # Convert to response model
        return ChatResponse(
            success=result.success,
            message=result.message,
            events=[
                EventSchema(
                    event_type=e.event_type,
                    content=e.content,
                    timestamp=e.timestamp
                )
                for e in result.events
            ],
            file_changes=[
                FileChangeSchema(
                    filename=fc.filename,
                    diff=fc.diff,
                    operation=fc.operation
                )
                for fc in result.file_changes
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
        available_models = await agent_state.adapter.get_available_models()
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
