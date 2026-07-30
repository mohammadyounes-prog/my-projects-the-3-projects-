import sqlite3
import os
from pathlib import Path

# --- Configuration ---
# Assumes 'questions.db' is in the project root.
# Assumes this script is run from the project root.
DB_PATH = os.getenv('DB_PATH', 'questions.db')
MIGRATIONS_DIR = Path(__file__).resolve().parent / 'migrations'
MIGRATION_FILE = MIGRATIONS_DIR / 'add_solution_to_questions.sql'

def apply_migration():
    """Connects to the database and applies the specified SQL migration."""
    if not MIGRATION_FILE.exists():
        print(f"Error: Migration file not found at {MIGRATION_FILE}")
        return

    try:
        print(f"Connecting to database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print(f"Reading migration file: {MIGRATION_FILE.name}...")
        with open(MIGRATION_FILE, 'r') as f:
            sql_script = f.read()

        print("Executing migration script...")
        cursor.executescript(sql_script)
        conn.commit()

        print(f"Successfully applied migration: {MIGRATION_FILE.name}")

    except sqlite3.Error as e:
        # Check for "duplicate column name" error
        if "duplicate column name" in str(e).lower():
            print(f"Migration for column 'solution' appears to have already been applied.")
        else:
            print(f"Error applying migration {MIGRATION_FILE.name}: {e}")

    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    apply_migration()
