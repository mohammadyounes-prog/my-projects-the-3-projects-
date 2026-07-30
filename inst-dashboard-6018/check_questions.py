
import sqlite3

DB_FILE = "questions.db"

def check_questions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    print(f"Found {count} questions in the database.")
    conn.close()

if __name__ == "__main__":
    check_questions()
