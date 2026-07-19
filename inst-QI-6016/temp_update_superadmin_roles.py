import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

sql_statement = "UPDATE users SET tenant_id = 1, is_super_admin = 1 WHERE username = 'superadmin';"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql_statement)
    conn.commit()
    print(f"Successfully updated superadmin user: tenant_id set to 1, is_super_admin set to 1.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
