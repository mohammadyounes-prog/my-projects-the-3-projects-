import sqlite3
import os

db_path = r"D:\QuestionRetrieval\new-q-bank\questions.db"

if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM billing_tenant_question_balances;")
        count = cursor.fetchone()[0]
        print(f"Number of rows in billing_tenant_question_balances: {count}")

        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
