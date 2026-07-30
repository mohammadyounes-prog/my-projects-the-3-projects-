import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

insert_currencies_sql = """
INSERT OR IGNORE INTO currencies (code, name, decimal_places, is_active) VALUES
('USD', 'United States Dollar', 2, 1),
('EUR', 'Euro', 2, 1),
('GBP', 'British Pound', 2, 1);
"""

insert_products_sql = """
INSERT OR IGNORE INTO billing_products (product_type, audience_type, name, description, price_cents, currency_code, questions_quota, duration_days, is_active) VALUES
('bundle', 'general', 'Basic Question Pack', '100 questions for general use', 1000, 'USD', 100, NULL, 1),
('subscription', 'general', 'Monthly Unlimited', 'Unlimited questions for a month', 2000, 'USD', -1, 30, 1),
('bundle', 'school', 'School Question Pack', '50 questions for school use', 750, 'EUR', 50, NULL, 1);
"""

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Inserting currencies...")
    cursor.executescript(insert_currencies_sql)
    conn.commit()
    print("Currencies inserted.")

    print("Inserting billing products...")
    cursor.executescript(insert_products_sql)
    conn.commit()
    print("Billing products inserted.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
