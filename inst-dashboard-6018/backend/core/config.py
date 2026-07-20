from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path
import os

# Define the path to the .env file
# The .env file is in the 'newboard' directory, which is the parent of 'backend'
BACKEND_DIR = Path(__file__).resolve().parent.parent
NEWBOARD_DIR = BACKEND_DIR.parent
ENV_FILE_PATH = NEWBOARD_DIR / '.env'

# Load environment variables from the .env file
if ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=ENV_FILE_PATH)
else:
    print(f"WARNING: .env file not found at {ENV_FILE_PATH}")

class Settings(BaseSettings):
    APP_ENV: str
    LOG_LEVEL: str

    # Backend Settings
    BACKEND_PORT: int

    # Database Connections
    QUESTAI_DB_PATH: str

    # Online Exam MySQL Database Connection
    ONLINE_EXAM_DB_HOST: str
    ONLINE_EXAM_DB_PORT: int
    ONLINE_EXAM_DB_NAME: str
    ONLINE_EXAM_DB_USER: str
    ONLINE_EXAM_DB_PASS: str

    # JWT & Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # External Service URLs
    QUESTAI_API_BASE_URL: str
    ONLINE_EXAM_API_BASE_URL: str

    # Multilingual Settings
    SUPPORTED_LANGUAGES: str
    DEFAULT_LANGUAGE: str
    
    # Optional API Key
    GOOGLE_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = "828352184347-2bblb1ansh4q7cs8g3fgqj37gr9e9b1o.apps.googleusercontent.com"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding='utf-8', extra='ignore')
    
# Function to get settings instance
def get_settings() -> Settings:
    return Settings()

# --- Optional: Function to access settings directly without dependency injection ---
# This can be useful for global access or during startup.
settings = get_settings()
