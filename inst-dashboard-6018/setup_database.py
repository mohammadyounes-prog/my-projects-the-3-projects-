import sqlite3
import os

db_file = 'questions.db'
create_script = 'create_question_db.sql'
populate_script = 'populate_lookup_tables.sql'

def execute_sql_script(cursor, script_path):
    with open(script_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    print(f"Executed {script_path} successfully.")

def setup_database():
    conn = None
    try:
        # Connect to SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Execute the create table script
        execute_sql_script(cursor, create_script)

        # Execute the populate lookup tables script
        execute_sql_script(cursor, populate_script)

        conn.commit()
        print(f"Database {db_file} setup complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError as e:
        print(f"Error: SQL script not found - {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ensure the script is run from the project root or adjust paths
    # For this context, assuming it's run from D:\QuestionRetrieval\
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    setup_database()
