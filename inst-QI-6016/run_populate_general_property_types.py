import sqlite3

def run_sql_script(db_path, script_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        with open(script_path, 'r') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        print(f"Successfully executed {script_path} on {db_path}")
    except Exception as e:
        print(f"Error executing {script_path}: {e}")

if __name__ == "__main__":
    run_sql_script('questions.db', 'populate_general_property_types.sql')