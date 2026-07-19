import sqlite3

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, is_admin, tenant_id, is_super_admin FROM users WHERE username = 'superadmin';")
    superadmin_user = cursor.fetchone()

    if superadmin_user:
        print(f"Superadmin User Details:")
        print(f"  ID: {superadmin_user[0]}")
        print(f"  Username: {superadmin_user[1]}")
        print(f"  Is Admin: {superadmin_user[2]}")
        print(f"  Tenant ID: {superadmin_user[3]}")
        print(f"  Is Super Admin: {superadmin_user[4]}")
    else:
        print("Superadmin user not found.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
