import sqlite3
from backend.auth_utils import get_password_hash

DB_FILE = "questions.db"

def create_super_admin():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # First, ensure tenant 1 (the master tenant) exists
        cursor.execute("INSERT OR IGNORE INTO tenants (id, name) VALUES (?, ?)", (1, 'Master Tenant'))

        # Create the superadmin user
        username = "superadmin"
        password = "superadmin"
        hashed_password = get_password_hash(password)
        
        cursor.execute("""
            INSERT INTO users (username, password, is_admin, is_super_admin, tenant_id, full_name)
            VALUES (?, ?, 1, 1, 1, 'Super Admin')
            ON CONFLICT(username) DO UPDATE SET
            password=excluded.password,
            is_admin=excluded.is_admin,
            is_super_admin=excluded.is_super_admin,
            tenant_id=excluded.tenant_id,
            full_name=excluded.full_name;
        """, (username, hashed_password))

        conn.commit()
        print(f"Successfully created or updated superadmin user with username: {username} and password: {password}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_super_admin()
