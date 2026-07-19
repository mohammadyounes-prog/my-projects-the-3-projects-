import sqlite3

def make_models_global():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE generation_models SET tenant_id = NULL")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    make_models_global()
    print("All models have been made global.")
