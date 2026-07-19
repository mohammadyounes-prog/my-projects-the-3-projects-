import sqlite3
import os
from pathlib import Path

# Define the path to the database file
SCRIPT_DIR = Path(__file__).resolve().parent
DATABASE_FILE = SCRIPT_DIR.parent / 'questions.db'

def get_db_connection():
    print(f"DEBUG: Attempting to connect to database at: {DATABASE_FILE}")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to database at {DATABASE_FILE}: {e}")
        return None

def inspect_property_types_table():
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        # Check if 'is_global' column exists before querying it
        cursor.execute("PRAGMA table_info(property_types);")
        columns_info = cursor.fetchall()
        column_names = [col['name'] for col in columns_info]

        if not column_names:
            print("INFO: 'property_types' table does not exist or has no columns.")
            conn.close()
            return

        select_cols = ["id", "name", "api_name", "audience_type"]
        if "is_global" in column_names:
            select_cols.append("is_global")
        else:
            print("WARNING: 'is_global' column not found in 'property_types' table.")
        
        select_statement = ", ".join(select_cols)
        print(f"DEBUG: Executing query: SELECT {select_statement} FROM property_types;")

        cursor.execute(f"SELECT {select_statement} FROM property_types;")
        rows = cursor.fetchall()
        
        if not rows:
            print("INFO: No rows found in 'property_types' table.")
            
        for row in rows:
            row_dict = dict(row)
            output = f"ID: {row_dict['id']}, Name: {row_dict['name']}, API Name: {row_dict['api_name']}, Audience Type: {row_dict['audience_type']}"
            if "is_global" in column_names:
                output += f", Is Global: {bool(row_dict['is_global'])}"
            print(output)
    except sqlite3.OperationalError as e:
        print(f"ERROR: SQLite Operational Error during query: {e}. Check table/column names or database integrity.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during inspection: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_property_types_table()