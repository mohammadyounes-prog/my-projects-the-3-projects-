import sqlite3

def insert_dummy_general_properties(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table is empty before inserting
        cursor.execute("SELECT COUNT(*) FROM general;")
        if cursor.fetchone()[0] == 0:
            print("Inserting dummy data into 'general' table...")
            properties = [
                ('General Property 1',),
                ('General Property 2',),
                ('General Property 3',)
            ]
            cursor.executemany("INSERT INTO general (name) VALUES (?);", properties)
            conn.commit()
            print("Dummy data inserted successfully.")
        else:
            print("'general' table already contains data. Skipping insertion.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"
    insert_dummy_general_properties(db_path)

