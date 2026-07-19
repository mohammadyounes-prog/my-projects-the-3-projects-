import sqlite3
import os

db_file = 'questions.db'
update_script = 'add_audience_config_table.sql'

def execute_sql_script(cursor, script_path):
    with open(script_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    print(f"Executed {script_path} successfully.")

def update_database():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        execute_sql_script(cursor, update_script)
        conn.commit()
        print(f"Database {db_file} updated successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError as e:
        print(f"Error: SQL script not found - {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    update_database()