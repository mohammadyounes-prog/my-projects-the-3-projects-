import sqlite3
import os
import sys

# Define the path to your SQLite database
DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def inspect_tenants_table():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print(f"--- Inspecting 'tenants' table in '{DATABASE_FILE}' ---")
        cursor.execute("SELECT id, name, created_at, parent_id, created_by FROM tenants ORDER BY id ASC")
        rows = cursor.fetchall()

        if not rows:
            print("The 'tenants' table is empty.")
            return

        print("ID | Name            | Created At                 | Parent ID | Created By")
        print("---|-----------------|----------------------------|-----------|-----------")
        for row in rows:
            created_at = row['created_at'] if row['created_at'] else 'N/A'
            parent_id = row['parent_id'] if row['parent_id'] else 'N/A'
            created_by = row['created_by'] if row['created_by'] else 'N/A'
            print(f"{row['id']:<2} | {row['name']:<15} | {created_at:<26} | {parent_id:<9} | {created_by:<10}")

    except sqlite3.OperationalError as e:
        print(f"Database operational error: {e}. Please ensure the backend server is not running and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_tenants_table()
