import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in questions.db:")
    for table in tables:
        print(table[0])
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
