
import sqlite3
import os

DATABASE_FILE = "questions.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def view_table_data(table_name: str):
    print(f"--- Data for table: {table_name} ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(dict(row))
        else:
            print(f"No data found in table {table_name}.")
    except sqlite3.Error as e:
        print(f"Error reading data from {table_name}: {e}")
    finally:
        conn.close()
    print("-" * (len(table_name) + 20))
    print()

if __name__ == "__main__":
    tables_to_view = [
        "difficulty_levels",
        "cognitive_levels",
        "learning_outcomes",
        "question_types"
    ]
    for table in tables_to_view:
        view_table_data(table)
