#!/usr/bin/env python3
"""Wrapper script to run Aider with Python 3.12 site-packages.

This script detects Python 3.12 site-packages across different platforms
(Linux, macOS, Windows) to ensure Aider works in any environment.
"""
import sys
import os
from pathlib import Path


def find_python312_site_packages():
    """Find Python 3.12 site-packages in various common locations.
    
    Returns:
        Path to Python 3.12 site-packages if found, None otherwise.
    """
    home = Path.home()
    system = sys.platform
    
    # Common paths for Python 3.12 site-packages
    potential_paths = []
    
    if system == "linux":
        potential_paths = [
            home / ".local" / "lib" / "python3.12" / "site-packages",
            Path("/usr/local/lib/python3.12/site-packages"),
            Path("/usr/lib/python3.12/site-packages"),
            # Try to find venv in common locations
            Path.cwd() / "venv" / "lib" / "python3.12" / "site-packages",
            Path.cwd() / ".venv" / "lib" / "python3.12" / "site-packages",
        ]
    elif system == "darwin":  # macOS
        potential_paths = [
            home / ".local" / "lib" / "python3.12" / "site-packages",
            Path("/opt/homebrew/lib/python3.12/site-packages"),
            Path("/usr/local/lib/python3.12/site-packages"),
            Path.cwd() / "venv" / "lib" / "python3.12" / "site-packages",
            Path.cwd() / ".venv" / "lib" / "python3.12" / "site-packages",
        ]
    elif system == "win32":  # Windows
        potential_paths = [
            home / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "Lib" / "site-packages",
            Path.cwd() / "venv" / "Lib" / "site-packages",
            Path.cwd() / ".venv" / "Lib" / "site-packages",
        ]
    
    # Try to detect from current Python executable
    current_python = Path(sys.executable)
    if current_python.parent.parent.exists():
        site_packages = current_python.parent.parent / "lib" / "python3.12" / "site-packages"
        if site_packages.exists():
            return str(site_packages)
        # Try Windows path
        site_packages = current_python.parent.parent / "Lib" / "site-packages"
        if site_packages.exists():
            return str(site_packages)
    
    # Check all potential paths
    for path in potential_paths:
        if path.exists():
            return str(path)
    
    return None


# Find and add Python 3.12 site-packages
_python12_site_packages = find_python312_site_packages()

if _python12_site_packages and _python12_site_packages not in sys.path:
    sys.path.insert(0, _python12_site_packages)
    print(f"[Aider Wrapper] Using site-packages: {_python12_site_packages}", file=sys.stderr)
else:
    print("[Aider Wrapper] Warning: Could not find Python 3.12 site-packages", file=sys.stderr)

# Now run aider with the remaining arguments
from aider import main
if __name__ == '__main__':
    sys.exit(main())
