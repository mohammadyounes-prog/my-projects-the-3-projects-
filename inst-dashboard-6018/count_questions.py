import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def count_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    num_questions = count_questions()
    print(f"Number of questions in the database: {num_questions}")
