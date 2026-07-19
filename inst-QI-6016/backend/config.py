import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(dotenv_path=Path(__file__).with_name('.env'), override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_API_KEY = os.getenv("CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8300"))

