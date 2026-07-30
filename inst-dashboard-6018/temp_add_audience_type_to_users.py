import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

sql_statement = "ALTER TABLE users ADD COLUMN audience_type TEXT;"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql_statement)
    conn.commit()
    print(f"Successfully added audience_type column to users table in {db_path}")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
