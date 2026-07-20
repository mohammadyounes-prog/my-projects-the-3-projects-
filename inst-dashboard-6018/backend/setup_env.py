import os
from pathlib import Path

# Define base directory for backend
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_FILE_PATH = PROJECT_ROOT / '.env'

# Function to create a .env file with placeholder configurations
def create_env_file():
    env_content = f"""
# --- General Settings ---
APP_ENV=development
LOG_LEVEL=INFO

# --- Backend Settings ---
BACKEND_PORT=8000
# Use SQLite for dashboard's own data if needed, or omit if not using
# DASHBOARD_DB_PATH="{PROJECT_ROOT}/data/dashboard.db"

# --- Database Connections ---
# QuestAI (new-q-bank) SQLite Database
# Assumes questions.db is in the new-q-bank root directory, one level up from backend/
QUESTAI_DB_PATH="{PROJECT_ROOT.parent}/questions.db"

# Online Exam MySQL Database Connection
# REPLACE WITH ACTUAL VALUES
ONLINE_EXAM_DB_HOST=localhost
ONLINE_EXAM_DB_PORT=3306
ONLINE_EXAM_DB_NAME=schooldemo12
ONLINE_EXAM_DB_USER=root
ONLINE_EXAM_DB_PASS=your_mysql_password

# --- JWT & Security ---
SECRET_KEY=your_super_secret_key_for_jwt_signing # CHANGE THIS IN PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- External Service URLs ---
# Base URLs for the QuestAI and Online Exam APIs
# If they are running on different IPs/ports, update these accordingly.
QUESTAI_API_BASE_URL=http://localhost:8000 # Assuming QuestAI backend is also served
ONLINE_EXAM_API_BASE_URL=http://localhost/tams/app/schooldemo12/apps/online-exam # Adjust if running elsewhere

# --- Multilingual Settings ---
# Supported languages and their RTL status
SUPPORTED_LANGUAGES=en,ar
DEFAULT_LANGUAGE=en
"""
    try:
        with open(ENV_FILE_PATH, 'w') as f:
            f.write(env_content.strip())
        print(f"Created '{ENV_FILE_PATH}' with placeholder configurations.")
    except Exception as e:
        print(f"Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file()
