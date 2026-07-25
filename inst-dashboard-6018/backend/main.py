from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .api.api import router as api_router
from .core.config import settings # Import settings directly
from .core.security import verify_password, verify_legacy_password, get_password_hash, create_access_token # Import security utilities
from .database.session import get_questai_db, get_online_exam_db_connection # Import DB connections
import sqlite3

# --- Load Settings ---
# Settings are already loaded globally in core/config.py for direct access.
# If you prefer dependency injection for settings, use:
# from fastapi import Depends
# from .core.config import get_settings
# settings = Depends(get_settings)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Executive Dashboard API",
    description="API for aggregating data from QuestAI and Online Exam projects.",
    version="1.0.0",
    # OpenAPI URL can be dynamically set based on settings if needed
)

# --- CORS Middleware ---
# Configure CORS to allow requests from your frontend application
# Ensure the frontend URL (e.g., http://localhost:3000) is added here.
origins = [
    "http://localhost:3000",  # Default React development server
    "http://localhost:6015",  # Website / suite hub (inst-website-6015) — SSO entry origin
    "http://localhost:6019",  # Dashboard CRA (inst-dashboard-6018 frontend)
    # Legacy alias if an older stack still serves the website here:
    "http://localhost:3700",
    # Add other allowed origins, e.g., deployed frontend URL
    settings.ONLINE_EXAM_API_BASE_URL, # Potentially if frontend is served from here
]

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(api_router, prefix="/api/v1")

# --- Health Check Endpoint ---
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Dashboard API is running."}

# --- Root Redirect (Optional) ---
# Redirect root URL to API docs
from fastapi.responses import RedirectResponse
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

# --- Example of using security utilities (can be moved to auth endpoint) ---
@app.post("/token", summary="Token endpoint for authentication")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    # Enforce 72-byte truncation for all password inputs
    password = form_data.password[:72]
    
    # 1. Check QuestAI (SQLite) - Uses Bcrypt
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT username, password, role, full_name, tenant_id, is_admin, is_super_admin FROM users WHERE username = ?", (form_data.username,))
        user = sqlite_cursor.fetchone()
    except Exception as e:
        print(f"DEBUG: SQLite error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    
    if user:
        if verify_password(password, user['password']):
            # Use form_data.username as the sub
            token = create_access_token(data={"sub": form_data.username, "role": user['role']})
            return {
                "access_token": token, 
                "token_type": "bearer", 
                "role": user['role'], 
                "name": user['full_name'],
                "is_admin": user['is_admin'],
                "is_super_admin": user['is_super_admin'],
                "tenant_id": user['tenant_id']
            }

    # 2. Check TAMS (MySQL) - Uses SHA256
    try:
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as cursor:
                # Use form_data.username for both email or username lookup
                cursor.execute("SELECT id, email, pass, name FROM employee WHERE email = %s OR name = %s", (form_data.username, form_data.username))
                employee = cursor.fetchone()

                if employee:
                    if verify_legacy_password(password, employee['pass']):
                        # Use the email (stored in TAMS) as the sub for SSO consistency
                        token = create_access_token(data={"sub": employee['email'], "role": "instructor"})
                        return {
                            "access_token": token, 
                            "token_type": "bearer", 
                            "role": "instructor", 
                            "name": employee['name'],
                            "is_admin": 1,
                            "is_super_admin": 0,
                            "tenant_id": 1 # Default or lookup
                        }
        finally:
            mysql_conn.close()
    except Exception as e:
        print(f"DEBUG: MySQL error: {e}")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# --- Example of accessing settings directly in an endpoint ---
@app.get("/status", summary="API Status with Settings Info")
async def api_status():
    return {
        "api_status": "operational",
        "backend_port": settings.BACKEND_PORT,
        "app_env": settings.APP_ENV,
        "questai_db_path": settings.QUESTAI_DB_PATH,
        "online_exam_db_host": settings.ONLINE_EXAM_DB_HOST,
        "default_language": settings.DEFAULT_LANGUAGE,
    }

# --- Main execution block for running with uvicorn ---
if __name__ == "__main__":
    # This block is typically for direct execution, but uvicorn is preferred for production.
    # To run: uvicorn backend.main:app --reload --port 8000
    print(f"Starting FastAPI server on port {settings.BACKEND_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=settings.BACKEND_PORT)
