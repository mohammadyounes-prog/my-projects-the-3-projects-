import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'questions.db')

def inspect_users_table():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()

        print("Columns in 'users' table:")
        for col in columns:
            print(f"- Name: {col[1]}, Type: {col[2]}, Not Null: {bool(col[3])}, Primary Key: {bool(col[5])}")

    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_users_table()
