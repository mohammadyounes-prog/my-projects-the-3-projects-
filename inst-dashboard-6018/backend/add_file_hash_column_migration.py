import sqlite3
import os
import logging

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '../', 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def add_file_hash_column_to_uploaded_files_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE uploaded_files ADD COLUMN file_hash TEXT")
        conn.commit()
        logging.info("Added file_hash column to uploaded_files table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("file_hash column already exists in uploaded_files table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    add_file_hash_column_to_uploaded_files_table()
