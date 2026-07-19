import sqlite3

source_db_path = "D:\\QuestionRetrieval\\new-q-bank\\working-eorkin- afte -q-bank\\questions.db"
target_db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

lookup_tables = [
    "difficulty_levels", "cognitive_levels", "learning_outcomes",
    "school_types", "school_subjects", "school_years",
    "university_majors", "university_courses", "university_materials", "university_semesters",
    "companies", "departments", "job_roles", "question_types", "currencies"
]

def migrate_lookup_table(source_conn, target_conn, table_name):
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute(f"PRAGMA table_info({table_name});")
    source_columns_info = source_cursor.fetchall()
    source_column_names = [col[1] for col in source_columns_info]

    target_cursor.execute(f"PRAGMA table_info({table_name});")
    target_columns_info = target_cursor.fetchall()
    target_column_names = [col[1] for col in target_columns_info]

    common_columns = [col for col in source_column_names if col in target_column_names]

    if not common_columns:
        print(f"Skipping table {table_name}: No common columns found.")
        return

    select_cols = ', '.join(common_columns)
    insert_cols = ', '.join(common_columns)
    placeholders = ', '.join(['?' for _ in common_columns])

    source_cursor.execute(f"SELECT {select_cols} FROM {table_name}")
    rows = source_cursor.fetchall()

    print(f"Migrating data for table: {table_name}")
    for row in rows:
        try:
            target_cursor.execute(
                f"INSERT OR IGNORE INTO {table_name} ({insert_cols}) VALUES ({placeholders})",
                row
            )
        except sqlite3.Error as e:
            print(f"Error inserting into {table_name}: {e} - Row: {row}")
    target_conn.commit()
    print(f"Finished migrating data for table: {table_name}")

try:
    source_conn = sqlite3.connect(source_db_path)
    target_conn = sqlite3.connect(target_db_path)

    for table in lookup_tables:
        migrate_lookup_table(source_conn, target_conn, table)

    print("Lookup tables migration complete.")

except sqlite3.Error as e:
    print(f"An error occurred during migration: {e}")
finally:
    if source_conn:
        source_conn.close()
    if target_conn:
        target_conn.close()
