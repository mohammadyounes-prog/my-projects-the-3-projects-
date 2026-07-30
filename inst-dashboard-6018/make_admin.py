import sqlite3
import argparse

def make_admin(username: str):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
    conn.commit()
    if conn.total_changes > 0:
        print(f"User '{username}' is now an admin.")
    else:
        print(f"User '{username}' not found.")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make a user an admin.')
    parser.add_argument('username', type=str, help='The username of the user to make an admin.')
    args = parser.parse_args()
    make_admin(args.username)
