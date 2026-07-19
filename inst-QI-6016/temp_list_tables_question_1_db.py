import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\question-1.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print(f"Tables in {db_path}:")
        for table_name in tables:
            print(f"- {table_name[0]}")
    else:
        print(f"No tables found in {db_path}.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
