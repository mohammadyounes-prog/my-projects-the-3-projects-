import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"
sql_statement = "ALTER TABLE questions ADD COLUMN status TEXT DEFAULT 'pending';"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql_statement)
    conn.commit()
    print(f"Successfully added status column to questions table in {db_path}")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
