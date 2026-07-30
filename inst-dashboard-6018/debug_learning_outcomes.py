import sqlite3
import json

def inspect_learning_outcomes():
    conn = sqlite3.connect('questions.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check schema
    cursor.execute("PRAGMA table_info(learning_outcomes)")
    schema = [dict(row) for row in cursor.fetchall()]
    print("--- SCHEMA ---")
    print(json.dumps(schema, indent=2))

    # Check first 5 rows
    cursor.execute("SELECT * FROM learning_outcomes LIMIT 5")
    rows = [dict(row) for row in cursor.fetchall()]
    print("
--- ROWS ---")
    print(json.dumps(rows, indent=2))

    conn.close()

if __name__ == "__main__":
    inspect_learning_outcomes()
