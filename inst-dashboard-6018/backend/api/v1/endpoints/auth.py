from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from ....database.session import get_questai_db, get_online_exam_db_connection
from ....core.security import verify_password, verify_legacy_password, create_access_token, php_encrypt
from ....core.config import settings
from jose import jwt
import sqlite3
import pymysql
import uuid
import hashlib

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

import httpx

@router.post("/google", summary="Login with Google")
async def google_login(
    payload: dict,
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    # Verify token with Google API
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        google_user = resp.json()

    # Check audience (aud) to prevent token substitution attacks
    if google_user.get("aud") != settings.GOOGLE_CLIENT_ID:
         raise HTTPException(status_code=401, detail="Invalid token audience")

    email = google_user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    # 1. Match against TAMS (MySQL)
    try:
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as cursor:
                cursor.execute("SELECT id, email, name FROM employee WHERE email = %s", (email,))
                employee = cursor.fetchone()
                if employee:
                    jwt_token = create_access_token(data={"sub": employee['email'], "role": "instructor"})
                    return {"access_token": jwt_token, "token_type": "bearer", "role": "instructor", "name": employee['name']}
        finally:
            mysql_conn.close()
    except Exception as e:
        print(f"DEBUG: MySQL error in Google login: {e}")

    # 2. Match against QuestAI (SQLite)
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT username, role, full_name FROM users WHERE email = ? OR username = ?", (email, email))
        user = sqlite_cursor.fetchone()
        if user:
            jwt_token = create_access_token(data={"sub": user['username'], "role": user['role']})
            return {"access_token": jwt_token, "token_type": "bearer", "role": user['role'], "name": user['full_name']}
    except Exception as e:
        print(f"DEBUG: SQLite error in Google login: {e}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No account found linked to this Google email. Please register first.",
    )

@router.post("/login", summary="Login to either QuestAI or TAMS system")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    # Enforce 72-byte truncation for all password inputs
    password = form_data.password[:72]
    
    # 1. Check QuestAI (SQLite) - Uses Bcrypt
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT username, password, role, full_name FROM users WHERE username = ?", (form_data.username,))
        user = sqlite_cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")
    
    if user:
        if verify_password(password, user['password']):
            # Use form_data.username as the sub
            token = create_access_token(data={"sub": form_data.username, "role": user['role']})
            return {"access_token": token, "token_type": "bearer", "role": user['role'], "name": user['full_name']}

    # 2. Check TAMS (MySQL) - Uses SHA256
    try:
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as cursor:
                # Use form_data.username for both email or username lookup
                cursor.execute("SELECT id, email, pass, name FROM employee WHERE email = %s OR name = %s", (form_data.username, form_data.username))
                employee = cursor.fetchone()
                
                if employee:
                    is_valid = verify_legacy_password(password, employee['pass'])
                    if not is_valid:
                        # Log more details to diagnose
                        print(f"DEBUG: TAMS auth check for {form_data.username}. Valid: {is_valid}.")
                        print(f"DEBUG: Expected hash: {employee['pass']}")
                        print(f"DEBUG: Calculated hash: {hashlib.sha256(php_encrypt(password).encode()).hexdigest()}")
                        # Note: The 'Input Hash' in previous logs was just sha256(password), 
                        # which is likely why it didn't match.
                    if is_valid:
                        # Use the email (stored in TAMS) as the sub for SSO consistency
                        token = create_access_token(data={"sub": employee['email'], "role": "instructor"})
                        return {"access_token": token, "token_type": "bearer", "role": "instructor", "name": employee['name']}
        finally:
            mysql_conn.close()
    except Exception as e:
        print(f"DEBUG: MySQL error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/generate-sso-token")
async def generate_sso_token(
    identifier: str = Depends(get_current_user_email),
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    print(f"DEBUG: SSO token generation for identifier: {identifier}")
    # Lookup the user_id from the identifier (email or username)
    conn = get_online_exam_db_connection()
    user_id = None
    try:
        with conn.cursor() as cursor:
            # Try lookup in employee table by email OR name
            cursor.execute("SELECT id FROM employee WHERE email = %s OR name = %s", (identifier, identifier))
            result = cursor.fetchone()
            if result:
                user_id = result['id']
            else:
                # Fallback: check QuestAI users
                cursor = sqlite_db.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (identifier,))
                result = cursor.fetchone()
                if result:
                    user_id = result['id']
    except Exception as e:
        print(f"DEBUG: Database error in SSO gen: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    if not user_id:
        print(f"DEBUG: User not found: {identifier}")
        raise HTTPException(status_code=404, detail="User not found")

    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=5)
    
    conn = get_online_exam_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sso_sessions (user_id, token, expires_at) VALUES (%s, %s, %s)",
                (user_id, token, expires_at)
            )
        conn.commit()
    finally:
        conn.close()
        
    return {"sso_token": token}

@router.get("/verify-sso")
async def verify_sso(sso_token: str, sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    conn = get_online_exam_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check sso_sessions table
            cursor.execute("SELECT user_id FROM sso_sessions WHERE token = %s AND expires_at > NOW()", (sso_token,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Token invalid or expired")
                
            user_id = result['user_id']
            
            # Fetch username/name based on user_id
            cursor.execute("SELECT name FROM employee WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return {"username": user['name']}
            
            # Fallback to QuestAI users
            sqlite_cursor = sqlite_db.cursor()
            sqlite_cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = sqlite_cursor.fetchone()
            if user:
                return {"username": user['username']}
                
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()
