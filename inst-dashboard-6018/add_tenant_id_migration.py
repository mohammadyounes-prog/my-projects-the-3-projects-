import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def add_tenant_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN tenant_id INTEGER")
        conn.commit()
        print("Added tenant_id column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("tenant_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

if __name__ == "__main__":
    add_tenant_id_to_questions_table()
