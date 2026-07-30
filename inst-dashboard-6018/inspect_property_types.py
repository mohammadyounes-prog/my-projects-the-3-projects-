import sqlite3
import os

def inspect_property_types():
    db_path = os.path.join(os.path.dirname(__file__), 'questions.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM property_types")
    rows = cursor.fetchall()

    for row in rows:
        print(dict(row))

    conn.close()

if __name__ == "__main__":
    inspect_property_types()