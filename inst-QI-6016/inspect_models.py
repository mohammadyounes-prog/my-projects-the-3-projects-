
import sqlite3
import os

db_path = os.getenv('DB_PATH', 'questions.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("--- Querying generation_models table ---")
    cursor.execute("SELECT id, model_name, model_api_name, tenant_id FROM generation_models;")
    rows = cursor.fetchall()
    if not rows:
        print("No models found in the generation_models table.")
    else:
        print("id | model_name | model_api_name | tenant_id")
        print("---------------------------------------------")
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    print("---------------------------------------------")

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
