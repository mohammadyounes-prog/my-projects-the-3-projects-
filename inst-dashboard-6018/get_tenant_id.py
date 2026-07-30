import sqlite3
import argparse

def get_tenant_id(name: str):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tenants WHERE name = ?", (name,))
    tenant = cursor.fetchone()
    conn.close()
    if tenant:
        print(tenant[0])
    else:
        print(f"Tenant '{name}' not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get the ID of a tenant.')
    parser.add_argument('name', type=str, help='The name of the tenant.')
    args = parser.parse_args()
    get_tenant_id(args.name)
