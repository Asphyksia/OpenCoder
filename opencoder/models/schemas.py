"""
Pydantic Models for OpenCoder API

This module defines the request and response schemas for the REST API.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for the /chat endpoint.
    
    Attributes:
        message: The user's message/command.
        model: Model identifier to use (e.g., "gpt-4o").
        read_only: If True, don't make file changes.
    """
    message: str = Field(..., min_length=1, description="User message or command")
    model: Optional[str] = Field(None, description="Model identifier")
    read_only: Optional[bool] = Field(False, description="Prevent file modifications")


class FileChangeSchema(BaseModel):
    """Schema for a file change.
    
    Attributes:
        filename: Path to the modified file.
        diff: The diff/changes applied.
        operation: Type of operation (created, modified, deleted).
    """
    filename: str
    diff: str
    operation: str


class EventSchema(BaseModel):
    """Schema for an agent event.
    
    Attributes:
        event_type: Type of event (thinking, planning, editing, error, etc.)
        content: The event content.
        timestamp: ISO timestamp.
    """
    event_type: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    """Response model for the /chat endpoint.
    
    Attributes:
        success: Whether the operation succeeded.
        message: Human-readable result message.
        events: List of events that occurred.
        file_changes: List of file modifications.
        diffs: Combined diff output.
        error: Error message if failed.
    """
    success: bool
    message: str
    events: list[EventSchema] = Field(default_factory=list)
    file_changes: list[FileChangeSchema] = Field(default_factory=list)
    diffs: str = ""
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """Response model for the /status endpoint.
    
    Attributes:
        status: Overall status (ready, busy, error).
        repo_path: Path to the working repository.
        read_only: Whether in read-only mode.
        events_count: Number of events in current session.
        file_changes_count: Number of file changes in current session.
        available_models: List of available models.
        error: Error message if any.
    """
    status: str
    repo_path: str
    read_only: bool
    events_count: int = 0
    file_changes_count: int = 0
    available_models: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check.
    
    Attributes:
        status: Health status (healthy, degraded, unhealthy).
        version: API version.
    """
    status: str
    version: str
