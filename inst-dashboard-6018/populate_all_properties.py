import sqlite3
import os

# --- Configuration ---
DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

# Define all property types that should exist in the database.
# Format: (Display Name, API Name/Table Name, Audience Type)
ALL_PROPERTIES = [
    # Question Audience
    ('Question Type', 'question_types', 'question'),
    ('Difficulty Level', 'difficulty_levels', 'question'),
    ('Learning Outcome', 'learning_outcomes', 'question'),
    ('Cognitive Level', 'cognitive_levels', 'question'),
    ('Test', 'test', 'question'),
    ('Unit', 'unit', 'question'),

    # School Audience
    ('School Type', 'school_types', 'school'),
    ('Subject', 'school_subjects', 'school'),
    ('Year', 'school_years', 'school'),
    ('Gender', 'gender', 'school'),

    # University Audience
    ('Major', 'university_majors', 'university'),
    ('Course', 'university_courses', 'university'),
    ('Material', 'university_materials', 'university'),
    ('Semester', 'university_semesters', 'university'),

    # Company Audience
    ('Company', 'companies', 'company'),
    ('Department', 'departments', 'company'),
    ('Job Role', 'job_roles', 'company')
]

def setup_all_properties():
    """
    Connects to the database, ensures all lookup tables exist, and inserts
    all necessary property types for all audiences if they do not already exist.
    """
    print(f"Connecting to database: {DATABASE_FILE}")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print("\n--- Step 1: Ensuring all lookup tables exist ---")
        for _, api_name, _ in ALL_PROPERTIES:
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {api_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )
                """)
                print(f"- Table '{api_name}' exists or was created.")
            except sqlite3.OperationalError as e:
                print(f"x Could not create or verify table '{api_name}'. Error: {e}")


        print("\n--- Step 2: Checking and inserting property types into 'property_types' table ---")
        for name, api_name, audience_type in ALL_PROPERTIES:
            # Check if the property already exists for the given audience
            cursor.execute(
                "SELECT 1 FROM property_types WHERE api_name = ? AND audience_type = ?",
                (api_name, audience_type)
            )
            if cursor.fetchone():
                print(f"- Property '{name}' ('{api_name}') already exists for audience '{audience_type}'. Skipping.")
            else:
                # If it doesn't exist, insert it
                print(f"+ Inserting property '{name}' ('{api_name}') for audience '{audience_type}'...")
                cursor.execute(
                    "INSERT INTO property_types (name, api_name, audience_type) VALUES (?, ?, ?)",
                    (name, api_name, audience_type)
                )
                print(f"  -> Successfully inserted.")

        conn.commit()
        print("\nDatabase setup and population complete.")

    except sqlite3.Error as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure the database file is accessible.")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    setup_all_properties()