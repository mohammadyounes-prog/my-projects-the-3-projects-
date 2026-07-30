import sqlite3
import os

db_file = 'questions.db'

def check_audience_config():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audience_field_config")
        rows = cursor.fetchall()
        if not rows:
            print("The 'audience_field_config' table is empty.")
        else:
            print("Contents of 'audience_field_config' table:")
            for row in rows:
                print(dict(row))
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    check_audience_config()