import sqlite3
import os

db_file = 'questions.db'
populate_script = 'populate_audience_config.sql'

def execute_sql_script(cursor, script_path):
    with open(script_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    print(f"Executed {script_path} successfully.")

def populate_data():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        execute_sql_script(cursor, populate_script)
        conn.commit()
        print(f"Data populated successfully in {db_file}.")
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
    populate_data()