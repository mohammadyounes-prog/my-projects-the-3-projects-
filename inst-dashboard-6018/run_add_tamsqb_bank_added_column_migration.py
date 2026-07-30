import sqlite3
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), 'questions.db')
    sql_file = os.path.join(os.path.dirname(__file__), 'add_tamsqb_bank_added_column.sql')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        with open(sql_file, 'r') as f:
            sql_script = f.read()
            cursor.executescript(sql_script)
        conn.commit()
        print("Migration completed successfully: Added tamsqb_bank_added column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("tamsqb_bank_added column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
