import sqlite3

def inspect_db_schema(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Tables in {db_path}:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            table_name = table_name[0]
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, PK: {col[5]}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"
    inspect_db_schema(db_path)

