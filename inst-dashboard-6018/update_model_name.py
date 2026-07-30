
import sqlite3
import os

db_path = os.getenv('DB_PATH', 'questions.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # The row to update has model_api_name = 'gemini-1.5-flash'
    target_api_name = "gemini-1.5-flash"
    new_api_name = "gemini-2.5-flash" # The correct, available API name
    
    print(f"--- Updating generation_models table for model '{target_api_name}' ---")
    cursor.execute("""
        UPDATE generation_models 
        SET model_api_name = ?
        WHERE model_api_name = ?
    """, (new_api_name, target_api_name))
    
    conn.commit()
    
    if cursor.rowcount > 0:
        print(f"Successfully updated {cursor.rowcount} row to use '{new_api_name}'.")
    else:
        print(f"No row found with model_api_name '{target_api_name}' to update.")
        
    print("--- Verifying update ---")
    cursor.execute("SELECT id, model_name, model_api_name FROM generation_models WHERE model_api_name = ?", (new_api_name,))
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
