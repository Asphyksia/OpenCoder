#!/usr/bin/env python3
"""
Aider wrapper that patches litellm before running aider.

This script is used by AiderBridge to ensure litellm is patched
before Aider tries to use it.
"""
import sys
import os

# Add some debug output
print(f"[Aider Wrapper] Starting with args: {sys.argv}", file=sys.stderr)
print(f"[Aider Wrapper] Current directory: {os.getcwd()}", file=sys.stderr)
print(f"[Aider Wrapper] Script location: {__file__}", file=sys.stderr)

# Patch litellm BEFORE importing aider
# This must be done before any litellm imports
patch_loaded = False

# Method 1: Try to import and patch from the package
try:
    print("[Aider Wrapper] Trying package import...", file=sys.stderr)
    from opencoder.core.litellm_patch import patch_litellm_for_opengpu
    patch_litellm_for_opengpu()
    patch_loaded = True
    print("[Aider Wrapper] Patch loaded from package!", file=sys.stderr)
except ImportError as e:
    print(f"[Aider Wrapper] Package import failed: {e}", file=sys.stderr)
except Exception as e:
    print(f"[Aider Wrapper] Package patch failed: {e}", file=sys.stderr)

# Method 2: If not found as package, try to find and load the module directly
if not patch_loaded:
    print("[Aider Wrapper] Trying direct file load...", file=sys.stderr)
    try:
        import importlib.util
        import pathlib
        
        # Look for litellm_patch.py in common locations (dynamic paths)
        project_root = pathlib.Path(__file__).parent.parent
        possible_paths = [
            project_root / "opencoder" / "core" / "litellm_patch.py",
            pathlib.Path(os.getcwd()) / "opencoder" / "core" / "litellm_patch.py",
        ]
        
        print(f"[Aider Wrapper] Checking paths: {possible_paths}", file=sys.stderr)
        
        for path in possible_paths:
            if path.exists():
                print(f"[Aider Wrapper] Found: {path}", file=sys.stderr)
                spec = importlib.util.spec_from_file_location("litellm_patch", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'patch_litellm_for_opengpu'):
                    module.patch_litellm_for_opengpu()
                    patch_loaded = True
                    print("[Aider Wrapper] Patch loaded from file!", file=sys.stderr)
                    break
            else:
                print(f"[Aider Wrapper] Not found: {path}", file=sys.stderr)
    except Exception as e:
        print(f"[Aider Wrapper] Direct file load failed: {e}", file=sys.stderr)

if not patch_loaded:
    print("[Aider Wrapper] WARNING: Patch not loaded! Aider may fail.", file=sys.stderr)

# Now run aider with the remaining arguments
if __name__ == "__main__":
    print("[Aider Wrapper] Starting aider main...", file=sys.stderr)
    from aider.main import main
    sys.exit(main())
