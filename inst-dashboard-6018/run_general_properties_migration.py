# run_general_properties_migration.py
import sqlite3

def run_migration():
    db_path = 'questions.db'
    migration_script_path = 'add_general_property_types.sql'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(migration_script_path, 'r') as f:
            sql_script = f.read()
            
        cursor.executescript(sql_script)
        conn.commit()
        
        print("Successfully applied the general_properties migration.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
