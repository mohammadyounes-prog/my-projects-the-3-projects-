import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

def update_api_key(model_api_name: str, new_api_key: str):
    """Updates the API key for a specific model in the generation_models table."""
    try:
        print(f"Connecting to database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print(f"Updating API key for model: {model_api_name}...")
        cursor.execute("UPDATE generation_models SET api_key = ? WHERE model_api_name = ?", (new_api_key, model_api_name))

        conn.commit()
        if cursor.rowcount > 0:
            print(f"Successfully updated API key for model '{model_api_name}'.")
        else:
            print(f"Model '{model_api_name}' not found or API key was already the same.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    # IMPORTANT: Replace 'YOUR_NEW_GOOGLE_API_KEY' with your actual, valid Google API key.
    # You can get a new API key from https://aistudio.google.com/app/apikey
    model_to_update = "gemini-2.5-flash"
    new_key = "YOUR_NEW_GOOGLE_API_KEY" 
    
    if new_key == "YOUR_NEW_GOOGLE_API_KEY":
        print("\nERROR: Please replace 'YOUR_NEW_GOOGLE_API_KEY' in the script with your actual API key.")
    else:
        update_api_key(model_to_update, new_key)
