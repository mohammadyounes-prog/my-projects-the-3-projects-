import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def update_superadmin():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # First, check if the is_super_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'is_super_admin' not in columns:
            print("is_super_admin column not found in users table. Please run the migration to add it first.")
            return

        # Update the superadmin user
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'superadmin'")
        conn.commit()
        
        if cursor.rowcount > 0:
            print("Superadmin user updated successfully. 'is_admin' is now set to 1.")
        else:
            print("Superadmin user not found.")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_superadmin()
