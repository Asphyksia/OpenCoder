"""
Agent Engine - Aider Wrapper for OpenCoder

This module provides a Python wrapper around Aider's coding engine,
capturing events and returning structured data instead of printing to console.

Reference: https://github.com/Aider-AI/aider
"""

import os
import re
import io
import asyncio
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from contextlib import redirect_stdout, redirect_stderr
from loguru import logger

# Configure litellm BEFORE importing aider
# This must be done at module level before aider loads
def _configure_litellm_early():
    """Configure litellm to use OpenGPU Relay at import time."""
    import os as _os
    _api_key = _os.getenv("OPENGPU_API_KEY", "")
    _base_url = _os.getenv("OPENGPU_BASE_URL", "https://relay.opengpu.network/v1")
    
    if _api_key:
        _os.environ["OPENAI_API_KEY"] = _api_key
        _os.environ["OPENAI_API_BASE"] = _base_url
        _os.environ["LITELLM_API_KEY"] = _api_key
        _os.environ["LITELLM_API_BASE"] = _base_url
        # Route all models through the relay
        _os.environ["OLLAMA_API_BASE"] = f"{_base_url}/ollama"
        _os.environ["ANTHROPIC_API_BASE"] = f"{_base_url}/anthropic"
        print(f"[OpenCoder] Configured litellm: base_url={_base_url}")

# Call early configuration
_configure_litellm_early()
del _configure_litellm_early

# Aider imports - optional, will be loaded if available
AIDER_AVAILABLE = False
try:
    from aider.coders import Coder
    from aider.io import InputOutput as AiderIO
    from aider import models
    # Repo and Audit may not exist in newer versions
    try:
        from aider.repo import Repo
    except ImportError:
        Repo = None
    try:
        from aider.audit import Audit
    except ImportError:
        Audit = None
    AIDER_AVAILABLE = True
    logger.info(f"Aider loaded successfully: Coder={Coder}, models={models}")
except ImportError as e:
    Coder = None
    models = None
    Repo = None
    Audit = None
    AiderIO = None
    logger.warning(f"Aider not available: {e}")



@dataclass
class FileChange:
    """Represents a file change made by the agent.
    
    Attributes:
        filename: Path to the modified file.
        diff: The diff/changes applied to the file.
        operation: Type of operation (created, modified, deleted).
    """
    filename: str
    diff: str
    operation: str = "modified"  # created, modified, deleted


@dataclass
class AgentEvent:
    """Represents an event during agent execution.
    
    Attributes:
        event_type: Type of event (thinking, planning, editing, error, etc.)
        content: The content/message of the event.
        timestamp: ISO timestamp when the event occurred.
    """
    event_type: str
    content: str
    timestamp: str = field(default_factory=lambda: asyncio.get_event_loop().time())


@dataclass
class AgentResponse:
    """Structured response from the agent engine.
    
    Attributes:
        success: Whether the operation completed successfully.
        message: Human-readable message about the result.
        events: List of events that occurred during execution.
        file_changes: List of file changes made.
        diffs: Combined diff output.
        error: Error message if any.
    """
    success: bool
    message: str
    events: list[AgentEvent] = field(default_factory=list)
    file_changes: list[FileChange] = field(default_factory=list)
    diffs: str = ""
    error: Optional[str] = None


class EventCapture(io.StringIO):
    """Custom StringIO to capture output and categorize it."""
    
    def __init__(self, event_callback: Optional[callable] = None) -> None:
        super().__init__()
        self.event_callback = event_callback
        self.buffer = ""
    
    def write(self, text: str) -> int:
        """Write text and optionally trigger callback."""
        if text.strip():
            self.buffer += text
            if self.event_callback:
                self.event_callback(text)
        return len(text)
    
    def flush(self) -> None:
        pass


class AgentEngine:
    """Wrapper around Aider's Coder class for programmatic use.
    
    This class encapsulates Aider's functionality while capturing
    all output and events in a structured format suitable for API responses.
    
    Attributes:
        repo_path: Path to the repository to work with.
        model: Model instance to use for coding.
        read_only: If True, don't make any changes (dry-run mode).
    
    Example:
        >>> from opencoder.core.opengpu_adapter import OpenGPUAdapter, AiderOpenGPUModel
        >>> adapter = OpenGPUAdapter()
        >>> model = AiderOpenGPUModel("gpt-4o", adapter)
        >>> engine = AgentEngine("./my-project", model)
        >>> result = await engine.execute("Add a hello world function")
    """
    
    def __init__(
        self,
        repo_path: str,
        model: Any,
        read_only: bool = False,
        pretty: bool = False,
        auto_commits: bool = True,
        commit_message: Optional[str] = None,
    ) -> None:
        """Initialize the Agent Engine.
        
        Args:
            repo_path: Path to the repository directory.
            model: Model instance (Aider-compatible).
            read_only: If True, prevent file modifications.
            pretty: Enable pretty-printed output.
            auto_commits: Automatically commit changes.
            commit_message: Custom commit message (if auto_commits=True).
        """
        self.repo_path = Path(repo_path).resolve()
        self.model = model
        self.read_only = read_only
        self.pretty = pretty
        self.auto_commits = auto_commits
        self.commit_message = commit_message
        
        self._coder: Optional[Coder] = None
        self._events: list[AgentEvent] = []
        self._file_changes: list[FileChange] = []
        self._last_output: str = ""
        
    def _add_event(self, event_type: str, content: str) -> None:
        """Add an event to the event list."""
        import time
        self._events.append(AgentEvent(
            event_type=event_type,
            content=content,
            timestamp=str(time.time())
        ))
    
    def _add_file_change(self, filename: str, diff: str, operation: str = "modified") -> None:
        """Add a file change to the changes list."""
        self._file_changes.append(FileChange(
            filename=filename,
            diff=diff,
            operation=operation
        ))
    
    def _configure_litellm(self) -> None:
        """Configure litellm to use OpenGPU Relay."""
        import litellm
        
        # Get API key from environment or model
        api_key = os.getenv("OPENGPU_API_KEY", "")
        base_url = os.getenv("OPENGPU_BASE_URL", "https://relay.opengpu.network/v1")
        
        # Always set these env vars for litellm
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = base_url
        os.environ["LITELLM_API_KEY"] = api_key
        os.environ["LITELLM_API_BASE"] = base_url
        
        # Also set for the model specifically
        os.environ["MODEL_API_KEY"] = api_key
        os.environ["MODEL_API_BASE"] = base_url
        
        self._add_event("system", f"Configured litellm: base_url={base_url}, [REDACTED]")

    def _setup_coder(self) -> Coder:
        """Set up and return the Aider Coder instance."""
        if self._coder is not None:
            return self._coder
        
        # Prepare model for Aider
        if hasattr(self.model, 'model_name'):
            model_name = self.model.model_name
        else:
            model_name = str(self.model)
        
        # Create model instance that Aider can use
        # Aider expects a models.Model subclass or similar interface
        try:
            # Try to get the underlying adapter
            if hasattr(self.model, 'adapter'):
                aider_model = models.Model(model_name)
            else:
                aider_model = models.Model(model_name)
        except Exception:
            # Fallback - Aider will handle model creation internally
            aider_model = models.Model(model_name)
        
        # Create the Coder instance with captured outputs
        # We use io.StringIO to capture what would be printed
        self._output_capture = io.StringIO()
        # Create Aider IO manager
        from aider.io import InputOutput
        self._aider_io = InputOutput(
            pretty=False,
            fancy_input=False,
            input=io.StringIO(),
            output=self._output_capture,
        )
        self._error_capture = io.StringIO()
        
        self._coder = Coder.create(
main_model=aider_model,
            io=self._aider_io,
            fnames=[] if self.repo_path else [],
            read_only_fnames=[] if self.read_only else None,  # New Aider API
            # pretty parameter removed
            auto_commits=self.auto_commits,
            # commit_message parameter removed
            verbose=False,
        )
        
        return self._coder
    
    async def execute(self, user_message: str) -> AgentResponse:
        """Execute a user message through the agent.
        
        This is the main entry point for running agent commands.
        It captures all events and returns structured data.
        
        Args:
            user_message: The user's request/command.
        
        Returns:
            AgentResponse with structured data about the execution.
        """
        self._events = []
        self._file_changes = []
        
        self._add_event("system", "Initializing agent engine...")
        
        try:
            # Ensure repo path exists
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True, exist_ok=True)
                self._add_event("system", f"Created repository directory: {self.repo_path}")
            
            # Set up coder
            coder = self._setup_coder()
            self._add_event("system", "Aider Coder initialized")
            
            # Run the user message through Aider
            # Aider's run() method takes a message and executes it
            self._add_event("user", user_message)
            
            # Capture output during execution
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    # Aider's run method - this is the main interaction loop
                    # We'll use a simple approach: send message and get response
                    self._add_event("thinking", "Processing your request...")
                    
                    # Run the chat with the user message
                    coder.run(user_message)
                    
                except Exception as e:
                    # Some errors are expected (like user wanting to exit)
                    error_msg = str(e)
                    if "EOF" in error_msg or "exit" in error_msg.lower():
                        # Normal termination
                        self._add_event("complete", "Operation completed")
                    else:
                        raise
            
            # Capture outputs
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            # Parse outputs for events
            self._parse_coder_output(stdout_output)
            self._parse_coder_output(stderr_output)
            
            # Get file changes from Aider's internal state
            self._capture_file_changes(coder)
            
            # Build the response
            diffs_text = "\n".join([fc.diff for fc in self._file_changes])
            
            success = len(self._file_changes) > 0 or "complete" in [e.event_type for e in self._events]
            
            return AgentResponse(
                success=success,
                message=f"Processed: {user_message[:50]}...",
                events=self._events,
                file_changes=self._file_changes,
                diffs=diffs_text,
                error=None
            )
            
        except Exception as e:
            error_msg = str(e)
            self._add_event("error", error_msg)
            return AgentResponse(
                success=False,
                message="Error during execution",
                events=self._events,
                file_changes=self._file_changes,
                diffs="",
                error=error_msg
            )
    
    def _parse_coder_output(self, output: str) -> None:
        """Parse Aider's output and categorize events."""
        if not output:
            return
        
        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Categorize output by patterns
            if "git" in line.lower() or "commit" in line.lower():
                self._add_event("git", line)
            elif "file" in line.lower() and ("created" in line.lower() or "modified" in line.lower()):
                self._add_event("file", line)
            elif "error" in line.lower() or "exception" in line.lower():
                self._add_event("error", line)
            elif any(word in line.lower() for word in ["thinking", "analyzing", "processing"]):
                self._add_event("thinking", line)
            else:
                # General output
                if line:
                    self._add_event("output", line)
    
    def _capture_file_changes(self, coder: Coder) -> None:
        """Capture file changes from the Coder instance.
        
        Aider tracks file changes internally. We extract them here.
        """
        # Try to get file information from coder
        # This depends on Aider's internal structure
        try:
            # Aider tracks repo changes via the repo object
            if hasattr(coder, 'repo') and coder.repo:
                repo: Repo = coder.repo
                
                # Check for tracked files
                if hasattr(repo, 'get_tracked_files'):
                    tracked_files = repo.get_tracked_files()
                    for filepath in tracked_files:
                        # Create a placeholder diff entry
                        # In a full implementation, we'd get actual diffs
                        self._add_file_change(
                            filename=str(filepath),
                            diff=f"[Tracked file: {filepath}]",
                            operation="modified"
                        )
        except Exception:
            pass  # Non-critical - continue without file tracking
    
    async def get_commit_message(self) -> Optional[str]:
        """Get the commit message for current changes.
        
        Uses Aider's get_commit_message method if available.
        
        Returns:
            Commit message string or None.
        """
        try:
            coder = self._setup_coder()
            if hasattr(coder, 'get_commit_message'):
                return coder.get_commit_message()
        except Exception:
            pass
        return None
    
    def get_status(self) -> dict[str, Any]:
        """Get the current status of the repository.
        
        Returns:
            Dictionary with repository status information.
        """
        status = {
            "repo_path": str(self.repo_path),
            "read_only": self.read_only,
            "events_count": len(self._events),
            "file_changes_count": len(self._file_changes),
        }
        
        try:
            if self._coder and hasattr(self._coder, 'repo'):
                repo = self._coder.repo
                status["repo_exists"] = True
                
                # Try to get git status
                if hasattr(repo, 'git_status'):
                    status["git_status"] = repo.git_status()
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def reset(self) -> None:
        """Reset the engine state."""
        self._events = []
        self._file_changes = []
        self._last_output = ""
        # Keep the coder instance for continuity


class SimpleAgentEngine:
    """Simplified agent engine for basic operations.
    
    This is a lighter-weight alternative that doesn't require
    a full Aider setup. Useful for quick operations.
    """
    
    def __init__(
        self,
        repo_path: str,
        model: Any,
    ) -> None:
        """Initialize the simple agent engine.
        
        Args:
            repo_path: Path to the repository.
            model: Model instance for generating responses.
        """
        self.repo_path = Path(repo_path)
        self.model = model
        self._conversation_history: list[dict[str, str]] = []
    
    async def chat(self, message: str) -> dict[str, Any]:
        """Send a chat message and get a response.
        
        Args:
            message: User message.
        
        Returns:
            Response dictionary.
        """
        # Add user message to history
        self._conversation_history.append({"role": "user", "content": message})
        
        try:
            # Get response from model
            if hasattr(self.model, 'chat'):
                response = await self.model.chat(self._conversation_history)
            else:
                # Direct adapter call
                response = await self.model.adapter.chat_complete(
                    messages=self._conversation_history,
                    model=self.model.model_name
                )
            
            # Extract assistant response - handle both OpenAI and Ollama formats
            if hasattr(response, 'choices'):
                # OpenAI SDK object
                assistant_message = response.choices[0].message.content
            elif isinstance(response, dict):
                # Plain dict response - check for OpenAI format first (choices array)
                choices = response.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    if isinstance(msg, dict):
                        assistant_message = msg.get("content", str(response))
                    else:
                        assistant_message = str(msg)
                else:
                    # Ollama format: {"message": {"content": "..."}}
                    msg = response.get("message", {})
                    assistant_message = msg.get("content", str(response))
            else:
                assistant_message = str(response)
            
            # Add to history
            self._conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                "success": True,
                "message": assistant_message,
                "events": [{"event_type": "chat", "content": "Response generated"}],
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": "",
                "events": [{"event_type": "error", "content": str(e)}],
                "error": str(e)
            }
    
    def get_history(self) -> list[dict[str, str]]:
        """Get the conversation history.
        
        Returns:
            List of message dictionaries.
        """
        return self._conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []


class AiderCLIEngine:
    """Aider CLI wrapper for real agentic coding.
    
    This class runs Aider as a subprocess, providing real file editing
    capabilities with proper context and git integration.
    """
    
    def __init__(
        self,
        repo_path: str,
        model_name: str,
        read_only: bool = False,
        auto_commits: bool = False,
        event_callback: Optional[callable] = None,
    ) -> None:
        """Initialize the Aider CLI engine.
        
        Args:
            repo_path: Path to the repository directory.
            model_name: Model to use (e.g., "gpt-4o", "claude-sonnet-4-6").
            read_only: If True, prevent file modifications.
            auto_commits: If True, automatically commit changes.
            event_callback: Optional callback for streaming events.
        """
        self.repo_path = Path(repo_path).resolve()
        self.model_name = model_name
        self.read_only = read_only
        self.auto_commits = auto_commits
        self.event_callback = event_callback
        
        self._conversation_history: list[dict[str, str]] = []
        self._events: list[AgentEvent] = []
        self._file_changes: list[FileChange] = []
        
    def _add_event(self, event_type: str, content: str) -> None:
        """Add an event and call callback if present."""
        import time
        event = AgentEvent(
            event_type=event_type,
            content=content,
            timestamp=str(time.time())
        )
        self._events.append(event)
        
        if self.event_callback:
            self.event_callback(event)
    
    def _discover_files(self) -> list[str]:
        """Discover source files in the repository.
        
        Returns:
            List of file paths to include in context.
        """
        if not self.repo_path.exists():
            return []
        
        # Common source file extensions
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb', '.php', '.swift', '.kt'}
        files = []
        
        for ext in extensions:
            files.extend(self.repo_path.rglob(f'*{ext}'))
        
        # Filter out common ignore patterns
        ignored_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next'}
        
        filtered = []
        for f in files:
            # Skip ignored directories
            if any(ignored in f.parts for ignored in ignored_dirs):
                continue
            filtered.append(str(f))
        
        return filtered[:50]  # Limit to 50 files for context
    
    def _get_git_diff(self) -> str:
        """Get git diff of changes.
        
        Returns:
            Git diff output as string.
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except Exception as e:
            self._add_event("error", f"Failed to get git diff: {e}")
            return ""
    
    def _parse_git_diff(self, diff_text: str) -> list[FileChange]:
        """Parse git diff into FileChange objects.
        
        Args:
            diff_text: Raw git diff output.
            
        Returns:
            List of FileChange objects.
        """
        changes = []
        current_file = None
        current_diff = []
        
        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    changes.append(FileChange(
                        filename=current_file,
                        diff='\n'.join(current_diff),
                        operation='modified'
                    ))
                # Extract filename from: diff --git a/path b/path
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[2].replace('a/', '')
                    current_diff = [line]
            elif current_file:
                current_diff.append(line)
        
        if current_file:
            changes.append(FileChange(
                filename=current_file,
                diff='\n'.join(current_diff),
                operation='modified'
            ))
        
        return changes
    
    def _get_env(self) -> dict[str, str]:
        """Get environment variables for Aider subprocess.
        
        Returns:
            Dictionary of environment variables.
        """
        import os
        env = os.environ.copy()
        
        # Configure for OpenGPU Relay
        api_key = os.getenv("OPENGPU_API_KEY", "")
        base_url = os.getenv("OPENGPU_BASE_URL", "https://relay.opengpu.network/v1")
        
        if api_key:
            env["OPENAI_API_KEY"] = api_key
            env["OPENAI_API_BASE"] = f"{base_url}/openai"
            env["ANTHROPIC_API_KEY"] = api_key
            env["ANTHROPIC_API_BASE"] = f"{base_url}/anthropic"
            env["OLLAMA_API_BASE"] = f"{base_url}/ollama"
        
        return env
    
    async def execute(self, message: str) -> AgentResponse:
        """Execute a message using Aider CLI.
        
        Args:
            message: User message/command.
            
        Returns:
            AgentResponse with results and file changes.
        """
        import asyncio
        import subprocess
        
        self._events = []
        self._file_changes = []
        
        self._add_event("system", f"Starting Aider with model: {self.model_name}")
        
        try:
            # Ensure repo path exists
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True, exist_ok=True)
                # Initialize git repo if needed
                subprocess.run(['git', 'init'], cwd=str(self.repo_path), capture_output=True)
                self._add_event("system", f"Initialized git repository: {self.repo_path}")
            
            # Discover files for context
            context_files = self._discover_files()
            if context_files:
                self._add_event("system", f"Found {len(context_files)} files in repository")
            
            # Build aider command
            cmd = [
                'aider',
                '--model', self.model_name,
                '--message', message,
                '--no-auto-commits' if not self.auto_commits else '--auto-commits',
                '--pretty',
                '--yes',  # Auto-confirm
            ]
            
            if self.read_only:
                cmd.append('--read-only')
            
            # Add context files
            for f in context_files[:20]:  # Limit to 20 files
                cmd.extend(['--file', f])
            
            self._add_event("thinking", "Processing your request...")
            
            # Run Aider with timeout
            try:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        cwd=str(self.repo_path),
                        env=self._get_env(),
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    ),
                    timeout=120.0  # 2 minute timeout
                )
                
                # Send message and get response
                stdout, stderr = await process.communicate()
                
            except asyncio.TimeoutError:
                # Kill the process on timeout
                process.kill()
                await process.wait()
                self._add_event("error", "Aider command timed out after 2 minutes")
                return AgentResponse(
                    success=False,
                    message="Command timed out",
                    events=self._events,
                    file_changes=[],
                    diffs="",
                    error="Timeout after 120 seconds"
                )
            
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Parse output for events
            self._add_event("output", stdout_text[:1000] if stdout_text else "No output")
            
            if stderr_text:
                self._add_event("error", stderr_text[:500] if "error" in stderr_text.lower() else "")
            
            # Get git diff
            self._add_event("system", "Capturing file changes...")
            diff_text = self._get_git_diff()
            
            if diff_text:
                self._file_changes = self._parse_git_diff(diff_text)
                self._add_event("system", f"Found {len(self._file_changes)} file changes")
            else:
                self._add_event("system", "No file changes detected")
            
            # Build response
            success = process.returncode == 0 or len(self._file_changes) > 0
            
            return AgentResponse(
                success=success,
                message=f"Executed: {message[:50]}...",
                events=self._events,
                file_changes=self._file_changes,
                diffs=diff_text[:5000] if diff_text else "",  # Limit diff size
                error=None if success else f"Exit code: {process.returncode}"
            )
            
        except asyncio.TimeoutError:
            self._add_event("error", "Aider command timed out")
            return AgentResponse(
                success=False,
                message="Command timed out",
                events=self._events,
                file_changes=[],
                diffs="",
                error="Timeout"
            )
        except Exception as e:
            error_msg = str(e)
            self._add_event("error", error_msg)
            return AgentResponse(
                success=False,
                message="Error during execution",
                events=self._events,
                file_changes=self._file_changes,
                diffs="",
                error=error_msg
            )
    
    def get_status(self) -> dict[str, Any]:
        """Get status of the repository.
        
        Returns:
            Dictionary with repository status.
        """
        import subprocess
        
        status = {
            "repo_path": str(self.repo_path),
            "read_only": self.read_only,
            "events_count": len(self._events),
            "file_changes_count": len(self._file_changes),
        }
        
        try:
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            status["git_status"] = result.stdout
            status["has_changes"] = bool(result.stdout.strip())
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def reset(self) -> None:
        """Reset engine state."""
        self._events = []
        self._file_changes = []
