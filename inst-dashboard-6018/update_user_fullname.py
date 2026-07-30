import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def update_user_full_name(username: str, full_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET full_name = ? WHERE username = ?", (full_name, username))
    conn.commit()
    conn.close()
    print(f"Updated full_name for user {username} to {full_name}")

if __name__ == "__main__":
    update_user_full_name("test", "Test User")
