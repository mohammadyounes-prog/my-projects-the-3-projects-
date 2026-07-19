import sqlite3
import argparse

def create_tenant(name: str):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tenants (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Tenant '{name}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"Tenant '{name}' already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new tenant.')
    parser.add_argument('name', type=str, help='The name of the tenant to create.')
    args = parser.parse_args()
    create_tenant(args.name)
