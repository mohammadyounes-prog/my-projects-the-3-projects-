import sqlite3

db_path = 'D:\\QuestionRetrieval\\new-q-bank\\questions.db'

def run_alter_statements():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ALTER TABLE statements for 'users' table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("Added is_admin to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: is_admin already exists or error: {e}")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN tenant_id INTEGER")
        print("Added tenant_id to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: tenant_id already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        print("Added full_name to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: full_name already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN mobile_phone TEXT")
        print("Added mobile_phone to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: mobile_phone already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN audience_type TEXT")
        print("Added audience_type to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: audience_type already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0")
        print("Added is_super_admin to users table.")
    except sqlite3.OperationalError as e:
        print(f"Info: is_super_admin already exists or error: {e}")

    # ALTER TABLE statements for 'tenants' table
    try:
        cursor.execute("ALTER TABLE tenants ADD COLUMN created_by INTEGER")
        print("Added created_by to tenants table.")
    except sqlite3.OperationalError as e:
        print(f"Info: created_by already exists or error: {e}")

    try:
        cursor.execute("ALTER TABLE tenants ADD COLUMN parent_id INTEGER")
        print("Added parent_id to tenants table.")
    except sqlite3.OperationalError as e:
        print(f"Info: parent_id already exists or error: {e}")

    # ALTER TABLE statements for 'generation_models' table
    try:
        cursor.execute("ALTER TABLE generation_models ADD COLUMN api_key TEXT")
        print("Added api_key to generation_models table.")
    except sqlite3.OperationalError as e:
        print(f"Info: api_key already exists or error: {e}")

    # For 'generation_tasks' timestamp and 'questions' date_created, changing column type directly is complex in SQLite.
    # For now, we will leave them as TEXT/DATE in the DB and handle conversion in Python if needed.
    # If strict type enforcement is required, a more complex migration (create new table, copy data, drop old, rename new) would be needed.

    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_alter_statements()
