
import sqlite3
import os

db_path = os.getenv('DB_PATH', 'questions.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # The problematic row has id = 1
    target_id = 1
    new_model_name = "Gemini (Primary)" # More user-friendly name
    new_api_name = "gemini-1.5-flash"   # The correct API name
    
    print(f"--- Updating generation_models table for id={target_id} ---")
    cursor.execute("""
        UPDATE generation_models 
        SET model_name = ?, model_api_name = ?
        WHERE id = ?
    """, (new_model_name, new_api_name, target_id))
    
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"Successfully updated {cursor.rowcount} row.")
    else:
        print("No row found with the specified id to update.")
        
    print("--- Verifying update ---")
    cursor.execute("SELECT id, model_name, model_api_name FROM generation_models WHERE id = ?", (target_id,))
    row = cursor.fetchone()
    if row:
        print("Updated row:", row)
    else:
        print("Could not find the row after update.")

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
