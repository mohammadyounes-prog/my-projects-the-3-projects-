import sqlite3
import os

DATABASE_PATH = r"E:\questionretrieval\new-q-bank\config-manager\backend\instances.db"

def check_instance(name):
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at {DATABASE_PATH}")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances WHERE instance_name=?", (name,))
    row = cursor.fetchone()
    if row:
        print(dict(row))
    else:
        print(f"Instance {name} not found in database.")
    conn.close()

if __name__ == "__main__":
    check_instance("instance-13")
