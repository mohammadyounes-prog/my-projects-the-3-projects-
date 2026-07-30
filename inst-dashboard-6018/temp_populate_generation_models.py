import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

insert_models_sql = """
INSERT OR IGNORE INTO generation_models (model_name, model_api_name, generation_method, tenant_id, is_default, is_active, api_key) VALUES
('Dummy Generator', 'dummy', 'ai', 1, 1, 1, 'dummy_key'),
('Gemini Pro', 'gemini-pro', 'ai', 1, 0, 1, 'your_gemini_api_key'),
('OpenAI GPT-3.5', 'gpt-3.5-turbo', 'ai', 1, 0, 1, 'your_openai_api_key');
"""

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Inserting generation models...")
    cursor.executescript(insert_models_sql)
    conn.commit()
    print("Generation models inserted.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()

