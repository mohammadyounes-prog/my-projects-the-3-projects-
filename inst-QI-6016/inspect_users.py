import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

def inspect_users():
    """Connects to the database and prints the contents of the users table."""
    try:
        print(f"Connecting to database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("Fetching all rows from the users table...")
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        if not rows:
            print("The 'users' table is empty.")
            return

        print("\n--- Contents of 'users' table ---")
        for row in rows:
            print(dict(row))
        print("----------------------------------\n")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    inspect_users()

