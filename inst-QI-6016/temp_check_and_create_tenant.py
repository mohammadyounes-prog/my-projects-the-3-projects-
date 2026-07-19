import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM tenants;")
    tenants = cursor.fetchall()

    if tenants:
        print("Tenants in the database:")
        for tenant in tenants:
            print(f"  ID: {tenant[0]}, Name: {tenant[1]}")
    else:
        print("No tenants found in the database. Creating a default tenant.")
        cursor.execute("INSERT INTO tenants (name) VALUES ('Global Tenant')")
        conn.commit()
        print("Default 'Global Tenant' created with ID 1.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
