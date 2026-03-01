"""
AiderBridge - Puente entre FastAPI y Aider CLI

Este módulo proporciona una interfaz para ejecutar Aider CLI como subprocess,
permitiendo usar todas las capacidades de Aider desde un backend Python 3.13.

IMPORTANT: The litellm patch must be imported BEFORE any litellm/aider import.
"""

# FIRST: Patch litellm for OpenGPU (before any litellm imports)
from opencoder.core.litellm_patch import patch_litellm_for_opengpu
patch_litellm_for_opengpu()

# AFTER: Normal imports
import os
import re
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class AiderResult:
    """Resultado de ejecutar Aider."""
    success: bool
    message: str
    output: str
    diffs: str = ""
    files_changed: List[str] = field(default_factory=list)
    error: Optional[str] = None


class AiderBridge:
    """
    Puente para ejecutar Aider CLI como subprocess.
    
    Requiere que Aider esté instalado via:
        python -m pip install aider-install
        aider-install
    
    Esto crea un entorno aislado con Python 3.12 donde Aider funciona correctamente.
    """
    
    def __init__(
        self,
        repo_path: str,
        model: str = "",
        api_key: Optional[str] = None,
        base_url: str = "https://relaygpu.com/backend/openai/v1",
        auto_commits: bool = True,
        read_only: bool = False,
    ):
        """
        Inicializa el puente de Aider.
        
        Args:
            repo_path: Ruta al repositorio de código.
            model: Modelo a usar (sin prefijo openai/ para OpenGPU).
            api_key: API key de OpenGPU. Si no se proporciona, usa OPENGPU_API_KEY.
            base_url: URL base de OpenGPU.
            auto_commits: Si True, hace commits automáticos.
            read_only: Si True, no hace cambios reales.
        """
        self.repo_path = Path(repo_path).resolve()
        self.model = model
        self.api_key = api_key or os.getenv("OPENGPU_API_KEY", "")
        self.base_url = base_url
        self.auto_commits = auto_commits
        self.read_only = read_only
        
        # Verificar que el directorio existe
        if not self.repo_path.exists():
            self.repo_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[AiderBridge] Inicializado: repo={self.repo_path}, model={self.model}")
    
    def _build_env(self) -> Dict[str, str]:
        """Construye el entorno de variables para Aider."""
        env = os.environ.copy()
        
        # Configuración de OpenGPU para Aider
        env["OPENAI_API_KEY"] = self.api_key
        env["OPENAI_API_BASE"] = self.base_url
        
        # Para litellm (usado internamente por Aider)
        env["LITELLM_API_KEY"] = self.api_key
        env["LITELLM_API_BASE"] = self.base_url
        
        # Prevent litellm from doing provider auto-detection
        # This is needed for custom model names like Qwen/Qwen3-Coder
        env["LITELLM_DROP_PARAMS"] = "true"
        env["LITELLM_MAX_PARALLEL_REQUESTS"] = "100"
        
        return env
    
    def _find_aider_command(self) -> List[str]:
        """Encuentra el comando de Aider instalado.
        
        Returns:
            Lista de comandos para ejecutar Aider via uv tool with litellm patch.
        """
        # Use uv from PATH - it should be available in the environment
        import shutil
        uv_path = shutil.which("uv")
        if not uv_path:
            raise RuntimeError("uv not found in PATH. Please ensure uv is installed and available.")
        
        # Get the path to our wrapper script
        import pathlib
        wrapper_path = pathlib.Path(__file__).parent.parent.parent / "scripts" / "aider_with_patch.py"
        
        # Use uv to run our wrapper script which patches litellm before running aider
        # We need to add dependencies (httpx, loguru) to the environment
        return [
            uv_path, "tool", "run",
            "--with", "httpx",
            "--with", "loguru",
            "--from", "aider-chat",
            "python", str(wrapper_path)
        ]
    
    async def execute(
        self,
        message: str,
        files: Optional[List[str]] = None,
    ) -> AiderResult:
        """
        Ejecuta un comando de Aider.
        
        Args:
            message: Mensaje/instrucción para Aider.
            files: Lista de archivos a incluir (relativos al repo_path).
        
        Returns:
            AiderResult con el resultado de la ejecución.
        """
        # Construir comando - use extend to add the command list
        cmd = []
        cmd.extend(self._find_aider_command())  # Add the command executable(s)
        
        # Handle model name for litellm
        # litellm needs explicit provider for unknown models like Qwen
        # Since base_url is openai-compatible, we can try different approaches
        # 
        # Approach 1: Use just the model name part (e.g., "Qwen/Qwen3-Coder")
        # This requires litellm to not do provider auto-detection
        #
        # Approach 2: Set LITELLM_DROP_PARAMS to skip validation
        # Only strip "openai/" prefix - other providers like moonshotai, qwen, deepseek-ai
        # are NOT standard litellm providers and should be kept as part of the model name
        if self.model.startswith("openai/"):
            model_to_use = self.model[7:]  # Remove "openai/" prefix
        else:
            model_to_use = self.model  # Keep full model name (e.g., "moonshotai/kimi-k2.5")
        
        # For litellm with custom base URLs, we need to prevent provider auto-detection
        # by setting special environment variables
        model_arg = f"--model={model_to_use}"
        
        # Add to cmd the flag to skip model warnings
        cmd.append("--no-show-model-warnings")
        
        cmd.extend([
            model_arg,
            f"--message={message}",
            "--yes",  # Auto-confirmar
            "--no-stream",  # Output completo al final
        ])
        
        if self.auto_commits:
            cmd.append("--auto-commits")
        else:
            cmd.append("--no-auto-commits")
        
        if self.read_only:
            cmd.append("--dry-run")
        
        # Añadir archivos
        if files:
            for f in files:
                file_path = self.repo_path / f
                if file_path.exists():
                    cmd.append(str(file_path))
        else:
            # Si no hay archivos específicos, añadir todos los .py del repo
            py_files = list(self.repo_path.glob("*.py"))[:10]
            for f in py_files:
                cmd.append(str(f))
        
        # Log the command
        cmd_str = ' '.join(cmd)
        logger.info(f"[AiderBridge] Ejecutando: {cmd_str[:100]}...")
        
        try:
            # Ejecutar subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_path),
                env=self._build_env(),
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode("utf-8", errors="replace")
            error_output = stderr.decode("utf-8", errors="replace")
            
            # Parsear resultado
            success = process.returncode == 0
            
            # Extraer diffs del output
            diffs = self._extract_diffs(output)
            
            # Extraer archivos modificados
            files_changed = self._extract_files_changed(output)
            
            if success:
                logger.info(f"[AiderBridge] Éxito: {len(files_changed)} archivos modificados")
                return AiderResult(
                    success=True,
                    message="Comando ejecutado correctamente",
                    output=output,
                    diffs=diffs,
                    files_changed=files_changed,
                    error=None
                )
            else:
                logger.error(f"[AiderBridge] Error: {error_output}")
                return AiderResult(
                    success=False,
                    message="Error en Aider",
                    output=output,
                    diffs=diffs,
                    files_changed=files_changed,
                    error=error_output
                )
                
        except FileNotFoundError:
            error_msg = "Aider no encontrado. Instala con: python -m pip install aider-install && aider-install"
            logger.error(f"[AiderBridge] {error_msg}")
            return AiderResult(
                success=False,
                message=error_msg,
                output="",
                error=error_msg
            )
        except Exception as e:
            logger.error(f"[AiderBridge] Excepción: {e}")
            return AiderResult(
                success=False,
                message=f"Error inesperado: {str(e)}",
                output="",
                error=str(e)
            )
    
    def _extract_diffs(self, output: str) -> str:
        """Extrae los diffs del output de Aider."""
        diffs = []
        in_diff = False
        current_diff = []
        
        for line in output.split("\n"):
            if line.startswith("diff --git"):
                if current_diff:
                    diffs.append("\n".join(current_diff))
                current_diff = [line]
                in_diff = True
            elif in_diff:
                if line.startswith("diff --git"):
                    diffs.append("\n".join(current_diff))
                    current_diff = [line]
                else:
                    current_diff.append(line)
        
        if current_diff:
            diffs.append("\n".join(current_diff))
        
        return "\n\n".join(diffs)
    
    def _extract_files_changed(self, output: str) -> List[str]:
        """Extrae la lista de archivos modificados del output."""
        # Buscar patrones de archivos modificados
        patterns = [
            r"Applied edit to (.+)",
            r"Created (.+)",
            r"Modified (.+)",
            r"diff --git a/(.+) b/(.+)",
        ]
        
        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, output)
            for match in matches:
                if isinstance(match, tuple):
                    files.update(match)
                else:
                    files.add(match)
        
        return list(files)
    
    async def chat(self, message: str) -> AiderResult:
        """
        Ejecuta un comando de chat con Aider (sin edición).
        
        Args:
            message: Mensaje para el chat.
        
        Returns:
            AiderResult con la respuesta.
        """
        # Usar --chat-only si está disponible, o simplemente enviar el mensaje
        return await self.execute(message)
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del repositorio."""
        return {
            "repo_path": str(self.repo_path),
            "model": self.model,
            "api_configured": bool(self.api_key),
            "base_url": self.base_url,
            "auto_commits": self.auto_commits,
            "read_only": self.read_only,
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_aider_bridge(
    repo_path: str,
    model: str = "",
    api_key: Optional[str] = None,
    auto_commits: bool = True,
    read_only: bool = False,
) -> AiderBridge:
    """
    Factory function para crear un AiderBridge.
    
    Args:
        repo_path: Ruta al repositorio.
        model: Modelo a usar.
        api_key: API key de OpenGPU.
        auto_commits: Si hace commits automáticos.
        read_only: Si es solo lectura.
    
    Returns:
        Instancia de AiderBridge configurada.
    """
    return AiderBridge(
        repo_path=repo_path,
        model=model,
        api_key=api_key,
        auto_commits=auto_commits,
        read_only=read_only,
    )
