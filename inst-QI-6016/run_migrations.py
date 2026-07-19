import sqlite3
import os
import glob

DB_FILE = "questions.db"

def run_migration(cursor, migration_file):
    print(f"Running migration: {migration_file}...")
    with open(migration_file, 'r') as f:
        sql_script = f.read()
        try:
            cursor.executescript(sql_script)
            print(f"Successfully applied {migration_file}.")
        except sqlite3.Error as e:
            # It's okay if migrations fail because they were already applied.
            # We print the error for debugging but don't stop the process.
            print(f"Info: Could not apply {migration_file}: {e}")

def main():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Find all .sql files in root and in migrations/ directory
    root_migrations = glob.glob('*.sql')
    sub_migrations = glob.glob('migrations/*.sql')
    
    all_migrations = sorted(root_migrations + sub_migrations)

    print(f"Found {len(all_migrations)} migration files to run.")

    for migration in all_migrations:
        run_migration(cursor, migration)

    conn.commit()
    conn.close()
    print("\nAll migrations finished.")

if __name__ == "__main__":
    main()