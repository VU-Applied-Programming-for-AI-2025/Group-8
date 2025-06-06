# Copied this code from Marton's demo in Canvas to let the tests.py file import the app module correctly.

import sys
from pathlib import Path

# Add the root directory to the Python path
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

try:
    from app import app

except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    raise