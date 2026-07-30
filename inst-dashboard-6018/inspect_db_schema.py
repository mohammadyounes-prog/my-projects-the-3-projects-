import sqlite3
import os
from pathlib import Path

DB_FILE = "questions.db"
DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / DB_FILE))

def get_table_schema(db_path, table_name):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        print(f"\n--- Schema for table: {table_name} ---")
        for col in schema:
            print(col)
    except sqlite3.Error as e:
        print(f"Error accessing table {table_name}: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    get_table_schema(DB_PATH, "users")