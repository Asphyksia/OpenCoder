#!/usr/bin/env python3
"""
Aider wrapper that patches litellm before running aider.

This script is used by AiderBridge to ensure litellm is patched
before Aider tries to use it.
"""
import sys
import os

# Patch litellm BEFORE importing aider
# This must be done before any litellm imports
try:
    # Try to import and patch from the package
    from opencoder.core.litellm_patch import patch_litellm_for_opengpu
    patch_litellm_for_opengpu()
except ImportError:
    # If not found as package, try to find and load the module directly
    import importlib.util
    import pathlib
    
    # Look for litellm_patch.py in common locations
    possible_paths = [
        pathlib.Path(__file__).parent / "opencoder" / "core" / "litellm_patch.py",
        pathlib.Path("/home/asphyksia/OpenCoder/opencoder/core/litellm_patch.py"),
    ]
    
    for path in possible_paths:
        if path.exists():
            spec = importlib.util.spec_from_file_location("litellm_patch", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'patch_litellm_for_opengpu'):
                module.patch_litellm_for_opengpu()
                break

# Now run aider with the remaining arguments
if __name__ == "__main__":
    # Execute aider with all remaining command line arguments
    from aider.main import main
    sys.exit(main())
