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

def create_user(username: str, hashed_password: str, is_admin: int = 0, full_name: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin, full_name) VALUES (?, ?, ?, ?)", (username, hashed_password, is_admin, full_name))
        conn.commit()
        print(f"User {username} created successfully.")
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    # Create an admin user named 'test' with password 'testpassword'
    create_user("test", get_password_hash("testpassword"), is_admin=1, full_name="Test Admin")
