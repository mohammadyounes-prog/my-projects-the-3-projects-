import sqlite3

db_path = 'D:\\QuestionRetrieval\\new-q-bank\\questions.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables_to_check = [
        "questions", "users", "tenants", "generation_tasks", "generation_models",
        "difficulty_levels", "cognitive_levels", "learning_outcomes", "question_types",
        "school_types", "school_subjects", "school_years",
        "university_majors", "university_courses", "university_materials", "university_semesters",
        "companies", "departments", "job_roles",
        "audience_field_config", "question_actions", "billing_products", "billing_events",
        "tenant_countries", "countries"
    ]

    for table_name in tables_to_check:
        print(f"\nSchema for '{table_name}' table:")
        try:
            cursor.execute(f"PRAGMA table_info({table_name});")
            table_info = cursor.fetchall()
            if not table_info:
                print(f"  Table '{table_name}' does not exist or is empty.")
            for column in table_info:
                print(column)
        except sqlite3.OperationalError as e:
            print(f"  Error retrieving schema for '{table_name}': {e}")

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    if conn:
        conn.close()