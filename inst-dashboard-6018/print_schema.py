import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def print_table_schema(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema = cursor.fetchall()
    conn.close()
    print(f"Schema for table {table_name}:")
    for col in schema:
        print(dict(col))

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        print_table_schema(table_name)
    else:
        print("Usage: python print_schema.py <table_name>")
        print_table_schema("questions") # Default to questions if no argument provided
