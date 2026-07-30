
import sqlite3
import os

db_path = os.getenv('DB_PATH', 'questions.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    target_id = 1
    
    print(f"--- Deleting row from generation_models table where id={target_id} ---")
    cursor.execute("DELETE FROM generation_models WHERE id = ?", (target_id,))
    
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"Successfully deleted {cursor.rowcount} row.")
    else:
        print("No row found with the specified id to delete.")

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
