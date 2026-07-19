import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / 'questions.db'))

# A mapping of the incorrect new api_name back to the original old api_name
REVERSIONS = {
    "company": "companies",
    "department": "departments",
    "job_role": "job_roles",
    "difficulty_level": "difficulty_levels",
    "cognitive_level": "cognitive_levels",
    "school_type": "school_types",
    "subject": "school_subjects",
    "year": "school_years",
    "major": "university_majors",
    "course": "university_courses",
    "material": "university_materials",
    "semester": "university_semesters",
    "question_type": "question_types",
    "learning_outcome": "learning_outcomes"
}

def revert_api_names():
    """Connects to the database and reverts the api_name values in the property_types table."""
    try:
        print(f"Connecting to database at {DB_PATH}...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Reverting api_name values in property_types table...")
        for new_name, old_name in REVERSIONS.items():
            print(f"  - Renaming '{new_name}' back to '{old_name}'...")
            cursor.execute("UPDATE property_types SET api_name = ? WHERE api_name = ?", (old_name, new_name))

        conn.commit()
        print("\nDatabase reversion complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    revert_api_names()
