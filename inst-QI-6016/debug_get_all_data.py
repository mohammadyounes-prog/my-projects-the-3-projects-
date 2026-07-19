import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("--- Tenants ---")
    cursor.execute("SELECT * FROM tenants")
    tenants = cursor.fetchall()
    if tenants:
        for tenant in tenants:
            print(dict(tenant))
    else:
        print("No tenants found.")

    print("\n--- Users ---")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(dict(user))
    else:
        print("No users found.")

    print("\n--- Property Types ---")
    cursor.execute("SELECT * FROM property_types")
    property_types = cursor.fetchall()
    if property_types:
        for pt in property_types:
            print(dict(pt))
    else:
        print("No property types found.")

    conn.close()

if __name__ == "__main__":
    get_all_data()

