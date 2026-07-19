import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db" # Assuming billing tables are in questions.db, if not, please specify the correct db path

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking 'currencies' table:")
    cursor.execute("SELECT COUNT(*) FROM currencies;")
    count_currencies = cursor.fetchone()[0]
    print(f"Number of rows in 'currencies': {count_currencies}")

    print("\nChecking 'billing_products' table:")
    cursor.execute("SELECT COUNT(*) FROM billing_products;")
    count_billing_products = cursor.fetchone()[0]
    print(f"Number of rows in 'billing_products': {count_billing_products}")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
