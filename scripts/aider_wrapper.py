#!/usr/bin/env python3
"""Wrapper script to run Aider with Python 3.12 site-packages."""
import sys
import os

# Add Python 3.12 site-packages to path
_python12_site_packages = '/home/asphyksia/OpenCoder/venv/lib/python3.12/site-packages'
if _python12_site_packages not in sys.path:
    sys.path.insert(0, _python12_site_packages)

# Now run aider with the remaining arguments
from aider import main
if __name__ == '__main__':
    sys.exit(main())
