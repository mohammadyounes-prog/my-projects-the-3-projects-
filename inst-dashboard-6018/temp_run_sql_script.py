import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"
sql_script_path = "D:\\QuestionRetrieval\\new-q-bank\\create_question_db.sql"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(sql_script_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    print(f"Successfully executed {sql_script_path} on {db_path}")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
