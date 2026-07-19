import sqlite3
import os

DATABASE_FILE = "questions.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def get_table_schema(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        if schema:
            print(f"Schema for table {table_name}:")
            for col in schema:
                print(dict(col))
        else:
            print(f"Table {table_name} not found or has no schema.")
    except sqlite3.Error as e:
        print(f"Error getting schema for {table_name}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        get_table_schema(table_name)
    else:
        print("Please provide a table name as an argument.")