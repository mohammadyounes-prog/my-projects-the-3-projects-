import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def execute_sql_script(script_path):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        with open(script_path, 'r') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        print(f"Executed {script_path} successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError as e:
        print(f"Error: SQL script not found - {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migration_script = 'add_api_key_to_generation_models.sql'
    execute_sql_script(migration_script)
