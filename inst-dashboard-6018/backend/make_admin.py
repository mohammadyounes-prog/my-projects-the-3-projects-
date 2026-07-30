import sqlite3
import os
import sys
import datetime

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def make_user_admin(username: str):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id_row = cursor.fetchone()
        
        if user_id_row:
            user_id = user_id_row["id"]
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"User '{username}' (ID: {user_id}) is now an admin.")
            else:
                print(f"Failed to update user '{username}'.")
        else:
            print(f"User '{username}' not found in the database.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def create_users_table():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        print("Users table ensured to exist.")
    except sqlite3.Error as e:
        print(f"Error creating users table: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Make User Admin Script ---")
    print(f"Attempting to connect to database: {DATABASE_FILE}")
    
    create_users_table()

    try:
        test_conn = get_db_connection()
        test_conn.close()
        print("Database connection successful.")
    except sqlite3.Error as e:
        print(f"ERROR: Could not connect to database at {DATABASE_FILE}. Please ensure the path is correct and the file exists.")
        print(f"Details: {e}")
        sys.exit(1)

    admin_username = input("Enter the username to make admin: ")
    make_user_admin(admin_username)
    print("----------------------------")
