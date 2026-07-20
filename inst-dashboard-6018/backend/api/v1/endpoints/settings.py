from ....core.config import get_settings, Settings
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict
from ....database.session import get_online_exam_db_connection, get_questai_db # Import for accessing Online Exam MySQL database
import sqlite3

router = APIRouter()

@router.get("/weights", summary="Get KPI weights for Dashboard")
async def get_kpi_weights(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    """
    Fetches the weights used for calculating the Overall Performance Index.
    """
    try:
        cursor = sqlite_db.cursor()
        cursor.execute("SELECT key, value FROM dashboard_weights")
        rows = cursor.fetchall()
        return {row['key']: row['value'] for row in rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weights", summary="Update KPI weights for Dashboard")
async def update_kpi_weights(
    new_weights: Dict[str, float], 
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    """
    Updates the weights used for calculating the Overall Performance Index.
    """
    try:
        cursor = sqlite_db.cursor()
        for key, value in new_weights.items():
            cursor.execute(
                "INSERT OR REPLACE INTO dashboard_weights (key, value) VALUES (?, ?)", 
                (key, value)
            )
        sqlite_db.commit()
        return {"status": "success", "message": "Weights updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current", summary="Get current dashboard settings")
async def get_current_settings(settings: Settings = Depends(get_settings)):
    """
    Retrieves the current dashboard configuration settings.
    This endpoint is intended to show the loaded settings, excluding sensitive ones like passwords.
    """
    # Return settings, but exclude sensitive information like passwords
    return {
        "APP_ENV": settings.APP_ENV,
        "LOG_LEVEL": settings.LOG_LEVEL,
        "BACKEND_PORT": settings.BACKEND_PORT,
        "QUESTAI_DB_PATH": settings.QUESTAI_DB_PATH, # Path is generally safe to expose
        "ONLINE_EXAM_DB_HOST": settings.ONLINE_EXAM_DB_HOST,
        "ONLINE_EXAM_DB_PORT": settings.ONLINE_EXAM_DB_PORT,
        "ONLINE_EXAM_DB_NAME": settings.ONLINE_EXAM_DB_NAME,
        "ONLINE_EXAM_DB_USER": settings.ONLINE_EXAM_DB_USER,
        # Do not return ONLINE_EXAM_DB_PASS
        "SECRET_KEY": "*******", # Mask sensitive keys
        "ALGORITHM": settings.ALGORITHM,
        "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "QUESTAI_API_BASE_URL": settings.QUESTAI_API_BASE_URL,
        "ONLINE_EXAM_API_BASE_URL": settings.ONLINE_EXAM_API_BASE_URL,
        "SUPPORTED_LANGUAGES": settings.SUPPORTED_LANGUAGES,
        "DEFAULT_LANGUAGE": settings.DEFAULT_LANGUAGE,
    }

@router.post("/update", summary="Update dashboard settings")
async def update_dashboard_settings(
    new_settings: Dict[str, Any],
    settings: Settings = Depends(get_settings)
):
    """
    Updates dashboard configuration settings.
    This is a placeholder. In a real application, this would involve:
    1. Validating the input `new_settings`.
    2. Persisting these changes (e.g., to a database or by updating a config file).
    3. Reloading settings if necessary.
    For now, it simulates an update and returns the modified (but not sensitive) settings.
    """
    # In a real scenario, you would update a persistent store here.
    # For demonstration, we'll simulate updating and return the *new* values.
    # !!! WARNING: This does NOT persist changes to .env or environment variables !!!
    # !!! This is a placeholder for logic that would modify a persistent config store !!!

    # Example: Updating a non-sensitive setting
    if 'ONLINE_EXAM_DB_HOST' in new_settings:
        # In a real app, you'd update your configuration source.
        # For this example, we'll just use the new value for demonstration purposes.
        # This change is NOT persistent beyond the current request/process.
        settings.ONLINE_EXAM_DB_HOST = new_settings['ONLINE_EXAM_DB_HOST']
        print(f"Simulating update: ONLINE_EXAM_DB_HOST set to {settings.ONLINE_EXAM_DB_HOST}")

    # You would implement logic here to update db credentials, API URLs, etc.
    # For security, passwords and secret keys should be handled with extreme care.

    # Return the updated settings (excluding sensitive ones)
    return {
        "message": "Settings updated (simulated).",
        "updated_settings": {
            "APP_ENV": settings.APP_ENV,
            "LOG_LEVEL": settings.LOG_LEVEL,
            "BACKEND_PORT": settings.BACKEND_PORT,
            "QUESTAI_DB_PATH": settings.QUESTAI_DB_PATH,
            "ONLINE_EXAM_DB_HOST": settings.ONLINE_EXAM_DB_HOST, # Reflecting the simulated update
            "ONLINE_EXAM_DB_PORT": settings.ONLINE_EXAM_DB_PORT,
            "ONLINE_EXAM_DB_NAME": settings.ONLINE_EXAM_DB_NAME,
            "ONLINE_EXAM_DB_USER": settings.ONLINE_EXAM_DB_USER,
            # Mask sensitive keys
            "SECRET_KEY": "*******",
            "ALGORITHM": settings.ALGORITHM,
            "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "QUESTAI_API_BASE_URL": settings.QUESTAI_API_BASE_URL,
            "ONLINE_EXAM_API_BASE_URL": settings.ONLINE_EXAM_API_BASE_URL,
            "SUPPORTED_LANGUAGES": settings.SUPPORTED_LANGUAGES,
            "DEFAULT_LANGUAGE": settings.DEFAULT_LANGUAGE,
        }
    }

# Example of how to access the Online Exam DB connection from a settings endpoint
# This is just illustrative and not part of the actual settings update logic.
@router.get("/test-online-exam-db-connection", summary="Test Online Exam DB Connection")
async def test_online_exam_db_connection():
    """
    Tests the connection to the Online Exam MySQL database.
    """
    try:
        conn = get_online_exam_db_connection()
        # Perform a simple query to verify connection
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                return {"message": "Successfully connected to Online Exam MySQL database."}
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Online Exam DB query failed.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not connect to Online Exam MySQL database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

