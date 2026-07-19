import os
import sqlite3
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import create_user, get_db_connection
from backend.auth_utils import get_password_hash

# Define the path to your SQLite database
DATABASE_FILE = os.path.join(os.path.dirname(__file__), '..', 'questions.db')

def create_superadmin_user():
    username = "superadmin"
    password = "superadmin" # This will be hashed
    
    hashed_password = get_password_hash(password)
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"User '{username}' already exists. Updating existing user to superadmin.")
            cursor.execute("UPDATE users SET is_admin = 1, is_super_admin = 1, password = ? WHERE username = ?", (hashed_password, username))
            conn.commit()
            print(f"Existing user '{username}' updated to is_admin=1 and is_super_admin=1 with new password.")
        else:
            # Create the user
            # The create_user function doesn't directly support is_super_admin,
            # so we'll update it separately after creation.
            create_user(
                username=username,
                hashed_password=hashed_password,
                is_admin=1,
                full_name="Super Admin",
                tenant_id=1, # Assuming tenant_id 1 exists or is a default for superadmin
                mobile_phone=None,
                audience_type=None
            )
            print(f"User '{username}' created with is_admin=1.")

            # Now, update the is_super_admin flag directly
            cursor.execute("UPDATE users SET is_super_admin = 1 WHERE username = ?", (username,))
            conn.commit()
            print(f"User '{username}' updated to is_super_admin=1.")
        
    except sqlite3.OperationalError as e:
        print(f"Database operational error: {e}. Please ensure the backend server is not running and try again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Creating Superadmin User ---")
    create_superadmin_user()
    print("--------------------------------")
