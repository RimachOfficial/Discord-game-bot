"""Pytest configuration: add code/ to sys.path for imports."""
import sys
from pathlib import Path

# Add the code directory to sys.path so that imports like
# 'from engines.fishing_engine import ...' work correctly
code_dir = Path(__file__).resolve().parent.parent
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))