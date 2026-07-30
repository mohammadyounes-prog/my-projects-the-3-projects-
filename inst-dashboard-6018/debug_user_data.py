import sqlite3
import os
from pathlib import Path

DATABASE_FILE = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def inspect_users_and_tenants():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n--- Inspecting Users ---")
    cursor.execute("SELECT u.id, u.username, u.tenant_id, t.name as tenant_name FROM users u LEFT JOIN tenants t ON u.tenant_id = t.id")
    users = cursor.fetchall()
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(dict(user))

    print("\n--- Inspecting Tenants ---")
    cursor.execute("SELECT t.id, t.name, tc.country_id, c.name as country_name FROM tenants t LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id LEFT JOIN countries c ON tc.country_id = c.country_id")
    tenants = cursor.fetchall()
    if not tenants:
        print("No tenants found.")
    else:
        for tenant in tenants:
            print(dict(tenant))

    print("\n--- Inspecting Tenant Countries ---")
    cursor.execute("SELECT * FROM tenant_countries")
    tenant_countries = cursor.fetchall()
    if not tenant_countries:
        print("No tenant_countries found.")
    else:
        for tc in tenant_countries:
            print(dict(tc))

    print("\n--- Inspecting Countries ---")
    cursor.execute("SELECT * FROM countries")
    countries = cursor.fetchall()
    if not countries:
        print("No countries found.")
    else:
        for country in countries:
            print(dict(country))

    conn.close()

if __name__ == "__main__":
    inspect_users_and_tenants()
