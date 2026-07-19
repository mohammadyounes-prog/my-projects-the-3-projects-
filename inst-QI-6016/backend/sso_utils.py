from fastapi import HTTPException
from online_exam_db_connector import get_online_exam_db_connection

def verify_sso_token(sso_token: str):
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        print(f"[DEBUG] verify_sso_token: Searching for token: {sso_token}")
        # Verify token in the MySQL sso_sessions table
        cursor.execute("SELECT user_id, expires_at FROM sso_sessions WHERE token = %s", (sso_token,))
        row = cursor.fetchone()
        
        if not row:
            print(f"[DEBUG] verify_sso_token: Token {sso_token} not found in DB!")
            raise HTTPException(status_code=401, detail="Invalid or expired SSO token")
        
        # Check expiration
        from datetime import datetime
        expires_at = row["expires_at"]
        print(f"[DEBUG] verify_sso_token: Found token, expires_at: {expires_at}, NOW: {datetime.now()}")
        
        if expires_at < datetime.now():
            print(f"[DEBUG] verify_sso_token: Token {sso_token} is expired!")
            raise HTTPException(status_code=401, detail="Invalid or expired SSO token")
        
        user_id = row["user_id"]
        
        # Cleanup token after use
        cursor.execute("DELETE FROM sso_sessions WHERE token = %s", (sso_token,))
        conn.commit()
        cursor.close()
        
        return user_id
    except HTTPException:
        # Re-raise HTTPException directly
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during SSO verification: {e}")
    finally:
        if conn:
            conn.close()

def generate_sso_token(user_id: int):
    import uuid
    from datetime import datetime, timedelta
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        
        # Generate a unique token
        sso_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Insert into sso_sessions table
        # Based on user description, table is sso_sessions in schooldemo12 db
        cursor.execute(
            "INSERT INTO sso_sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
            (sso_token, user_id, expires_at)
        )
        conn.commit()
        cursor.close()
        return sso_token
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during SSO token generation: {e}")
    finally:
        if conn:
            conn.close()
