import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

# A mapping of the incorrect old api_name to the correct new api_name
CORRECTIONS = {
    "companies": "company",
    "departments": "department",
    "job_roles": "job_role",
    "difficulty_levels": "difficulty_level",
    "cognitive_levels": "cognitive_level",
    "school_types": "school_type",
    "school_subjects": "subject",
    "school_years": "year",
    "university_majors": "major",
    "university_courses": "course",
    "university_materials": "material",
    "university_semesters": "semester",
    "question_types": "question_type",
    "learning_outcomes": "learning_outcome"
}

def fix_api_names():
    """Connects to the database and corrects the api_name values in the property_types table."""
    try:
        print(f"Connecting to database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Updating incorrect api_name values in property_types table...")
        for old_name, new_name in CORRECTIONS.items():
            print(f"  - Renaming '{old_name}' to '{new_name}'...")
            cursor.execute("UPDATE property_types SET api_name = ? WHERE api_name = ?", (new_name, old_name))

        conn.commit()
        print("\nDatabase update complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    fix_api_names()
