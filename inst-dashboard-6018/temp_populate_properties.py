
import sqlite3
import os

DB_FILE = "questions.db"
MIGRATION_FILES = [
    "populate_general_property_types.sql",
    "add_school_university_properties.sql",
    "create_property_types_table.sql"
]

def run_migration(cursor, migration_file):
    print(f"Running migration: {migration_file}...")
    if not os.path.exists(migration_file):
        print(f"Error: Migration file not found: {migration_file}")
        return
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

    for migration in MIGRATION_FILES:
        run_migration(cursor, migration)

    conn.commit()
    conn.close()
    print("\nAll specified migrations finished.")

if __name__ == "__main__":
    main()
