import sqlite3
import os

DATABASE_FILE = os.path.join('D:\\questionretrieval\\new-q-bank', 'questions.db')

print(f'Checking database file at: {DATABASE_FILE}')
if not os.path.exists(DATABASE_FILE):
    print(f'Error: Database file not found at {DATABASE_FILE}')
else:
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print('--- Questions Table Schema ---')
        cursor.execute('PRAGMA table_info(questions)')
        for row in cursor.fetchall():
            print(row)

        print('\n--- Learning Outcomes Table Schema ---')
        cursor.execute('PRAGMA table_info(learning_outcomes)')
        for row in cursor.fetchall():
            print(row)

        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
