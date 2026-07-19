
import sqlite3
import os
from pathlib import Path

def inspect_tenants():
    db_path = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, created_by FROM tenants")
        rows = cur.fetchall()
        if not rows:
            print("The tenants table is empty.")
        else:
            for row in rows:
                print(dict(row))
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_tenants()
