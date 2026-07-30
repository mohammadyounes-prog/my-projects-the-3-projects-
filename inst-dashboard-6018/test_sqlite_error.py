import sqlite3
import os

db_path = r'D:\QuestionRetrieval\new-q-bank\test_error.db'

# Ensure the test database is clean
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    conn.commit()
    print("Table 'test_table' created successfully.")
except Exception as e:
    print(f"Error during first creation: {e}")

try:
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    conn.commit()
    print("Table 'test_table' created successfully again (should not happen).")
except Exception as e:
    print(f"Error during second creation: {e}")

conn.close()
