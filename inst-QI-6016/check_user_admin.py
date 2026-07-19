
import sqlite3
import argparse

def check_user_admin(username):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, username, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            print(f"User found: id={user[0]}, username={user[1]}, is_admin={user[2]}")
        else:
            print(f"User '{username}' not found.")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check the admin status of a user.')
    parser.add_argument('username', type=str, help='The username to check.')
    args = parser.parse_args()
    check_user_admin(args.username)
