import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv # Import load_dotenv

# wrap the run call:
if __name__ == "__main__":
    # Change working directory to the backend folder
    ROOT = Path(__file__).resolve().parent / "backend"
    os.chdir(ROOT)
    
    # Add backend to sys.path so modules can be imported
    import sys
    sys.path.insert(0, str(ROOT))

    load_dotenv(ROOT / ".env") # Load environment variables from .env in backend
    # 1. Check for explicit PORT variable
    # 2. Extract port from BACKEND_BASE_URL if it exists
    # 3. Default to 8000
    port_env = os.getenv("PORT")
    backend_url = os.getenv("BACKEND_BASE_URL", "http://0.0.0.0:8000")
    print(f"DEBUG: Loaded BACKEND_BASE_URL from env: {backend_url}")
    
    port = 8000
    if port_env and port_env.isdigit():
        port = int(port_env)
        print(f"DEBUG: Using explicit PORT from env: {port}")
    else:
        try:
            # Simple extraction logic for "http://host:port"
            if ":" in backend_url.replace("://", ""):
                port_str = backend_url.split(":")[-1].strip("/")
                if port_str.isdigit():
                    port = int(port_str)
        except Exception as e:
            print(f"DEBUG: Error parsing port from BACKEND_BASE_URL: {e}")

    print(f"DEBUG: Final port selection: {port}")
    print(f"DEBUG: Attempting to start Uvicorn server on port {port}...")

    # Add backend to sys.path so modules can be imported
    import sys
    sys.path.insert(0, str(ROOT))
    
    # Run FastAPI app; Python automatically includes CWD in sys.path
    uvicorn.run('main:app', host='0.0.0.0', port=port, reload=True, log_level="debug")
