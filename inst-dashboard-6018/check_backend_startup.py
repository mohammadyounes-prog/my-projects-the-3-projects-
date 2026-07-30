import sys
import os
from pathlib import Path

# Add the project root to the Python path so backend.main can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import backend.main
    print("Successfully imported backend.main")
except Exception as e:
    print(f"Error importing backend.main: {e}", file=sys.stderr)