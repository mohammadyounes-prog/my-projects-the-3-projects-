import sqlite3
import bcrypt

db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"
username = "superadmin"
password = "test"

# Hash the password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if superadmin already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"User '{username}' already exists. Updating password and admin status.")
        cursor.execute("UPDATE users SET password = ?, is_admin = 1 WHERE username = ?", (hashed_password, username))
    else:
        print(f"Adding user '{username}'...")
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, hashed_password, 1))
    
    conn.commit()
    print(f"User '{username}' added/updated successfully.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
