import sqlite3
import os
from pathlib import Path

DATABASE_FILE = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def update_stress_users_tenant():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update users with tenant_id 12 to tenant_id 1
        cursor.execute("UPDATE users SET tenant_id = 1 WHERE tenant_id = 12")
        conn.commit()
        print(f"Updated {cursor.rowcount} users from tenant_id 12 to tenant_id 1.")

        # Also ensure tenant 1 has some country associations if it doesn't already
        cursor.execute("SELECT COUNT(*) FROM tenant_countries WHERE tenant_id = 1")
        if cursor.fetchone()[0] == 0:
            print("Tenant 1 has no country associations. Adding a default.")
            # Assuming 'USA' exists in the countries table with country_id 'USA1'
            cursor.execute("INSERT OR IGNORE INTO tenant_countries (tenant_id, country_id) VALUES (?, ?)", (1, 'USA1'))
            conn.commit()
            print("Added default country association for tenant 1.")

    except Exception as e:
        conn.rollback()
        print(f"Error updating stress users tenant: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_stress_users_tenant()
