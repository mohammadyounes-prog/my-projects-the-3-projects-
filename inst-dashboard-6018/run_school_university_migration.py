# run_school_university_migration.py
import sqlite3

def run_migration():
    db_path = 'questions.db'
    migration_script_path = 'add_school_university_properties.sql'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(migration_script_path, 'r') as f:
            sql_script = f.read()
            
        cursor.executescript(sql_script)
        conn.commit()
        
        print("Successfully applied the school_university_properties migration.")
        
    except sqlite3.Error as e:
        # Ignore unique constraint errors in case this is run more than once
        if "UNIQUE constraint failed" in str(e):
            print("Properties already exist, skipping insertion.")
        else:
            print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
