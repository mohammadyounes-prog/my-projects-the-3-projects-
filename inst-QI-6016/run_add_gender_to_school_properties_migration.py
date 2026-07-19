import sqlite3
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), 'questions.db')
    sql_file = os.path.join(os.path.dirname(__file__), 'add_gender_to_school_properties.sql')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(sql_file, 'r') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()
