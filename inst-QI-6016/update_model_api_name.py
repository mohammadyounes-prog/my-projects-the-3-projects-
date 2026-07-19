import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def update_model_api_name(model_id: int, new_api_name: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE generation_models SET model_api_name = ? WHERE id = ?", (new_api_name, model_id))
        conn.commit()
        print(f"Successfully updated model ID {model_id} to API name: {new_api_name}")
    except Exception as e:
        print(f"Error updating model API name: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    model_id_to_update = 3
    new_api_name = "gemini-pro-latest"
    update_model_api_name(model_id_to_update, new_api_name)