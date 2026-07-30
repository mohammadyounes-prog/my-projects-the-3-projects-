import sqlite3

DB_FILE = "questions.db"

def print_table_schema(table_name):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Schema for table '{table_name}':")
        cursor.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print_table_schema("tenants")
    print("\n")
    print_table_schema("users")
    print("\n")
    print_table_schema("billing_tenant_question_balances")
    print("\n")
    print_table_schema("billing_events")
    print("\n")
    print_table_schema("billing_products")

