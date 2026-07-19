import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM generation_models;")
    count_models = cursor.fetchone()[0]

    print(f"Number of rows in 'generation_models': {count_models}")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
