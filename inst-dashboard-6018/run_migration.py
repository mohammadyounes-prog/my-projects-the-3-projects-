import sqlite3
import os
import glob

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def execute_sql_script(script_path):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        with open(script_path, 'r') as f:
            sql_script = f.read()
        # Use executescript for files that might have multiple statements
        cursor.executescript(sql_script)
        conn.commit()
        print(f"Executed {script_path} successfully.")
    except sqlite3.Error as e:
        print(f"Database error while executing {script_path}: {e}")
    except FileNotFoundError as e:
        print(f"Error: SQL script not found - {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    script_to_run = 'rename_tenant_to_agent.sql'
    print(f"Executing single script: {script_to_run}")
    execute_sql_script(script_to_run)