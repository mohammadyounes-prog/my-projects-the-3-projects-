import sqlite3
import os
from passlib.context import CryptContext

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def get_password_hash(password):
    return pwd_context.hash(password)

def reset_user_password(username: str, new_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = get_password_hash(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
    conn.commit()
    conn.close()
    print(f"Password for user {username} has been reset.")

if __name__ == "__main__":
    # Reset password for 'test' user to 'testpassword'
    reset_user_password("test", "testpassword")
