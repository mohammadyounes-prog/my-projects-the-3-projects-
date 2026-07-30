import sqlite3

db_path = 'D:\\QuestionRetrieval\\new-q-bank\\questions.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users);")
    table_info = cursor.fetchall()

    for column in table_info:
        print(column)

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    if conn:
        conn.close()
