import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_FILE = 'questions.db'

def finish_audit_migration():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    lookup_tables = [
        'learning_outcomes', 'difficulty_levels', 'cognitive_levels', 'question_types',
        'school_types', 'school_subjects', 'school_years', 'university_majors',
        'university_courses', 'university_materials', 'university_semesters',
        'companies', 'departments', 'job_roles', 'gender'
    ]
    
    # Assuming user ID 1 is the default admin/system user
    default_user_id = 1
    
    # Check if user ID 1 exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (default_user_id,))
    if not cursor.fetchone():
        # Fallback to the first available user if 1 doesn't exist
        cursor.execute("SELECT id FROM users LIMIT 1")
        row = cursor.fetchone()
        if row:
            default_user_id = row[0]
            logging.info(f"User ID 1 not found. Using user ID {default_user_id} as default creator.")
        else:
            logging.error("No users found in database. Cannot populate created_by.")
            conn.close()
            return

    for table in lookup_tables:
        try:
            # Check if created_by column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'created_by' in columns:
                # Update NULL created_by values
                cursor.execute(f"UPDATE {table} SET created_by = ? WHERE created_by IS NULL", (default_user_id,))
                affected = cursor.rowcount
                if affected > 0:
                    logging.info(f"Updated {affected} rows in {table} with default created_by={default_user_id}.")
            else:
                logging.warning(f"Table {table} does not have 'created_by' column.")
                
        except sqlite3.OperationalError as e:
            logging.debug(f"Table {table} skip: {e}")
            
    conn.commit()
    conn.close()
    logging.info("Audit migration finished.")

if __name__ == "__main__":
    finish_audit_migration()
