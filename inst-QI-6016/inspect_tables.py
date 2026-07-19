import sqlite3
import os

DATABASE_FILE = "questions.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def inspect_table(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if rows:
            print(f"Content of {table_name} table:")
            for row in rows:
                print(dict(row))
        else:
            print(f"{table_name} table is empty.")
    except sqlite3.Error as e:
        print(f"Error querying {table_name} table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_table("users")
    inspect_table("billing_products")
    inspect_table("currencies")
    inspect_table("countries")
    inspect_table("tenants")