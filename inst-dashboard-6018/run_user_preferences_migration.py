import sqlite3
import os
import re

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')
SQL_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'migrations', '009_add_user_specific_property_tables.sql')

def run_migration():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Drop existing user-specific property tables if they exist
        drop_statements = [
            "DROP TABLE IF EXISTS user_school_types;",
            "DROP TABLE IF EXISTS user_subjects;",
            "DROP TABLE IF EXISTS user_years;",
            "DROP TABLE IF EXISTS user_university_majors;",
            "DROP TABLE IF EXISTS user_university_courses;",
            "DROP TABLE IF EXISTS user_university_materials;",
            "DROP TABLE IF EXISTS user_university_semesters;",
            "DROP TABLE IF EXISTS user_companies_properties;",
            "DROP TABLE IF EXISTS user_departments;",
            "DROP TABLE IF EXISTS user_job_roles;",
            "DROP TABLE IF EXISTS user_difficulty_levels;",
            "DROP TABLE IF EXISTS user_cognitive_levels;",
            "DROP TABLE IF EXISTS user_learning_outcomes;",
            "DROP TABLE IF EXISTS user_question_types;",
            "DROP TABLE IF EXISTS user_school_preferences;",
            "DROP TABLE IF EXISTS user_university_preferences;",
            "DROP TABLE IF EXISTS user_company_preferences;",
        ]
        for statement in drop_statements:
            print(f"Executing DROP: {statement[:50]}...")
            cursor.execute(statement)

        with open(SQL_SCRIPT_PATH, 'r') as f:
            sql_script = f.read()

        # Split by semicolon to execute individual statements
        # Filter out empty strings that might result from splitting
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]

        for statement in statements:
            print(f"Executing CREATE: {statement[:100]}...")
            cursor.execute(statement)
        
        conn.commit()
        print("Migration script executed successfully.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if conn:
            conn.rollback()
    except FileNotFoundError:
        print(f"Error: SQL script not found at {SQL_SCRIPT_PATH}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

def list_tables():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\n--- Tables in questions.db ---")
        for table in tables:
            print(table[0])
        print("----------------------------")
    except sqlite3.Error as e:
        print(f"SQLite error when listing tables: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
    list_tables()