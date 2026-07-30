
import sqlite3
import argparse
from passlib.context import CryptContext

def create_user(username, password, tenant_id):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)

    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, tenant_id, is_admin) VALUES (?, ?, ?, ?)",
            (username, hashed_password, tenant_id, 0)
        )
        conn.commit()
        print(f"User '{username}' created successfully for tenant {tenant_id}.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists for tenant {tenant_id}.")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new user directly in the database.')
    parser.add_argument('username', type=str, help='The username.')
    parser.add_argument('password', type=str, help='The password.')
    parser.add_argument('tenant_id', type=int, help='The tenant ID.')
    args = parser.parse_args()
    create_user(args.username, args.password, args.tenant_id)
