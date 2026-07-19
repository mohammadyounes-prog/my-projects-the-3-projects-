import sqlite3
import os

DATABASE_FILE = 'questions.db'

def check_generation_models_schema():
    if not os.path.exists(DATABASE_FILE):
        print(f"Error: {DATABASE_FILE} not found.")
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    print("--- generation_models Columns ---")
    cursor.execute("PRAGMA table_info(generation_models)")
    for col in cursor.fetchall():
        print(col)

    print("
--- generation_models Indexes ---")
    cursor.execute("PRAGMA index_list(generation_models)")
    for idx in cursor.fetchall():
        print(idx)
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        for info in cursor.fetchall():
            print(f"  Index detail: {info}")

    conn.close()

if __name__ == "__main__":
    check_generation_models_schema()
