import sqlite3
import os
import time
from fastapi.concurrency import run_in_threadpool
import datetime
from typing import List, Optional, Any, Tuple
import re
import json
import logging
import pymysql # New import for pymysql
from online_exam_db_connector import get_online_exam_db_connection # New import
from fastapi import HTTPException, status # Import HTTPException and status for update_lookup_data

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '../', 'questions.db')
logging.debug(f"Using database file: {DATABASE_FILE}") # ADDED LOG

async def get_db():
    conn = await run_in_threadpool(sqlite3.connect, DATABASE_FILE, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # await run_in_threadpool(conn.execute, "PRAGMA journal_mode=WAL") # Commented out for debugging
    try:
        yield conn
    finally:
        await run_in_threadpool(conn.close)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def resolve_student_id_for_user(user_id: int, username: str) -> int:
    """
    Resolves the actual student ID in schooldemo12 for a given local user.
    Handles teachers who take exams via their shadow student accounts (s-username).
    Checks both xId and name columns for the s- prefix.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        
        # 1. Try to find student with xId or name = 's-username' (Teacher shadow account)
        shadow_val = f"s-{username}"
        cursor.execute("SELECT id FROM student WHERE xId = %s OR name = %s", (shadow_val, shadow_val))
        row = cursor.fetchone()
        if row:
            logging.info(f"RESOLVE_ID: Found shadow student ID {row['id']} for teacher {username}")
            return row['id']
            
        # 2. Try to find student with xId or name = username (Regular student account)
        cursor.execute("SELECT id FROM student WHERE xId = %s OR name = %s", (username, username))
        row = cursor.fetchone()
        if row:
            logging.info(f"RESOLVE_ID: Found student ID {row['id']} for user {username}")
            return row['id']
            
        # 3. Fallback: use the schooldemo12_user_id stored in our local DB
        local_conn = get_db_connection()
        local_cursor = local_conn.cursor()
        local_cursor.execute("SELECT schooldemo12_user_id FROM users WHERE id = ?", (user_id,))
        local_row = local_cursor.fetchone()
        local_conn.close()
        
        if local_row and local_row['schooldemo12_user_id']:
            logging.info(f"RESOLVE_ID: Falling back to stored schooldemo12_user_id {local_row['schooldemo12_user_id']} for user {username}")
            return local_row['schooldemo12_user_id']
            
        return None
    except Exception as e:
        logging.error(f"RESOLVE_ID ERROR: Failed to resolve student ID for {username}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def create_generation_tasks_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            request_parameters TEXT,
            num_questions_requested INTEGER,
            num_questions_generated INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def add_user_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN user_id INTEGER")
        # Optionally, update existing questions with a default user_id if needed
        # For example, if user_id 1 is a default admin or system user
        cursor.execute("UPDATE questions SET user_id = 1 WHERE user_id IS NULL")
        conn.commit()
        logging.info("Added user_id column to questions table and updated existing questions.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("user_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_task_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN task_id INTEGER")
        conn.commit()
        logging.info("Added task_id column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("task_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_audience_type_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN audience_type TEXT")
        conn.commit()
        logging.info("Added audience_type column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("audience_type column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_variables_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN variables TEXT")
        conn.commit()
        logging.info("Added variables column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("variables column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_tenant_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN tenant_id INTEGER")
        conn.commit()
        logging.info("Added tenant_id column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("tenant_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_audit_fields_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN approved_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN approved_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN rejected_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN rejected_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN edited_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN edited_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN deleted_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN deleted_at TEXT")
        conn.commit()
        logging.info("Added audit fields to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("Audit fields already exist in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_tamsqb_bank_added_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN tamsqb_bank_added INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        logging.info("Added tamsqb_bank_added column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("tamsqb_bank_added column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_hide_answers_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN hide_answers BOOLEAN DEFAULT 0")
        conn.commit()
        logging.info("Added hide_answers column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("hide_answers column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()



def add_email_to_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        logging.debug("Successfully added email column to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.debug("email column already exists in users table. Skipping migration.")
        else:
            logging.error(f"Failed to add email column to users table: {e}")
            raise e
    finally:
        conn.close()

def add_role_to_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT")
        conn.commit()
        logging.debug("Successfully added role column to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("role column already exists in users table. Skipping migration.")
        else:
            logging.error(f"Failed to add role column to users table: {e}")
            raise e
    finally:
        conn.close()

def add_schooldemo12_user_id_to_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN schooldemo12_user_id INTEGER")
        conn.commit()
        logging.info("Added schooldemo12_user_id column to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("schooldemo12_user_id column already exists in users table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def create_generation_models_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS generation_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_api_name TEXT NOT NULL UNIQUE,
            generation_method TEXT NOT NULL,
            tenant_id INTEGER,
            is_default BOOLEAN NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            api_key TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )"""
    )
    conn.commit()
    conn.close()

def create_exams_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            online_exam_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            exam_name TEXT,
            exam_date_time TEXT,
            duration_minutes INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def create_exam_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_questions (
            exam_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            bank_question_id INTEGER,
            PRIMARY KEY (exam_id, question_id),
            FOREIGN KEY (exam_id) REFERENCES exams(id),
            FOREIGN KEY (question_id) REFERENCES questions(question_id)
        )
    """)
    conn.commit()
    conn.close()

def add_bank_question_id_to_exam_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE exam_questions ADD COLUMN bank_question_id INTEGER")
        conn.commit()
        logging.info("Added bank_question_id column to exam_questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("bank_question_id column already exists in exam_questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def fix_durtation_column_in_exams_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the column with the wrong name exists
        cursor.execute("PRAGMA table_info(exams)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'Durtation' in columns and 'duration_minutes' not in columns:
            cursor.execute("ALTER TABLE exams RENAME COLUMN Durtation TO duration_minutes")
            conn.commit()
            logging.info("Renamed column 'Durtation' to 'duration_minutes' in 'exams' table.")
    except sqlite3.Error as e:
        logging.warning(f"Could not rename column in 'exams' table, may already be correct. Error: {e}")      
    finally:
        conn.close()

def add_report_image_path_to_exams_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE exams ADD COLUMN report_image_path TEXT")
        conn.commit()
        logging.info("Added report_image_path column to exams table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("report_image_path column already exists in exams table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_api_name_to_question_types_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE question_types ADD COLUMN api_name TEXT")
        conn.commit()
        logging.info("Added api_name column to question_types table.")

        # Populate api_name for existing entries
        # Mapping from 'name' to 'api_name'
        api_name_mapping = {
            'Multiple Choice': 'multiple choice',
            '?????? ?? ?????': 'multiple choice',
            'Open-Ended': 'open-ended',
            '????? ??????': 'open-ended',
            # Add other mappings as needed
            'True/False': 'true_false',
            '??/???': 'true_false',
            'Fill-in-the-Blank': 'fill_in_the_blank',
            '????? ??????': 'fill_in_the_blank',
            'Essay': 'essay',
            '?????': 'essay',
            'Short Answer': 'short_answer',
            '????? ?????': 'short_answer',
            'Scenario-based': 'scenario_based',
            '???? ??? ?????????': 'scenario_based',
            'Case Study': 'case_study',
            '????? ????': 'case_study',
        }

        cursor.execute("SELECT id, name, name_ar FROM question_types")
        rows = cursor.fetchall()

        for row in rows:
            question_type_id = row['id']
            name = row['name']
            name_ar = row['name_ar']
            
            api_name = None
            if name in api_name_mapping:
                api_name = api_name_mapping[name]
            elif name_ar in api_name_mapping:
                api_name = api_name_mapping[name_ar]
            
            if api_name:
                cursor.execute("UPDATE question_types SET api_name = ? WHERE id = ?", (api_name, question_type_id))
                logging.info(f"Populated api_name for question_type_id {question_type_id} with '{api_name}'.")
            else:
                logging.warning(f"No api_name mapping found for question_type_id {question_type_id} (name: {name}, name_ar: {name_ar}). Setting to default 'unknown'.")
                cursor.execute("UPDATE question_types SET api_name = ? WHERE id = ?", ('unknown', question_type_id))
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name: api_name" in str(e):
            logging.info("api_name column already exists in question_types table. Skipping migration.")
        else:
            raise e
    except Exception as e:
        logging.error(f"Error during add_api_name_to_question_types_table migration: {e}")
        raise e
    finally:
        conn.close()

# NEW MIGRATION: Create question_types table
def create_question_types_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_ar TEXT,
            api_name TEXT NOT NULL UNIQUE DEFAULT 'unknown',
            audience_type TEXT,
            tenant_id INTEGER
        )
    """)
    
    # Migration: Add audience_type and tenant_id if they don't exist
    try:
        cursor.execute("ALTER TABLE question_types ADD COLUMN audience_type TEXT")
    except sqlite3.OperationalError:
        pass # Already exists
    try:
        cursor.execute("ALTER TABLE question_types ADD COLUMN tenant_id INTEGER")
    except sqlite3.OperationalError:
        pass # Already exists

    # Migration: Set NULL audience_type to 'general' for existing ones
    # cursor.execute("UPDATE question_types SET audience_type = 'general' WHERE audience_type IS NULL")

    conn.commit()
    conn.close()
def add_created_by_to_lookup_tables():
    logging.debug("--- [MIGRATION_CHECK_V1] Starting add_created_by_to_lookup_tables migration ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # List of lookup tables to check
    # We can also fetch all table names if needed, but a defined list is safer.
    lookup_tables = [
        'learning_outcomes', 'difficulty_levels', 'cognitive_levels', 'question_types',
        'school_types', 'school_subjects', 'school_years', 'university_majors',
        'university_courses', 'university_materials', 'university_semesters',
        'companies', 'departments', 'job_roles', 'gender'
    ]
    
    for table in lookup_tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if columns and 'created_by' not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN created_by INTEGER")
                logging.info(f"Added created_by column to {table} table.")
        except sqlite3.OperationalError as e:
            # Table might not exist, which is fine
            logging.debug(f"Could not add created_by to {table}: {e}")
            
    conn.commit()
    conn.close()

def run_migrations():
    logging.info("Starting database migrations...")
    create_generation_tasks_table()
    add_user_id_to_questions_table()
    add_task_id_to_questions_table()
    add_audience_type_to_questions_table()
    add_variables_to_questions_table()
    add_tenant_id_to_questions_table()
    create_generation_models_table()
    create_exams_table()
    fix_durtation_column_in_exams_table()
    add_report_image_path_to_exams_table()
    create_exam_questions_table()
    add_bank_question_id_to_exam_questions_table()
    add_email_to_users_table()
    add_role_to_users_table()
    add_schooldemo12_user_id_to_users_table()
    add_audit_fields_to_questions_table()
    add_tamsqb_bank_added_to_questions_table()
    add_hide_answers_to_questions_table()
    create_question_types_table()
    add_api_name_to_question_types_table()
    add_created_by_to_lookup_tables()
    create_gender_lookup_table()
    create_indexes()
    create_user_specific_audience_tables()
    create_uploaded_files_table()
    add_task_id_to_uploaded_files_table()
    add_uploaded_file_id_to_generation_tasks_table()
    logging.info("Database migrations completed.")

def create_printed_exams_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS printed_exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            exam_id TEXT, -- Optional, can be NULL
            print_timestamp TEXT NOT NULL,
            question_ids TEXT NOT NULL, -- JSON string of question IDs
            filters_used TEXT, -- JSON string of filters used
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def insert_printed_exam(user_id: int, tenant_id: int, exam_name: str, exam_id: Optional[str], question_ids: str, filters_used: Optional[str]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    print_timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO printed_exams (user_id, tenant_id, exam_name, exam_id, print_timestamp, question_ids, filters_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, tenant_id, exam_name, exam_id, print_timestamp, question_ids, filters_used)
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def drop_printed_exams_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS printed_exams")
    conn.commit()
    conn.close()

def create_gender_lookup_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gender (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    # Add default values if table is newly created or empty
    cursor.execute("INSERT OR IGNORE INTO gender (name) VALUES ('Male')")
    cursor.execute("INSERT OR IGNORE INTO gender (name) VALUES ('Female')")
    cursor.execute("INSERT OR IGNORE INTO gender (name) VALUES ('Other')")
    conn.commit()
    conn.close()

# Call the new migration function
create_gender_lookup_table()

def create_indexes():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create helpful indexes if they don't already exist
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_user ON questions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_task ON questions(task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user ON generation_tasks(user_id)")
    conn.commit()
    conn.close()

create_indexes()

def create_user_specific_audience_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    for audience_type in ["school", "university", "company"]:
        table_name = f"user_{audience_type}_preferences"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    conn.commit()
    conn.close()

def create_uploaded_files_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tenant_id INTEGER,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            upload_timestamp TEXT NOT NULL,
            extracted_content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
    """)
    conn.commit()
    conn.close()

def add_task_id_to_uploaded_files_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE uploaded_files ADD COLUMN task_id INTEGER")
        conn.commit()
        logging.info("Added task_id column to uploaded_files table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("task_id column already exists in uploaded_files table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_uploaded_file_id_to_generation_tasks_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN uploaded_file_id INTEGER")
        conn.commit()
        logging.info("Added uploaded_file_id column to generation_tasks table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logging.info("uploaded_file_id column already exists in generation_tasks table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

create_user_specific_audience_tables()
create_uploaded_files_table()
add_task_id_to_uploaded_files_table() # Call the new migration function
add_uploaded_file_id_to_generation_tasks_table() # Call the new migration function


def get_user(username: str, tenant_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    try:
        if tenant_id:
            _cursor.execute("SELECT *, email, schooldemo12_user_id FROM users WHERE username = ? AND tenant_id = ?", (username, tenant_id))
        else:
            _cursor.execute("SELECT *, email, schooldemo12_user_id FROM users WHERE username = ?", (username,))
        user = _cursor.fetchone()
    finally:
        if not cursor: # Only close cursor if it was created by this function
            _cursor.close()
    if not conn: # Only close connection if it was created by this function
        _conn.close()
    return user

def get_user_by_id(user_id: int, tenant_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    try:
        if tenant_id:
            _cursor.execute("SELECT *, email FROM users WHERE id = ? AND tenant_id = ?", (user_id, tenant_id))
        else:
            _cursor.execute("SELECT *, email FROM users WHERE id = ?", (user_id,))
        user = _cursor.fetchone()
    finally:
        if not cursor:
            _cursor.close()
    if not conn:
        _conn.close()
    return user

def create_user(username: str, hashed_password: str, is_admin: int = 0, full_name: Optional[str] = None, tenant_id: Optional[int] = None, mobile_phone: Optional[str] = None, email: Optional[str] = None, audience_type: Optional[str] = None, role: Optional[str] = None, institution: Optional[str] = None, department: Optional[str] = None, country: Optional[str] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    
    try:
        _cursor.execute("INSERT INTO users (username, password, is_admin, full_name, tenant_id, mobile_phone, email, audience_type, role, institution, department, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, hashed_password, is_admin, full_name, tenant_id, mobile_phone, email, audience_type, role, institution, department, country))
        new_id = _cursor.lastrowid # Capture the last inserted row ID
    finally:
        if not cursor: # Only close cursor if it was created by this function
            _cursor.close()
    
    if not conn:
        _conn.commit()
        _conn.close()
    
    return new_id
    
def update_user_password(user_id: int, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

def get_user_by_schooldemo12_id(schooldemo12_user_id: int, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    try:
        _cursor.execute("SELECT * FROM users WHERE schooldemo12_user_id = ?", (schooldemo12_user_id,))
        user = _cursor.fetchone()
        return dict(user) if user else None
    finally:
        if not cursor:
            _cursor.close()
    if not conn:
        _conn.close()


def update_user_schooldemo12_id(user_id: int, schooldemo12_user_id: int, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    logging.debug(f"DEBUG: update_user_schooldemo12_id called with user_id={user_id}, schooldemo12_user_id={schooldemo12_user_id}")
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    try:
        logging.debug(f"DEBUG: Executing UPDATE for users table: SET schooldemo12_user_id = {schooldemo12_user_id} WHERE id = {user_id}")
        _cursor.execute("UPDATE users SET schooldemo12_user_id = ? WHERE id = ?", (schooldemo12_user_id, user_id))
    except sqlite3.Error as e:
        logging.error(f"SQLITE ERROR in update_user_schooldemo12_id for user_id={user_id}: {e}")
        # Re-raise the exception to be caught by the calling function's error handling
        raise
    finally:
        if not cursor: # Only close cursor if it was created by this function
            _cursor.close()
    if not conn: # Only commit and close if this function created the connection
        _conn.commit()
        logging.debug(f"DEBUG: UPDATE committed for user_id={user_id}.")
        _conn.close()

def delete_multiple_tenants(tenant_ids: List[int]):
    if not tenant_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in tenant_ids])
    cursor.execute(f"DELETE FROM tenants WHERE id IN ({placeholders})", tuple(tenant_ids))
    conn.commit()
    conn.close()

def delete_tenant(tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
    conn.commit()
    conn.close()

def update_tenant(tenant_id: int, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tenants SET name = ? WHERE id = ?", (name, tenant_id))
    conn.commit()
    conn.close()

def create_tenant(name: str, parent_id: Optional[int] = None, created_by: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None) -> int:
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    
    try:
        _cursor.execute("INSERT INTO tenants (name, parent_id, created_by) VALUES (?, ?, ?)", (name, parent_id, created_by))
        new_id = _cursor.lastrowid # Store lastrowid before finally block
    finally:
        if not cursor: # Only close cursor if it was created by this function
            _cursor.close()
    if not conn:
        _conn.commit()
        _conn.close()
    
    return _cursor.lastrowid

def get_all_tenants(skip: int = 0, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total count first
    cursor.execute("SELECT COUNT(*) FROM tenants")
    total_tenants = cursor.fetchone()[0]

    # Get paginated tenants
    cursor.execute("""
        SELECT t.id, t.name, t.created_at, u.username as created_by_username, t.created_by as created_by_id, c.name as country, u.mobile_phone as admin_mobile_phone
        FROM tenants t
        LEFT JOIN users u ON t.created_by = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        ORDER BY t.created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, skip))
    tenants = cursor.fetchall()
    conn.close()
    return total_tenants, [dict(tenant) for tenant in tenants]

def get_tenant_by_id(tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.created_at, c.name as country
        FROM tenants t
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        WHERE t.id = ?
    """, (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    logging.debug(f"get_tenant_by_id returning: {tenant}")
    return dict(tenant) if tenant else None

def get_all_users(tenant_ids: Optional[List[int]] = None, skip: int = 0, limit: int = 10, country: Optional[str] = None, product_id: Optional[int] = None, username: Optional[str] = None, phone: Optional[str] = None, sort_by: Optional[str] = None):
    logging.debug(f"get_all_users called with tenant_ids={tenant_ids}, skip={skip}, limit={limit}, country={country}, product_id={product_id}, username={username}, phone={phone}, sort_by={sort_by}")
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT u.id, u.username, u.is_admin, u.full_name, u.tenant_id, t.name as agent_name, GROUP_CONCAT(c.name) as country_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        LEFT JOIN tenant_countries tc ON u.tenant_id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
    """
    
    where_clauses = []
    params = []

    if tenant_ids is not None and len(tenant_ids) > 0:
        placeholders = ','.join('?' for _ in tenant_ids)
        where_clauses.append(f"u.tenant_id IN ({placeholders})")
        params.extend(tenant_ids)

    if username:
        where_clauses.append("u.username LIKE ?")
        params.append(f"%{username}%")

    if phone:
        where_clauses.append("u.mobile_phone LIKE ?")
        params.append(f"%{phone}%")

    if product_id is not None:
        # Join with billing_events to filter by product_id
        base_query += " LEFT JOIN billing_events be ON u.id = be.user_id "
        where_clauses.append("be.product_id = ?")
        params.append(product_id)

    # Construct the WHERE clause
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " GROUP BY u.id"

    having_clauses = []
    if country:
        having_clauses.append("country_name LIKE ?")
        params.append(f"%{country}%")

    if having_clauses:
        base_query += " HAVING " + " AND ".join(having_clauses)

    # Determine sorting order
    order_by_clause = " ORDER BY u.username ASC" # Default sort
    if sort_by == 'fifo':
        order_by_clause = " ORDER BY u.id ASC" # FIFO sorting
    elif sort_by == 'lifo':
        order_by_clause = " ORDER BY u.id DESC" # LIFO sorting
    elif sort_by == 'username':
        order_by_clause = " ORDER BY u.username ASC"

    # Get total count first
    # The count query needs to be adjusted to handle the GROUP BY logic correctly.
    # A subquery is a robust way to do this.
    count_query = f"SELECT COUNT(*) FROM ({base_query}) AS subquery"
    
    logging.debug(f"get_all_users count_query: {count_query}, count_params: {params}")
    cursor.execute(count_query, params)
    total_users_row = cursor.fetchone()
    total_users = total_users_row[0] if total_users_row else 0 # Handle None gracefully

    # Get paginated users
    final_query = base_query + order_by_clause + " LIMIT ? OFFSET ?"
    final_params = params + [limit, skip]

    logging.debug(f"get_all_users final_query: {final_query}, final_params: {final_params}")
    cursor.execute(final_query, final_params)
    users = cursor.fetchall()
    logging.debug(f"get_all_users fetched users: {users}")
    conn.close()
    return total_users, [dict(user) for user in users]

def update_user(user_id: int, username: Optional[str] = None, is_admin: Optional[int] = None, full_name: Optional[str] = None, mobile_phone: Optional[str] = None, email: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(is_admin)
    if full_name is not None:
        updates.append("full_name = ?")
        params.append(full_name)
    if mobile_phone is not None:
        updates.append("mobile_phone = ?")
        params.append(mobile_phone)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    
    if updates:
        sql_query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)
        cursor.execute(sql_query, tuple(params))
        conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Set created_by to NULL in tenants table
        cursor.execute("UPDATE tenants SET created_by = NULL WHERE created_by = ?", (user_id,))

        # Delete from generation_tasks
        cursor.execute("DELETE FROM generation_tasks WHERE user_id = ?", (user_id,))

        # Delete from user preferences tables
        for audience_type in ["school", "university", "company"]:
            table_name = f"user_{audience_type}_preferences"
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
            except sqlite3.OperationalError as e:
                # This will happen if the table doesn't exist, which is fine.
                if "no such table" in str(e):
                    logging.info(f"Table {table_name} does not exist, skipping.")
                else:
                    raise e
        
        # Finally, delete the user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_multiple_users(user_ids: List[int], tenant_id: Optional[int] = None):
    if not user_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in user_ids])
    if tenant_id is None:
        cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", tuple(user_ids))
    else:
        cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders}) AND tenant_id = ?", tuple(user_ids + [tenant_id]))
    conn.commit()
    conn.close()

def add_lookup_data(table_name: str, name: str, name_ar: Optional[str] = None, audience_type: Optional[str] = None, category: Optional[str] = None, category_ar: Optional[str] = None, tenant_id: Optional[int] = None, created_by: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None):
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    
    try:
        columns = ["name"]
        values = [name]
        placeholders = ["?"]

        # Check if the table has specific columns
        _cursor.execute(f"PRAGMA table_info({table_name})")
        table_columns = [col[1] for col in _cursor.fetchall()]
        
        # Add tenant_id if column exists in table and tenant_id is provided
        if "tenant_id" in table_columns and tenant_id is not None:
            columns.append("tenant_id")
            values.append(tenant_id)
            placeholders.append("?")

        # Add created_by if column exists in table and created_by is provided
        if "created_by" in table_columns and created_by is not None:
            columns.append("created_by")
            values.append(created_by)
            placeholders.append("?")

        logging.info(f"--- add_lookup_data inserting into {table_name}: columns={columns}, values={values} ---")

        if table_name == "learning_outcomes":
            if name_ar is not None:
                columns.append("name_ar")
                values.append(name_ar)
                placeholders.append("?")
            if audience_type is not None:
                columns.append("audience_type")
                values.append(audience_type)
                placeholders.append("?")
            if category is not None:
                columns.append("category")
                values.append(category)
                placeholders.append("?")
            if category_ar is not None:
                columns.append("category_ar")
                values.append(category_ar)
                placeholders.append("?")
        
        # Generic handling for name_ar, audience_type, api_name for other lookup tables if columns exist
        # This ensures consistency for tables like question_types and property_types
        if table_name in ["question_types", "property_types"]:
            if name_ar is not None and "name_ar" in table_columns:
                columns.append("name_ar")
                values.append(name_ar)
                placeholders.append("?")
            if audience_type is not None and "audience_type" in table_columns:
                columns.append("audience_type")
                values.append(audience_type)
                placeholders.append("?")
            if "api_name" in table_columns and "api_name" not in columns: # Ensure api_name is added if it exists and not already
                # For new inserts, api_name would typically be derived or explicitly passed.
                # For simplicity, if not passed and exists, it might default or be handled by the table schema.
                # This logic assumes 'name' is often used as 'api_name' if not explicitly provided.
                # However, `property_types` and `question_types` have `api_name TEXT NOT NULL UNIQUE`.
                # We need to ensure api_name is passed explicitly if it's NOT NULL.
                # Given current usage, `api_name` is likely always present in calls for property_types/question_types
                pass # We will rely on the calling code to pass api_name if it's NOT NULL.

        sql_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        _cursor.execute(sql_query, tuple(values))
        item_id = _cursor.lastrowid
    finally:
        if not cursor: # Only close cursor if it was created by this function
            _cursor.close()
    
    if not conn:
        _conn.commit()
        _conn.close()

    return item_id

def update_lookup_data(table_name: str, item_id: int, **fields):
    if not fields:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check table info to see which columns exist
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        updates = []
        params = []
        for key, value in fields.items():
            if key in columns:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return

        sql = f"UPDATE {table_name} SET {', '.join(updates)} WHERE id = ?"
        params.append(item_id)
        
        cursor.execute(sql, tuple(params))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An entry with these details already exists in {table_name}."
        )
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Database error updating lookup data in {table_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during update: {e}"
        )
    finally:
        conn.close()

def delete_lookup_data(table_name: str, item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def ensure_models_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            method TEXT NOT NULL CHECK (method IN ('ai','internet','both')),
            provider TEXT NOT NULL CHECK (provider IN ('google','openai','custom')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def get_models(method: str | None = None) -> list[dict]:
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if method:
        cur.execute("SELECT * FROM models WHERE method = ? ORDER BY display_name", (method,))
    else:
        cur.execute("SELECT * FROM models ORDER BY display_name")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_models() -> list[dict]:
    return get_models(None)

def get_model_by_name(name: str) -> dict | None:
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM models WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def create_model(name: str, display_name: str, method: str, provider: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO models (name, display_name, method, provider) VALUES (?,?,?,?)",
        (name, display_name, method, provider),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_model(model_id: int, **fields):
    if not fields:
        return
    allowed = {"name", "display_name", "method", "provider"}
    sets, values = [], []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k} = ?")
            values.append(v)
    if not sets:
        return
    values.append(model_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE models SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_model(model_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM models WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()


def create_generation_model(model_name: str, model_api_name: str, generation_method: str, tenant_id: Optional[int] = None, is_default: bool = False, is_active: bool = True, api_key: Optional[str] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None) -> int:
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()

    sql_query = """
        INSERT INTO generation_models (model_name, model_api_name, generation_method, tenant_id, is_default, is_active, api_key)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = [model_name, model_api_name, generation_method, tenant_id, is_default, is_active, api_key]

    logging.debug(f"Executing create_generation_model: {sql_query} with params: {params}")

    try:
        _cursor.execute(sql_query, tuple(params))
        new_id = _cursor.lastrowid
    finally:
        if not cursor:
            _cursor.close()
    
    if not conn:
        _conn.commit()
        _conn.close()
        
    return new_id


def insert_generation_task(user_id: int, request_parameters: str, num_questions_requested: int, num_questions_generated: int, status: str = 'completed', tenant_id: int | None = None, uploaded_file_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None) -> int:
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    logging.debug(f"Inserting generation task for user_id: {user_id}, uploaded_file_id: {uploaded_file_id}")
    
    try:
        # Try to insert tenant_id and uploaded_file_id if columns exist; fallback to insert without them
        try:
            _cursor.execute(
                """INSERT INTO generation_tasks (
                    user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id)
            )
        except sqlite3.OperationalError as e:
            if "no such column: tenant_id" in str(e):
                logging.warning(f"tenant_id column missing. Inserting without tenant_id. Error: {e}")
                try:
                    _cursor.execute(
                        """INSERT INTO generation_tasks (
                            user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id)
                    )
                except sqlite3.OperationalError as e_inner:
                    if "no such column: uploaded_file_id" in str(e_inner):
                        logging.warning(f"uploaded_file_id column missing. Inserting without uploaded_file_id. Error: {e_inner}")
                        _cursor.execute(
                            """INSERT INTO generation_tasks (
                                user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status
                            ) VALUES (?, ?, ?, ?, ?, ?)""",
                            (user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status)
                        )
                    else:
                        raise e_inner
            elif "no such column: uploaded_file_id" in str(e):
                logging.warning(f"uploaded_file_id column missing. Inserting without uploaded_file_id. Error: {e}")
                _cursor.execute(
                    """INSERT INTO generation_tasks (
                        user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status)
                )
            else:
                raise e
        task_id = _cursor.lastrowid
    finally:
        if not cursor:
            _cursor.close()
    
    if not conn:
        _conn.commit()
        _conn.close()
    return task_id

def get_exams_for_user(user_id: int, limit: int = 10, offset: int = 0, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, online_exam_id, exam_name, exam_date_time, duration_minutes, created_at FROM exams WHERE user_id = ?"
    params = [user_id]
    
    if start_date:
        query += " AND date(created_at) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(created_at) <= date(?)"
        params.append(end_date)
        
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    exams = cursor.fetchall()
    conn.close()
    return [dict(exam) for exam in exams]

def get_total_exams_for_user_count(user_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM exams WHERE user_id = ?"
    params = [user_id]

    if start_date:
        query += " AND date(created_at) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(created_at) <= date(?)"
        params.append(end_date)

    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_exam_by_id(exam_id: int) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, online_exam_id, user_id, exam_name, exam_date_time, duration_minutes, created_at, report_image_path FROM exams WHERE id = ?", (exam_id,))
    exam = cursor.fetchone()
    conn.close()
    return dict(exam) if exam else None

def update_exam_report_image_path(exam_id: int, report_image_path: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE exams SET report_image_path = ? WHERE id = ?", (report_image_path, exam_id))
    conn.commit()
    conn.close()

def update_exam_report_image_path(exam_id: int, report_image_path: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE exams SET report_image_path = ? WHERE id = ?", (report_image_path, exam_id))
    conn.commit()
    

def get_exam_questions_and_details(exam_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Join exam_questions with questions table to get full details
    query = """
        SELECT
            eq.question_id,
            eq.bank_question_id,
            q.question_text,
            q.choice_1, q.choice_2, q.choice_3, q.choice_4,
            q.correct_option,
            q.mark,
            lo.name AS learning_outcome_name,
            qt.api_name AS question_type,
            dl.name AS difficulty_level_name
        FROM exam_questions eq
        JOIN questions q ON eq.question_id = q.question_id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        WHERE eq.exam_id = ?
        ORDER BY eq.question_id ASC
    """
    cursor.execute(query, (exam_id,))
    questions = cursor.fetchall()
    conn.close()
    return [dict(q) for q in questions]

def get_student_results_for_exam(exam_id: int, student_schooldemo12_id: int) -> List[dict]:
    """
    Fetches student results from schooldemo12 DB for a given online_exam_id and student_id.
    """
    logging.debug(f"get_student_results_for_exam: schooldemo12 student_id: {student_schooldemo12_id}, local exam_id: {exam_id}")

    if not student_schooldemo12_id:
        logging.warning("No student_schooldemo12_id provided. Cannot fetch student results.")
        return []

    conn_schooldemo12 = None
    try:
        conn_schooldemo12 = get_online_exam_db_connection()
        cursor = conn_schooldemo12.cursor()

        # First, get the online_exam_id from the local exams table
        local_conn = get_db_connection()
        local_cursor = local_conn.cursor()
        local_cursor.execute("SELECT online_exam_id FROM exams WHERE id = ?", (exam_id,))
        exam_row = local_cursor.fetchone()
        local_conn.close()

        if not exam_row:
            logging.warning(f"Online exam ID not found for local exam ID {exam_id}.")
            return []
        
        online_exam_id = exam_row['online_exam_id']
        logging.debug(f"get_student_results_for_exam: Local exam_id: {exam_id}, Fetched online_exam_id: {online_exam_id}")

        query = """
            SELECT
                sr.examDataId,
                ed.bankId,
                sr.answer AS student_answer_index,
                sr.currentMark AS student_mark,
                sr.examDataMark AS question_mark,
                sr.answerText
            FROM studentresult sr
            JOIN examdata ed ON sr.examDataId = ed.id
            WHERE sr.studentId = %s AND sr.examId = %s
            ORDER BY sr.examDataId ASC
        """
        cursor.execute(query, (student_schooldemo12_id, online_exam_id))
        results = cursor.fetchall()
        logging.debug(f"get_student_results_for_exam: Found {len(results)} results from Studentresult table.")

        processed_results = []
        questions_for_exam = get_exam_questions_and_details(exam_id)
        # Map local question_id to its details for easier lookup
        question_details_map = {q['question_id']: q for q in questions_for_exam}
        
        # We need bank_question_id to link studentresults to local questions
        # Create a map from bank_question_id to local question_id
        bank_to_local_qid_map = {}
        for q_detail in questions_for_exam:
            if q_detail.get('bank_question_id'):
                bank_to_local_qid_map[q_detail['bank_question_id']] = q_detail['question_id']

        for res in results:
            res_dict = dict(res)
            
            # Link student result to local question details using bankId
            local_q_id = bank_to_local_qid_map.get(res_dict['bankId'])
            question_detail = question_details_map.get(local_q_id)

            if question_detail:
                # Populate choices
                res_dict['choice_1'] = question_detail.get('choice_1')
                res_dict['choice_2'] = question_detail.get('choice_2')
                res_dict['choice_3'] = question_detail.get('choice_3')
                res_dict['choice_4'] = question_detail.get('choice_4')
                res_dict['correct_option'] = question_detail.get('correct_option')
                res_dict['question_text'] = question_detail.get('question_text')
                res_dict['learning_outcome_name'] = question_detail.get('learning_outcome_name')
            else:
                logging.warning(f"get_student_results_for_exam: Could not find local question details for bankId: {res_dict.get('bankId')}")
                res_dict['student_answer_choice'] = res_dict.get('answerText', 'N/A') # Fallback
                res_dict['is_correct'] = False # Cannot determine correctness without question details
                
            processed_results.append(res_dict)
            
        return processed_results

    except pymysql.Error as e:
        logging.error(f"Error fetching student results from schooldemo12 DB: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching student results: {e}")
        return []
    finally:
        if conn_schooldemo12:
            conn_schooldemo12.close()

def get_search_suggestions(term: str, limit: int = 10) -> list[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    suggestions = set() # Use a set to store unique suggestions

    # Search in question_text
    cursor.execute(
        "SELECT question_text FROM questions WHERE question_text LIKE ? LIMIT ?",
        (f"%{term}%", limit)
    )
    for row in cursor.fetchall():
        suggestions.add(row['question_text'])

    # Search in choices
    for i in range(1, 5): # choice_1 to choice_4
        cursor.execute(
            f"SELECT choice_{i} FROM questions WHERE choice_{i} LIKE ? AND choice_{i} IS NOT NULL LIMIT ?",
            (f"%{term}%", limit)
        )
        for row in cursor.fetchall():
            suggestions.add(row[f'choice_{i}'])
    
    # Search in correct_option
    cursor.execute(
        "SELECT correct_option FROM questions WHERE correct_option LIKE ? AND correct_option IS NOT NULL LIMIT ?",
        (f"%{term}%", limit)
    )
    for row in cursor.fetchall():
        suggestions.add(row['correct_option'])

    conn.close()
    return sorted(list(suggestions))[:limit]

def get_total_questions_count(query: Optional[str] = None, status: Optional[str] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None,
                              date_from: Optional[str] = None, date_to: Optional[str] = None,
                              approved_by: Optional[int] = None, rejected_by: Optional[int] = None,
                              edited_by: Optional[int] = None, deleted_by: Optional[int] = None,
                              filter_by_task_topic_context: Optional[str] = None, # NEW PARAMETER FOR PREVIOUS TASK
                              task_id: Optional[int] = None,
                              audience_type: Optional[str] = None) -> int: # NEW PARAMETER
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT COUNT(q.question_id) FROM questions q"
    params = []

    if filter_by_task_topic_context: # NEW LOGIC (from previous task)
        sql_query += " JOIN generation_tasks gt ON q.task_id = gt.task_id"
    
    where_clauses = []
    if query:
        where_clauses.append("""(
            q.question_text LIKE ? OR
            q.choice_1 LIKE ? OR
            q.choice_2 LIKE ? OR
            q.choice_3 LIKE ? OR
            q.choice_4 LIKE ? OR
            q.correct_option LIKE ?
        )""")
        for _ in range(6):
            params.append(f"%{query}%")

    if status:
        where_clauses.append("q.status = ?")
        params.append(status)

    if task_id is not None: # NEW LOGIC
        where_clauses.append("q.task_id = ?")
        params.append(task_id)

    if user_id is not None:
        where_clauses.append("q.user_id = ?")
        params.append(user_id)

    if tenant_id is not None:
        where_clauses.append("q.tenant_id = ?")
        params.append(tenant_id)
    
    if audience_type is not None: # NEW LOGIC
        where_clauses.append("q.audience_type = ?")
        params.append(audience_type)

    if date_from and date_to:
        where_clauses.append("date(q.date_created) BETWEEN date(?) AND date(?)")
        params.extend([date_from, date_to])
    elif date_from:
        where_clauses.append("date(q.date_created) >= date(?)")
        params.append(date_from)
    elif date_to:
        where_clauses.append("date(q.date_created) <= date(?)")
        params.append(date_to)

    if approved_by is not None:
        where_clauses.append("q.approved_by = ?")
        params.append(approved_by)
    if rejected_by is not None:
        where_clauses.append("q.rejected_by = ?")
        params.append(rejected_by)
    if edited_by is not None:
        where_clauses.append("q.edited_by = ?")
        params.append(edited_by)
    if deleted_by is not None:
        where_clauses.append("q.deleted_by = ?")
        params.append(deleted_by)

    if filter_by_task_topic_context: # NEW LOGIC (from previous task)
        where_clauses.append("gt.request_parameters LIKE ?")
        params.append(f"%\"topic_context\": \"%{filter_by_task_topic_context}%\"%")

    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)

    logging.debug(f"get_total_questions_count SQL Query: {sql_query}")
    logging.debug(f"get_total_questions_count Parameters: {params}")
    cursor.execute(sql_query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_questions(query: Optional[str] = None, status: Optional[str] = None, task_id: Optional[int] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None, skip: int = 0, limit: int = 10,
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  approved_by: Optional[int] = None, rejected_by: Optional[int] = None,
                  edited_by: Optional[int] = None, deleted_by: Optional[int] = None,
                  filter_by_task_topic_context: Optional[str] = None, # NEW PARAMETER FOR PREVIOUS TASK
                  include_correct_answer: bool = True,
                  audience_type: Optional[str] = None): # NEW PARAMETER
    import time
    t0 = time.perf_counter()
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = f"""SELECT 
        q.question_id, q.author_creator, q.date_created, q.question_text,
        q.choice_1, q.choice_2, q.choice_3, q.choice_4, 
        CASE WHEN {1 if include_correct_answer else 0} THEN q.correct_option ELSE NULL END as correct_option,
        dl.name as difficulty_level, cl.name as cognitive_level, lo.name as learning_outcome,
        qt.api_name as question_type,
        st.name as school_type, ss.name as subject, sy.name as year,
        um.name as major, uc.name as course, umt.name as material, us.name as semester,
        comp.name as company, dep.name as department, jr.name as job_role,
        q.mark, q.time_seconds, q.discriminating_factor, q.status, q.audience_type, q.variables, q.solution,
        q.hide_answers as answers_hidden
        FROM questions q
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN school_types st ON q.school_type_id = st.id
        LEFT JOIN school_subjects ss ON q.subject_id = ss.id
        LEFT JOIN school_years sy ON q.year_id = sy.id
        LEFT JOIN university_majors um ON q.major_id = um.id
        LEFT JOIN university_courses uc ON q.course_id = uc.id
        LEFT JOIN university_materials umt ON q.material_id = umt.id
        LEFT JOIN university_semesters us ON q.semester_id = us.id
        LEFT JOIN companies comp ON q.company_id = comp.id
        LEFT JOIN departments dep ON q.department_id = dep.id
        LEFT JOIN job_roles jr ON q.job_role_id = jr.id
    """
    params = []

    where_clauses = []
    if query:
        where_clauses.append("""(
            q.question_text LIKE ? OR
            q.choice_1 LIKE ? OR
            q.choice_2 LIKE ? OR
            q.choice_3 LIKE ? OR
            q.choice_4 LIKE ? OR
            q.correct_option LIKE ?
        )""")
        # Add the query parameter for each LIKE clause
        for _ in range(6): # 6 fields to search
            params.append(f"%{query}%")

    if status:
        where_clauses.append("q.status = ?")
        params.append(status)

    if task_id is not None: # NEW LOGIC
        where_clauses.append("q.task_id = ?")
        params.append(task_id)

    if user_id is not None:
        where_clauses.append("q.user_id = ?")
        params.append(user_id)

    if tenant_id is not None:
        where_clauses.append("q.tenant_id = ?")
        params.append(tenant_id)
    
    if audience_type is not None: # NEW LOGIC
        where_clauses.append("q.audience_type = ?")
        params.append(audience_type)

    if date_from and date_to:
        where_clauses.append("date(q.date_created) BETWEEN date(?) AND date(?)")
        params.extend([date_from, date_to])
    elif date_from:
        where_clauses.append("date(q.date_created) >= date(?)")
        params.append(date_from)
    elif date_to:
        where_clauses.append("date(q.date_created) <= date(?)")
        params.append(date_to)

    if approved_by is not None:
        where_clauses.append("q.approved_by = ?")
        params.append(approved_by)
    if rejected_by is not None:
        where_clauses.append("q.rejected_by = ?")
        params.append(rejected_by)
    if edited_by is not None:
        where_clauses.append("q.edited_by = ?")
        params.append(edited_by)
    if deleted_by is not None:
        where_clauses.append("q.deleted_by = ?")
        params.append(deleted_by)

    if filter_by_task_topic_context: # NEW LOGIC for filter_by_task_topic_context
        sql_query += " JOIN generation_tasks gt ON q.task_id = gt.task_id"
        where_clauses.append("gt.request_parameters LIKE ?")
        params.append(f"%\"topic_context\": \"%{filter_by_task_topic_context}%\"%")

    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)

    sql_query += " ORDER BY q.question_id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    logging.debug(f"get_questions SQL Query: {sql_query}")
    logging.debug(f"get_questions Parameters: {params}")
    cursor.execute(sql_query, params)
    questions = cursor.fetchall()
    t1 = time.perf_counter()
    logging.info(f"TIMING: get_questions took {int((t1 - t0)*1000)} ms (limit={limit}, skip={skip})")
    
    # NEW DEBUG LOGGING
    if questions:
        first_q = dict(questions[0])
        logging.debug(f"DEBUG_FETCH: First question record properties: school_type='{first_q.get('school_type')}', subject='{first_q.get('subject')}', year='{first_q.get('year')}'")
    else:
        logging.debug("DEBUG_FETCH: No questions returned from query.")

    conn.close()
    
    questions_list = []
    for q in questions:
        question_dict = dict(q)
        if question_dict.get('variables'):
            question_dict['variables'] = json.loads(question_dict['variables'])
        questions_list.append(question_dict)

    return questions_list

def get_lookup_data(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name FROM {table_name}")
    data = [{row['id']: row['name']} for row in cursor.fetchall()]
    conn.close()
    return data

def get_lookup_data_list(table_name: str, lang: Optional[str] = None, audience_type: Optional[str] = None, category: Optional[str] = None, tenant_id: Optional[int] = None, user_id: Optional[int] = None, skip: int = 0, limit: int = 1000):
    logging.info(f"--- [RELOAD_CHECK_V3] get_lookup_data_list called with table_name: {table_name}, audience_type: {audience_type}, category: {category}, tenant_id: {tenant_id}, user_id: {user_id}, skip: {skip}, limit: {limit} ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    has_name_ar = "name_ar" in columns
    has_api_name = "api_name" in columns
    has_tenant_id = "tenant_id" in columns 

    has_audience_type = "audience_type" in columns
    has_category = "category" in columns
    has_category_ar = "category_ar" in columns
    has_created_by = "created_by" in columns

    id_col = "t.id"
    if table_name == "countries":
        id_col = "t.country_id"

    select_cols = [id_col]
    if lang == 'ar' and has_name_ar:
        select_cols.append("COALESCE(t.name_ar, t.name) AS name")
    else:
        select_cols.append("t.name")
    
    # Keep name_ar as a separate field if it exists, for completeness in LookupItem
    if has_name_ar: select_cols.append("t.name_ar") 

    if has_api_name: select_cols.append("t.api_name")
    if has_tenant_id: select_cols.append("t.tenant_id")
    if table_name == "learning_outcomes":
        if has_audience_type: select_cols.append("t.audience_type")
        if has_category: select_cols.append("t.category")
        if has_category_ar: select_cols.append("t.category_ar")
    
    if has_created_by:
        select_cols.append("t.created_by")
        select_cols.append("u.username as created_by_username")

    select_statement = ", ".join(select_cols)
    sql_query = f"SELECT {select_statement} FROM {table_name} t"
    if has_created_by:
        sql_query += " LEFT JOIN users u ON t.created_by = u.id"
    
    query_params = []
    where_clauses = []

    if table_name == "learning_outcomes":
        if audience_type and has_audience_type:
            where_clauses.append("(t.audience_type = ? OR t.audience_type IS NULL OR t.audience_type = 'general')")
            query_params.append(audience_type)
        if category and has_category:
            # Determine which category column to filter by based on lang
            if lang == 'ar' and has_category_ar:
                where_clauses.append("t.category_ar = ?")
            else:
                where_clauses.append("t.category = ?")
            query_params.append(category)
    elif table_name in ["question_types", "property_types"]:
        if audience_type and has_audience_type:
            where_clauses.append("(t.audience_type = ? OR t.audience_type IS NULL OR t.audience_type = 'general')")
            query_params.append(audience_type)
    
    # --- Private vs Global Logic ---
    # Show items where:
    # 1. They are global (tenant_id IS NULL)
    # 2. They were created by this specific user
    # 3. They were created by Superadmin (user_id 25)
    
    filter_parts = []
    
    if has_tenant_id:
        filter_parts.append("t.tenant_id IS NULL")
        
    if has_created_by:
        filter_parts.append("t.created_by = 25") # Superadmin
        if user_id is not None:
            filter_parts.append("t.created_by = ?")
            query_params.append(user_id)
            
    if filter_parts:
        # Wrap the lookup visibility filter in parentheses
        where_clauses.append(f"({' OR '.join(filter_parts)})")

    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)

    # Sort countries alphabetically, others by ID ascending
    order_col = "t.name" if table_name == "countries" else id_col
    sql_query += f" ORDER BY {order_col} ASC LIMIT ? OFFSET ?"
    query_params.extend([limit, skip])

    logging.debug(f"DEBUG_LO: Final SQL query: {sql_query} | Params: {query_params}")

    try:
        cursor.execute(sql_query, query_params)
        data = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        logging.error(f"Error fetching lookup data for {table_name}: {e}")
        data = []
    finally:
        conn.close()
        
    logging.debug(f"DEBUG: get_lookup_data_list('{table_name}', lang='{lang}', audience_type='{audience_type}') returning: {data}")
    return data

def get_unique_categories_for_audience(audience_type: str, tenant_id: Optional[int] = None, user_id: Optional[int] = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(learning_outcomes)")
    columns = [col[1] for col in cursor.fetchall()]
    has_audience_type = "audience_type" in columns
    has_category = "category" in columns
    has_category_ar = "category_ar" in columns
    has_tenant_id = "tenant_id" in columns
    has_created_by = "created_by" in columns

    if not has_audience_type or not has_category:
        logging.warning("learning_outcomes table does not have 'audience_type' or 'category' columns.")
        conn.close()
        return []

    select_cols = ["DISTINCT category"]
    if has_category_ar:
        select_cols.append("category_ar")

    sql_query = f"SELECT {', '.join(select_cols)} FROM learning_outcomes WHERE audience_type = ?"
    params = [audience_type]

    # --- Private vs Global Logic ---
    filter_parts = []

    if has_tenant_id:
        filter_parts.append("tenant_id IS NULL")

    if has_created_by:
        filter_parts.append("created_by = 25") # Superadmin
        if user_id is not None:
            filter_parts.append("created_by = ?")
            params.append(user_id)

    if filter_parts:
        sql_query += f" AND ({' OR '.join(filter_parts)})"

    try:
        cursor.execute(sql_query, tuple(params))
        data = [dict(row) for row in cursor.fetchall()]
        logging.info(f"Unique categories for audience_type '{audience_type}' (tenant_id: {tenant_id}, user_id: {user_id}): {data}")
    except sqlite3.OperationalError as e:
        logging.error(f"Error fetching unique categories: {e}")
        data = []
    finally:
        conn.close()

    return data
def get_course_filter_options(audience_type: str, lang: Optional[str] = None, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
    filters = []

    if audience_type == "school":
        subjects = get_lookup_data_list("school_subjects", lang=lang, tenant_id=tenant_id)
        years = get_lookup_data_list("school_years", lang=lang, tenant_id=tenant_id)
        filters.append({"name": "subject", "values": [item.get('name') or item.get('name_ar') for item in subjects if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "year", "values": [item.get('name') or item.get('name_ar') for item in years if item.get('name') or item.get('name_ar')]})
    elif audience_type == "university":
        majors = get_lookup_data_list("university_majors", lang=lang, tenant_id=tenant_id)
        courses = get_lookup_data_list("university_courses", lang=lang, tenant_id=tenant_id)
        materials = get_lookup_data_list("university_materials", lang=lang, tenant_id=tenant_id)
        semesters = get_lookup_data_list("university_semesters", lang=lang, tenant_id=tenant_id)
        filters.append({"name": "major", "values": [item.get('name') or item.get('name_ar') for item in majors if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "course", "values": [item.get('name') or item.get('name_ar') for item in courses if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "material", "values": [item.get('name') or item.get('name_ar') for item in materials if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "semester", "values": [item.get('name') or item.get('name_ar') for item in semesters if item.get('name') or item.get('name_ar')]})
    elif audience_type == "company":
        companies = get_lookup_data_list("companies", lang=lang, tenant_id=tenant_id)
        departments = get_lookup_data_list("departments", lang=lang, tenant_id=tenant_id)
        roles = get_lookup_data_list("job_roles", lang=lang, tenant_id=tenant_id)
        filters.append({"name": "company", "values": [item.get('name') or item.get('name_ar') for item in companies if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "department", "values": [item.get('name') or item.get('name_ar') for item in departments if item.get('name') or item.get('name_ar')]})
        filters.append({"name": "job_role", "values": [item.get('name') or item.get('name_ar') for item in roles if item.get('name') or item.get('name_ar')]})

    return filters



def get_question_types_by_audience(audience_type: str, lang: Optional[str] = None, tenant_id: Optional[int] = None, user_id: Optional[int] = None) -> List[dict]:
    # This function will now query the question_types table, filtered by audience_type, tenant_id and user_id
    # The hardcoded logic is replaced by a call to the more generic get_lookup_data_list

    # We pass the audience_type to filter by. tenant_id and user_id are also passed for specific filtering.
    return get_lookup_data_list("question_types", lang=lang, audience_type=audience_type, tenant_id=tenant_id, user_id=user_id)
def get_all_learning_outcomes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if 'name_ar' column exists
    cursor.execute("PRAGMA table_info(learning_outcomes)")
    columns = [col[1] for col in cursor.fetchall()]
    has_name_ar = "name_ar" in columns

    if has_name_ar:
        cursor.execute("SELECT name, name_ar FROM learning_outcomes")
    else:
        cursor.execute("SELECT name, name as name_ar FROM learning_outcomes")
        
    outcomes = [{'name': row['name'], 'name_ar': row['name_ar']} for row in cursor.fetchall()]
    conn.close()
    return outcomes

def get_lookup_id_by_name(table_name: str, name: str) -> Optional[int]:
    if not name:
        logging.debug(f"get_lookup_id_by_name: Received empty name for table='{table_name}', returning None.")
        return None
    name_stripped = name.strip()
    if not name_stripped:
        logging.debug(f"get_lookup_id_by_name: Received name '{name}' became empty after strip for table='{table_name}', returning None.")
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    logging.debug(f"get_lookup_id_by_name: START robust search for table='{table_name}' with stripped_name='{name_stripped}'")

    # Fetch all entries from the table
    try:
        # Determine if 'name_ar' or 'api_name' columns exist
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        has_name_ar = "name_ar" in column_names
        has_api_name = "api_name" in column_names

        select_cols = ["id", "name"]
        if has_name_ar:
            select_cols.append("name_ar")
        if has_api_name:
            select_cols.append("api_name")
        
        select_clause = ", ".join(select_cols)
        cursor.execute(f"SELECT {select_clause} FROM {table_name}")
        all_entries = cursor.fetchall()
    except sqlite3.OperationalError as e:
        logging.error(f"get_lookup_id_by_name: Error fetching all entries from table '{table_name}': {e}")
        conn.close()
        return None

    # Normalize the search term aggressively
    normalized_search_term = name_stripped.lower().replace('\xa0', ' ').replace('\u202f', ' ').strip() # Handle common non-breaking spaces

    result_id = None
    for entry in all_entries:
        entry_dict = dict(entry)
        
        # Check against 'name' column
        db_name = entry_dict.get('name')
        if db_name:
            normalized_db_name = db_name.lower().replace('\xa0', ' ').replace('\u202f', ' ').strip()
            if normalized_search_term == normalized_db_name:
                result_id = entry_dict['id']
                logging.debug(f"get_lookup_id_by_name: SUCCESS! Found ID={result_id} for table='{table_name}' by 'name' matching '{name_stripped}' (normalized: '{normalized_search_term}')")
                break
        
        # Check against 'name_ar' column if it exists
        if result_id is None and has_name_ar:
            db_name_ar = entry_dict.get('name_ar')
            if db_name_ar:
                normalized_db_name_ar = db_name_ar.lower().replace('\xa0', ' ').replace('\u202f', ' ').strip()
                if normalized_search_term == normalized_db_name_ar:
                    result_id = entry_dict['id']
                    logging.debug(f"get_lookup_id_by_name: SUCCESS! Found ID={result_id} for table='{table_name}' by 'name_ar' matching '{name_stripped}' (normalized: '{normalized_search_term}')")
                    break

        # Check against 'api_name' column if it exists
        if result_id is None and has_api_name:
            db_api_name = entry_dict.get('api_name')
            if db_api_name:
                normalized_db_api_name = db_api_name.lower().replace('\xa0', ' ').replace('\u202f', ' ').strip()
                if normalized_search_term == normalized_db_api_name:
                    result_id = entry_dict['id']
                    logging.debug(f"get_lookup_id_by_name: SUCCESS! Found ID={result_id} for table='{table_name}' by 'api_name' matching '{name_stripped}' (normalized: '{normalized_search_term}')")
                    break
    
    if result_id is None:
        logging.debug(f"get_lookup_id_by_name: FAILED! No ID found for table='{table_name}', name='{name_stripped}' (normalized: '{normalized_search_term}')")
        logging.debug(f"get_lookup_id_by_name: All entries in '{table_name}': {[dict(row) for row in all_entries]}")
        
    conn.close()
    return result_id

def get_generation_tasks_by_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM generation_tasks WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    
    tasks_with_file_info = []
    for task_row in tasks:
        task = dict(task_row)
        task['uploaded_file_name'] = "No uploaded files within this task." # Default message
        task['generated_question_ids'] = [] # Initialize new field

        # Fetch generated question IDs for this task
        question_conn = get_db_connection()
        question_cursor = question_conn.cursor()
        query_sql = "SELECT question_id FROM questions WHERE task_id = ?"
        logging.debug(f"get_generation_tasks_by_user - Executing query: '{query_sql}' with task_id: {task['task_id']}")
        question_cursor.execute(query_sql, (task['task_id'],))
        generated_question_ids = [int(row['question_id']) for row in question_cursor.fetchall()]
        question_conn.close()
        task['generated_question_ids'] = generated_question_ids
        logging.debug(f"get_generation_tasks_by_user - Task {task['task_id']} has generated questions: {generated_question_ids}")
        logging.debug(f"get_generation_tasks_by_user - Raw query result for task {task['task_id']}: {generated_question_ids}")

        logging.debug(f"get_generation_tasks_by_user - Processing task_id: {task['task_id']}")
        logging.debug(f"get_generation_tasks_by_user - Raw request_parameters: {task['request_parameters']}")

        if task['request_parameters']:
            try:
                request_params = json.loads(task['request_parameters'])
                logging.debug(f"get_generation_tasks_by_user - Parsed request_params: {request_params}")
                uploaded_file_id = request_params.get('uploaded_file_id')
                logging.debug(f"get_generation_tasks_by_user - Extracted uploaded_file_id: {uploaded_file_id}")
                
                if uploaded_file_id:
                    file_conn = get_db_connection()
                    file_cursor = file_conn.cursor()
                    file_cursor.execute("SELECT file_name FROM uploaded_files WHERE id = ?", (uploaded_file_id,))
                    file_result = file_cursor.fetchone()
                    file_conn.close()

                    if file_result:
                        task['uploaded_file_name'] = file_result['file_name']
                        logging.debug(f"get_generation_tasks_by_user - Fetched file_name: {task['uploaded_file_name']}")
                    else:
                        task['uploaded_file_name'] = f"Uploaded file (ID: {uploaded_file_id}) not found."
                        logging.debug(f"get_generation_tasks_by_user - File not found for ID: {uploaded_file_id}")
            except json.JSONDecodeError:
                logging.warning(f"Could not decode request_parameters for task_id {task['task_id']}")
            except Exception as e:
                logging.error(f"Error processing uploaded_file_id for task_id {task['task_id']}: {e}")
        tasks_with_file_info.append(task)
    return tasks_with_file_info


def insert_question(question_data: dict, task_id: Optional[int] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None, hide_answers: Optional[bool] = False) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()

    logging.debug(f"insert_question called with: question_data={question_data.get('question_text')[:50]}..., task_id={task_id}, user_id={user_id}, tenant_id={tenant_id}, hide_answers={hide_answers}")
    logging.debug(f"insert_question - Received task_id for insertion: {task_id}")

    # Normalize incoming data to a plain dict to avoid attribute errors
    try:
        import sqlite3 as _sqlite3
        if isinstance(question_data, _sqlite3.Row):
            question_data = {k: question_data[k] for k in question_data.keys()}
    except Exception:
        pass
    if not isinstance(question_data, dict):
        try:
            question_data = dict(question_data)
        except Exception:
            # Fallback: reflect common attributes
            question_data = {k: getattr(question_data, k) for k in dir(question_data) if not k.startswith('_')}

    # Safe getter that does not rely on dict.get semantics for non-dict inputs
    def g(key: str, default=None):
        try:
            return question_data[key] if key in question_data else default
        except Exception:
            return default

    # Build a clean, flat dict with only fields we actually use downstream.
    clean = {
        'author_creator': g('author_creator', 'System'),
        'date_created': g('date_created', datetime.datetime.now().isoformat()),
        'question_text': g('question_text', ''),
        'choice_1': g('choice_1'),
        'choice_2': g('choice_2'),
        'choice_3': g('choice_3'),
        'choice_4': g('choice_4'),
        'correct_option': g('correct_option'),
        'difficulty_level': g('difficulty_level'),
        'cognitive_level': g('cognitive_level'),
        'learning_outcome': g('learning_outcome'),
        'question_type': g('question_type'),
        'mark': g('mark', 0),
        'time_seconds': g('time_seconds', 0),
        'discriminating_factor': g('discriminating_factor'),
        'status': g('status', 'pending'),
        'school_type': g('school_type'),
        'subject': g('subject'),
        'year': g('year'),
        'major': g('major'),
        'course': g('course'),
        'material': g('material'),
        'semester': g('semester'),
        'company': g('company'),
        'department': g('department'),
        'job_role': g('job_role'),
        'audience_type': g('audience_type'),
        'variables': g('variables'),
        'solution': g('solution'),
        'hide_answers': hide_answers,
    }

    # Coerce types and enforce NOT NULL defaults for constrained fields
    try:
        clean['mark'] = int(clean['mark']) if clean['mark'] is not None else 0
    except Exception:
        clean['mark'] = 0
    try:
        clean['time_seconds'] = int(clean['time_seconds']) if clean['time_seconds'] is not None else 0
    except Exception:
        clean['time_seconds'] = 0
    if isinstance(clean['date_created'], datetime.date):
        clean['date_created'] = str(clean['date_created'])
    if clean['date_created'] is None:
        clean['date_created'] = datetime.datetime.now().isoformat()
    if clean['status'] is None:
        clean['status'] = 'pending'

    # Get IDs for lookup tables using safe accessor
    difficulty_id = get_lookup_id_by_name('difficulty_levels', clean['difficulty_level'])
    cognitive_id = get_lookup_id_by_name('cognitive_levels', clean['cognitive_level'])
    learning_outcome_id = get_lookup_id_by_name('learning_outcomes', clean['learning_outcome'])
    question_type_id = get_lookup_id_by_name('question_types', clean['question_type'])

    school_type_id = get_lookup_id_by_name('school_types', clean['school_type'])
    subject_id = get_lookup_id_by_name('school_subjects', clean['subject'])
    year_id = get_lookup_id_by_name('school_years', clean['year'])
    major_id = get_lookup_id_by_name('university_majors', clean['major'])
    course_id = get_lookup_id_by_name('university_courses', clean['course']) # Assuming university_courses table exists
    material_id = get_lookup_id_by_name('university_materials', clean['material']) # Assuming university_materials table exists
    semester_id = get_lookup_id_by_name('university_semesters', clean['semester']) # Assuming university_semesters table exists
    company_id = get_lookup_id_by_name('companies', clean['company'])
    department_id = get_lookup_id_by_name('departments', clean['department'])
    job_role_id = get_lookup_id_by_name('job_roles', clean['job_role'])

    # If a lookup value is not found, set its ID to None (NULL in DB) instead of raising an error
    # This assumes these fields are nullable in the questions table schema.
    # The frontend should ensure required fields are selected.

    columns = [
        'author_creator', 'date_created', 'question_text', 
        'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_option',
        'difficulty_level_id', 'cognitive_level_id', 'learning_outcome_id', 'question_type_id',
        'mark', 'time_seconds', 'discriminating_factor', 'status',
        'school_type_id', 'subject_id', 'year_id', 'major_id', 'course_id', 'material_id', 'semester_id',
        'company_id', 'department_id', 'job_role_id',
        'audience_type', 'solution', 'hide_answers', 'task_id', 'user_id', 'tenant_id'
    ]
    values = [
        clean['author_creator'],
        clean['date_created'],
        clean['question_text'],
        clean['choice_1'],
        clean['choice_2'],
        clean['choice_3'],
        clean['choice_4'],
        clean['correct_option'],
        difficulty_id,
        cognitive_id,
        learning_outcome_id,
        question_type_id,
        clean['mark'],
        clean['time_seconds'],
        clean['discriminating_factor'],
        clean['status'],
        school_type_id,
        subject_id,
        year_id,
        major_id,
        course_id,
        material_id,
        semester_id,
        company_id,
        department_id,
        job_role_id,
        clean['audience_type'],
        clean['solution'],
        clean['hide_answers'],
        task_id,
        user_id,
        tenant_id
    ]

    placeholders = ', '.join(['?'] * len(columns))
    sql = f"INSERT INTO questions ({', '.join(columns)}) VALUES ({placeholders})"
    
    cursor.execute(sql, tuple(values))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_audience_fields(audience_type: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT field_name, is_enabled FROM audience_field_config WHERE audience_type = ?", (audience_type,))
    fields = {row['field_name']: bool(row['is_enabled']) for row in cursor.fetchall()}
    conn.close()
    return fields

def get_property_types_by_audience(audience_type: str, lang: Optional[str] = None, tenant_id: Optional[int] = None, user_id: Optional[int] = None):
    # This function will now query the property_types table, filtered by audience_type, tenant_id and user_id
    # The direct SQL query is replaced by a call to the more generic get_lookup_data_list

    # We pass the audience_type to filter by. tenant_id and user_id are also passed for specific filtering.
    return get_lookup_data_list("property_types", lang=lang, audience_type=audience_type, tenant_id=tenant_id, user_id=user_id)
def create_property_type(name: str, api_name: str, audience_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO property_types (name, api_name, audience_type) VALUES (?, ?, ?)",
        (name, api_name, audience_type)
    )
    conn.commit()
    new_id = cursor.lastrowid
    # Dynamically create the table for this new property type
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {api_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()
    return new_id

def get_property_type_by_api_name(api_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM property_types WHERE api_name = ?", (api_name,))
    property_type = cursor.fetchone()
    conn.close()
    return dict(property_type) if property_type else None

def delete_property_type(api_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use a transaction to ensure both operations succeed or fail together
    try:
        cursor.execute("BEGIN TRANSACTION")
        # Delete from the property_types table
        cursor.execute("DELETE FROM property_types WHERE api_name = ?", (api_name,))
        # Drop the associated lookup table
        cursor.execute(f"DROP TABLE IF EXISTS {api_name}")
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    finally:
        conn.close()

def update_audience_fields(audience_type: str, fields: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    for field_name, is_enabled in fields.items():
        # Use INSERT OR REPLACE to handle both new and existing fields
        cursor.execute("""
            INSERT INTO audience_field_config (audience_type, field_name, is_enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(audience_type, field_name) DO UPDATE SET is_enabled = excluded.is_enabled;
        """, (audience_type, field_name, is_enabled))
    conn.commit()
    conn.close()

import json

def update_question(question_id: int, question_data: dict, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []

    for key, value in question_data.items():
        # Ensure we don't try to update the primary key
        if key == 'question_id':
            continue

        if key == 'variables':
            update_fields.append('variables = ?')
            update_values.append(json.dumps(value))
            continue
        # Handle lookup fields and status field
        if key in ['difficulty_level', 'cognitive_level', 'learning_outcome', 'question_type',
                   'school_type', 'subject', 'year', 'major', 'course', 'material', 'semester',
                   'company', 'department', 'job_role']:
            lookup_table = f"{key}s"
            # Special handling for 'year' to map to 'school_years'
            if key == 'year':
                lookup_table = 'school_years'
            # Special handling for 'question_type' to map to 'question_types'
            if key == 'question_type':
                lookup_table = 'question_types'

            lookup_id = None
            if value is not None and value != '': # Only try to get ID if value is not None or empty
                lookup_id = get_lookup_id_by_name(lookup_table, value)
            
            
            if value is not None and value != '': # A string value was provided by the frontend
                lookup_id = get_lookup_id_by_name(lookup_table, value)
                update_fields.append(f"{key}_id = ?")
                update_values.append(lookup_id) # Will be the ID or None if lookup failed
            elif value is None or value == '': # A clear/null value was provided by the frontend
                update_fields.append(f"{key}_id = ?")
                update_values.append(None) # Explicitly set to NULL
            else:
                raise ValueError(f"Invalid value for {key}: {value}")
        elif key == 'status':
            update_fields.append(f"status = ?")
            update_values.append(value)
        else:
            update_fields.append(f"{key} = ?")
            update_values.append(value)

    if not update_fields:
        logging.debug(f"update_question: No fields to update for question_id {question_id}")
        return

    # If actor provided, stamp edit metadata
    if actor_user_id is not None:
        update_fields.append('edited_by = ?')
        update_values.append(actor_user_id)
        update_fields.append('edited_at = ?')
        update_values.append(datetime.datetime.utcnow().isoformat())

    sql_query = f"UPDATE questions SET {', '.join(update_fields)} WHERE question_id = ?"
    update_values.append(question_id)

    logging.debug(f"update_question SQL Query: {sql_query}")
    logging.debug(f"update_question Parameters: {update_values}")
    cursor.execute(sql_query, tuple(update_values))
    conn.commit()
    logging.debug(f"update_question: Commit successful for question_id {question_id}")
    # Log action if context available
    if actor_user_id is not None and tenant_id is not None:
        try:
            log_question_action_raw(question_id, tenant_id, actor_user_id, 'edited', {"fields": list(question_data.keys())})
        except Exception as e:
            logging.warning("failed to log edited action:", e)
    conn.close()

def get_question_by_id(question_id: int, include_correct_answer: bool = False, tenant_id: Optional[int] = None, audience_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    params = [question_id]
    where_clauses = ["q.question_id = ?"]

    if tenant_id is not None:
        where_clauses.append("q.tenant_id = ?")
        params.append(tenant_id)
    
    if audience_type is not None:
        where_clauses.append("q.audience_type = ?")
        params.append(audience_type)

    sql_query = f"""SELECT 
        q.question_id, q.author_creator, q.date_created, q.question_text,
        q.choice_1, q.choice_2, q.choice_3, q.choice_4, 
        CASE WHEN {1 if include_correct_answer else 0} THEN q.correct_option ELSE NULL END as correct_option,
        dl.name as difficulty_level, cl.name as cognitive_level, lo.name as learning_outcome,
        qt.api_name as question_type,
        st.name as school_type, ss.name as subject, sy.name as year,
        um.name as major, uc.name as course, umt.name as material, us.name as semester,
        comp.name as company, dep.name as department, jr.name as job_role,
        q.mark, q.time_seconds, q.discriminating_factor, q.status, q.audience_type, q.variables, q.solution,
        q.hide_answers as answers_hidden
        FROM questions q
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN school_types st ON q.school_type_id = st.id
        LEFT JOIN school_subjects ss ON q.subject_id = ss.id
        LEFT JOIN school_years sy ON q.year_id = sy.id
        LEFT JOIN university_majors um ON q.major_id = um.id
        LEFT JOIN university_courses uc ON q.course_id = uc.id
        LEFT JOIN university_materials umt ON q.material_id = umt.id
        LEFT JOIN university_semesters us ON q.semester_id = us.id
        LEFT JOIN companies comp ON q.company_id = comp.id
        LEFT JOIN departments dep ON q.department_id = dep.id
        LEFT JOIN job_roles jr ON q.job_role_id = jr.id
        WHERE {" AND ".join(where_clauses)}
    """
    logging.debug(f"get_question_by_id SQL Query: {sql_query}")
    logging.debug(f"get_question_by_id Parameters: {params}")
    cursor.execute(sql_query, tuple(params))
    question = cursor.fetchone()
    logging.debug(f"get_question_by_id Result: {question}")
    conn.close()
    if question:
        question_dict = dict(question)
        if question_dict.get('variables'):
            question_dict['variables'] = json.loads(question_dict['variables'])
        return question_dict
    return None

def delete_question(question_id: int, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    logging.debug(f"Attempting to delete question with ID: {question_id}")
    try:
        if actor_user_id is not None and tenant_id is not None:
            try:
                cursor.execute("UPDATE questions SET deleted_by = ?, deleted_at = ? WHERE question_id = ?", (actor_user_id, datetime.datetime.utcnow().isoformat(), question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'deleted', None)
            except Exception as e:
                logging.warning("failed to stamp delete metadata:", e)
        cursor.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))
        conn.commit()
        logging.debug(f"Successfully deleted question with ID: {question_id}")
    except Exception as e:
        logging.error(f"Failed to delete question with ID {question_id}: {e}")
        conn.rollback() # Rollback in case of error
    finally:
        conn.close()

def delete_multiple_questions(question_ids: List[int], tenant_id: Optional[int] = None):
    if not question_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in question_ids])
    try:
        if tenant_id is None:
            cursor.execute(f"DELETE FROM questions WHERE question_id IN ({placeholders})", tuple(question_ids))
        else:
            cursor.execute(f"DELETE FROM questions WHERE question_id IN ({placeholders}) AND tenant_id = ?", tuple(question_ids + [tenant_id]))
        conn.commit()
        logging.debug(f"Successfully deleted questions with IDs: {question_ids}")
    except Exception as e:
        logging.error(f"Failed to delete questions with IDs {question_ids}: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_question_status(question_id: int, status: str, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    import time
    t0 = time.perf_counter()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE questions SET status = ? WHERE question_id = ?", (status, question_id))
    if actor_user_id is not None and tenant_id is not None:
        try:
            now = datetime.datetime.utcnow().isoformat()
            if status.lower() == 'approved':
                cursor.execute("UPDATE questions SET approved_by = ?, approved_at = ? WHERE question_id = ?", (actor_user_id, now, question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'approved', None)
            elif status.lower() == 'rejected':
                cursor.execute("UPDATE questions SET rejected_by = ?, rejected_at = ? WHERE question_id = ?", (actor_user_id, now, question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'rejected', None)
        except Exception as e:
            logging.warning("failed to stamp status metadata:", e)
    conn.commit()
    t1 = time.perf_counter()
    logging.info(f"TIMING: update_question_status took {int((t1 - t0)*1000)} ms (status={status})")
    conn.close()

def log_question_action_raw(question_id: int, tenant_id: int, actor_user_id: int, action: str, details: Optional[Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    details_str = None
    if details is not None:
        details_str = json.dumps(details) if not isinstance(details, str) else details
    try:
        cur.execute(
            "INSERT INTO question_actions (question_id, tenant_id, action, actor_user_id, details) VALUES (?,?,?,?,?)",
            (question_id, tenant_id, action, actor_user_id, details_str)
        )
        conn.commit()
    except Exception as e:
        logging.warning("failed to log question action:", e)
    finally:
        conn.close()

def get_question_history(question_id: int, tenant_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT action, actor_user_id, details, created_at FROM question_actions WHERE question_id = ? AND tenant_id = ? ORDER BY created_at ASC", (question_id, tenant_id))
    rows = cur.fetchall()
    conn.close()
    # return as list of dicts
    result = []
    for r in rows:
        details = r[2]
        try:
            details = json.loads(details) if details else None
        except Exception:
            pass
        result.append({"action": r[0], "actor_user_id": r[1], "details": details, "created_at": r[3]})
    return result

def update_generation_task_status(task_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE generation_tasks SET status = ? WHERE task_id = ?", (status, task_id))
    conn.commit()
    conn.close()

def update_generation_task_generated_count(task_id: int, count: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE generation_tasks SET num_questions_generated = ? WHERE task_id = ?", (count, task_id))
    conn.commit()
    conn.close()



def get_generation_model_by_id(model_id: int, tenant_id: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute("SELECT * FROM generation_models WHERE id = ?", (model_id,))
    else:
        cursor.execute("SELECT * FROM generation_models WHERE id = ? AND tenant_id = ?", (model_id, tenant_id))
    model = cursor.fetchone()
    conn.close()
    return model

def get_generation_model_by_api_name(model_api_name: str, tenant_id: int | None):
    logging.debug(f"get_generation_model_by_api_name called with model_api_name={model_api_name}, tenant_id={tenant_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute(
            "SELECT * FROM generation_models WHERE model_api_name = ? AND is_active = 1 ORDER BY is_default DESC LIMIT 1",
            (model_api_name,)
        )
    else:
        cursor.execute(
            "SELECT * FROM generation_models WHERE model_api_name = ? AND (tenant_id = ? OR tenant_id IS NULL) AND is_active = 1 ORDER BY CASE WHEN tenant_id = ? THEN 0 ELSE 1 END, is_default DESC LIMIT 1",
            (model_api_name, tenant_id, tenant_id)
        )
    model = cursor.fetchone()
    conn.close()
    logging.debug(f"get_generation_model_by_api_name returning model: {model}")
    return model

def get_generation_models_by_method(generation_method: str, tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM generation_models WHERE generation_method = ? AND tenant_id = ? AND is_active = 1",
        (generation_method, tenant_id)
    )
    models = cursor.fetchall()
    conn.close()
    return [dict(model) for model in models]

def get_all_generation_models(tenant_id: int | None = None, skip: int = 0, limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query_base = ""
    params = []
    count_params = []
    
    if tenant_id is None:
        sql_query_base = (
            "SELECT * FROM generation_models WHERE is_active = 1"
        )
        # Simplified order by for the global case
        sql_query_ordered = sql_query_base + " ORDER BY is_default DESC, model_name ASC LIMIT ? OFFSET ?"
        params = [limit, skip]
    else:
        sql_query_base = (
            "SELECT * FROM generation_models WHERE (tenant_id = ? OR tenant_id IS NULL) AND is_active = 1"
        )
        # Order by tenant-specific first, then default, then name
        sql_query_ordered = sql_query_base + " ORDER BY CASE WHEN tenant_id = ? THEN 0 ELSE 1 END, is_default DESC, model_name ASC LIMIT ? OFFSET ?"
        params = [tenant_id, tenant_id, limit, skip]
        count_params = [tenant_id]

    # Get total count
    count_query = f"SELECT COUNT(*) FROM ({sql_query_base}) AS subquery"
    cursor.execute(count_query, tuple(count_params))
    total_count = cursor.fetchone()[0]

    logging.debug(f"get_all_generation_models SQL Query: {sql_query_ordered}")
    logging.debug(f"get_all_generation_models Parameters: {params}")
    cursor.execute(sql_query_ordered, tuple(params))
    models = cursor.fetchall()
    conn.close()
    logging.debug(f"get_all_generation_models fetched models: {models}")
    
    # Deduplicate models by model_name, giving priority to the first one found (which will be the tenant-specific one if it exists)
    unique_models = {}
    for model in models:
        model_dict = dict(model)
        if model_dict['model_name'] not in unique_models:
            unique_models[model_dict['model_name']] = model_dict
            
    return total_count, list(unique_models.values())

def update_generation_model(model_id: int, tenant_id: int, model_name: str, model_api_name: str, generation_method: str, is_default: bool, is_active: bool, api_key: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE generation_models
           SET model_name = ?, model_api_name = ?, generation_method = ?, is_default = ?, is_active = ?, api_key = ?
           WHERE id = ? AND tenant_id = ?""",
        (model_name, model_api_name, generation_method, is_default, is_active, api_key, model_id, tenant_id)
    )
    conn.commit()
    conn.close()

def delete_generation_model(model_id: int, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute("DELETE FROM generation_models WHERE id = ?", (model_id,))
    else:
        cursor.execute("DELETE FROM generation_models WHERE id = ? AND tenant_id = ?", (model_id, tenant_id))
    conn.commit()
    conn.close()

def get_all_billing_products(tenant_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT * FROM billing_products WHERE 1=1"
    params = []

    if is_active is not None:
        sql_query += " AND is_active = ?"
        params.append(1 if is_active else 0)
    
    if tenant_id is not None:
        sql_query += " AND (tenant_id IS NULL OR tenant_id = ?)"
        params.append(tenant_id)
    else:
        # If no tenant_id is provided, only return global products (tenant_id IS NULL)
        sql_query += " AND tenant_id IS NULL"

    cursor.execute(sql_query, params)
    products = cursor.fetchall()
    
    product_list = []
    for product in products:
        product_dict = dict(product)
        
        # Calculate sold_count
        cursor.execute("SELECT COUNT(*) FROM billing_events WHERE product_id = ?", (product_dict['id'],))
        sold_count = cursor.fetchone()[0]
        product_dict['sold_count'] = sold_count
        
        product_list.append(product_dict)

    conn.close()
    return product_list

def get_all_billing_events(
    tenant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    country: Optional[str] = None,
    agent_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT
            be.id,
            bp.name AS product_name,
            t.name AS agent_name,
            c.name AS country,
            u.username,
            be.created_at,
            be.total_price_cents,
            be.currency
        FROM billing_events be
        LEFT JOIN billing_products bp ON be.product_id = bp.id
        LEFT JOIN tenants t ON be.tenant_id = t.id
        LEFT JOIN users u ON be.user_id = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
    """

    where_clauses = ["be.event_type = 'credit'"]
    params = []

    if tenant_id is not None:
        where_clauses.append("be.tenant_id = ?")
        params.append(tenant_id)

    if country:
        where_clauses.append("c.name = ?")
        params.append(country)

    if agent_id is not None:
        where_clauses.append("t.id = ?")
        params.append(agent_id)

    if start_date:
        where_clauses.append("date(be.created_at) >= date(?)")
        params.append(start_date)

    if end_date:
        where_clauses.append("date(be.created_at) <= date(?)")
        params.append(end_date)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Get total count first
    count_query = f"SELECT COUNT(DISTINCT be.id) FROM billing_events be LEFT JOIN billing_products bp ON be.product_id = bp.id LEFT JOIN tenants t ON be.tenant_id = t.id LEFT JOIN users u ON be.user_id = u.id LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id LEFT JOIN countries c ON tc.country_id = c.country_id"
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)

    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Get paginated billing events
    final_query = base_query + " ORDER BY be.created_at DESC LIMIT ? OFFSET ?"
    final_params = params + [limit, skip]

    cursor.execute(final_query, final_params)
    billing_events = cursor.fetchall()
    logging.debug(f"get_all_billing_events returning total_count={total_count}, billing_events_count={len(billing_events)}")
    conn.close()
    return total_count, [dict(event) for event in billing_events]

def get_tenant_hierarchy(tenant_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        WITH RECURSIVE tenant_hierarchy (id) AS (
            SELECT id FROM tenants WHERE id = ?
            UNION ALL
            SELECT t.id
            FROM tenants t
            JOIN tenant_hierarchy th ON t.parent_id = th.id
        )
        SELECT t.id, t.name, t.created_at, u.username as created_by_username, t.created_by as created_by_id, c.name as country, u.mobile_phone as admin_mobile_phone
        FROM tenants t
        LEFT JOIN users u ON t.created_by = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        WHERE t.id IN (SELECT id FROM tenant_hierarchy)
        ORDER BY t.name;
    """
    cursor.execute(sql, (tenant_id,))
    tenants_rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in tenants_rows]

# Example usage (for testing purposes)
if __name__ == "__main__":
    logging.info("Difficulty Levels:", get_lookup_data_list('difficulty_levels'))
    logging.info("Cognitive Levels:", get_lookup_data_list('cognitive_levels'))
    logging.info("Learning Outcomes:", get_lookup_data_list('learning_outcomes'))

    # Example of inserting a question
    try:
        new_question_data = {
            "question_text": "What is the capital of Canada?",
            "choice_1": "Toronto",
            "choice_2": "Ottawa",
            "choice_3": "Vancouver",
            "choice_4": "Montreal",
            "correct_option": "Ottawa",
            "difficulty_level": "Easy",
            "cognitive_level": "Remembering",
            "learning_outcome": "Identify basic facts",
            "author_creator": "Test User",
            "mark": 1,
            "time_seconds": 30,
            "discriminating_factor": 0.5
        }
        inserted_id = insert_question(new_question_data)
        logging.info(f"Inserted new question with ID: {inserted_id}")
    except ValueError as e:
        logging.error(f"Error inserting question: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error during insert: {e}")

def get_user_specific_audience_items(user_id: int, audience_type: str, field_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"user_{field_name}s"
    logging.debug(f"get_user_specific_audience_items - Attempting to query table: {table_name} for user_id: {user_id}")
    # Basic validation to prevent SQL injection for table_name
    if not table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        logging.error(f"get_user_specific_audience_items - Invalid field_name: {field_name}")
        raise ValueError("Invalid field_name")
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE user_id = ?", (user_id,))
        items = cursor.fetchall()
        logging.debug(f"get_user_specific_audience_items - Successfully queried {table_name}. Items found: {len(items)}")
        conn.close()
        return [dict(item) for item in items]
    except sqlite3.OperationalError as e:
        logging.error(f"get_user_specific_audience_items - sqlite3.OperationalError: {e} for table: {table_name}")
        raise e
    except Exception as e:
        logging.error(f"get_user_specific_audience_items - An unexpected error occurred: {e} for table: {table_name}")
        raise e

def add_user_specific_audience_item(user_id: int, audience_type: str, field_name: str, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Add to user-specific preferences table
    user_table_name = f"user_{field_name}s"
    # Basic validation to prevent SQL injection
    if not user_table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        conn.close()
        raise ValueError("Invalid field_name")
    
    try:
        cursor.execute(f"INSERT INTO {user_table_name} (user_id, name) VALUES (?, ?)", (user_id, name))
        item_id = cursor.lastrowid

        # 2. Add to global lookup table if it's a known lookup field
        lookup_table_mapping = {
            "school_type": "school_types",
            "subject": "school_subjects",
            "year": "school_years",
            "major": "university_majors",
            "course": "university_courses",
            "material": "university_materials",
            "semester": "university_semesters",
            "company": "companies",
            "department": "departments",
            "job_role": "job_roles",
            "difficulty_level": "difficulty_levels",
            "cognitive_level": "cognitive_levels",
            "learning_outcome": "learning_outcomes",
            "question_type": "question_types"
        }

        if field_name in lookup_table_mapping:
            lookup_table = lookup_table_mapping[field_name]
            
            # Check if it already exists in the global table (case-insensitive for safety)
            cursor.execute(f"SELECT id FROM {lookup_table} WHERE LOWER(name) = LOWER(?)", (name,))
            if not cursor.fetchone():
                # Get user info for tenant_id and created_by
                cursor.execute("SELECT tenant_id FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                tenant_id = user_row['tenant_id'] if user_row else None
                
                # Check for audience_type and tenant_id columns
                cursor.execute(f"PRAGMA table_info({lookup_table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                insert_cols = ["name"]
                insert_vals = [name]
                
                if "audience_type" in columns:
                    insert_cols.append("audience_type")
                    insert_vals.append(audience_type)
                if "tenant_id" in columns:
                    insert_cols.append("tenant_id")
                    insert_vals.append(tenant_id)
                if "created_by" in columns:
                    insert_cols.append("created_by")
                    insert_vals.append(user_id)
                    
                placeholders = ", ".join(["?"] * len(insert_vals))
                cursor.execute(f"INSERT INTO {lookup_table} ({', '.join(insert_cols)}) VALUES ({placeholders})", tuple(insert_vals))

        conn.commit()
        return item_id
    except sqlite3.Error as e:
        logging.error(f"Database error in add_user_specific_audience_item: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_user_specific_audience_item(user_id: int, audience_type: str, field_name: str, item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"user_{field_name}s"
    # Basic validation to prevent SQL injection for table_name
    if not table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        raise ValueError("Invalid field_name")
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

def get_unbanked_questions_for_user(current_user: dict, selected_question_ids: Optional[List[int]] = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()

    is_admin = current_user.get("is_admin", False)
    is_super_admin = current_user.get("is_super_admin", False)
    user_id = current_user.get("id")
    tenant_id = current_user.get("tenant_id")

    params = []
    # Super admin can access any question from any tenant
    base_query = """
        SELECT q.*, 
               lo.name as learning_outcome,
               dl.name as difficulty_level,
               cl.name as cognitive_level,
               qt.name as question_type_name,
               qt.api_name as question_type
        FROM questions q
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
    """
    
    if is_super_admin:
        query = base_query
    # Admin can access any question from their tenant
    elif is_admin:
        query = base_query + " WHERE q.tenant_id = ?"
        params.append(tenant_id)
    # Regular user can only access their own questions
    else:
        query = base_query + " WHERE q.user_id = ?"
        params.append(user_id)

    if selected_question_ids:
        placeholders = ','.join('?' for _ in selected_question_ids)
        # Check if WHERE clause was already added
        if 'WHERE' in query:
            query += f" AND q.question_id IN ({placeholders})"
        else:
            query += f" WHERE q.question_id IN ({placeholders})"
        params.extend(selected_question_ids)
    else:
        # If no IDs are selected, revert to old behavior of getting unbanked questions
        if 'WHERE' in query:
            query += " AND q.tamsqb_bank_added = 0"
        else:
             query += " WHERE q.tamsqb_bank_added = 0"

    cursor.execute(query, tuple(params))
    questions = cursor.fetchall()
    conn.close()
    return [dict(q) for q in questions]

def update_question_tamsqb_bank_added_status(question_id: int, status: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE questions SET tamsqb_bank_added = ? WHERE question_id = ?", (status, question_id))
    conn.commit()
    conn.close()

def insert_uploaded_file(user_id: int, tenant_id: int, file_name: str, file_path: str, file_type: str, extracted_content: Optional[str], task_id: Optional[int] = None, file_hash: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    upload_timestamp = datetime.datetime.now().isoformat()
    logging.debug(f"insert_uploaded_file - Inserting file_name: {file_name}, extracted_content length: {len(extracted_content) if extracted_content else 0}, file_hash: {file_hash}")
    cursor.execute(
        """INSERT INTO uploaded_files (user_id, tenant_id, file_name, file_path, file_type, upload_timestamp, extracted_content, task_id, file_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, tenant_id, file_name, file_path, file_type, upload_timestamp, extracted_content, task_id, file_hash)
    )
    conn.commit()
    file_id = cursor.lastrowid
    logging.debug(f"insert_uploaded_file - File inserted with ID: {file_id}")
    conn.close()
    return file_id

def get_uploaded_file_by_hash(file_hash: str) -> Optional[dict]:
    """Retrieves an existing upload record by its MD5 hash to reuse extracted content."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Find the most recent successful extraction for this hash
    cursor.execute(
        "SELECT id, file_name, extracted_content FROM uploaded_files WHERE file_hash = ? AND extracted_content IS NOT NULL AND extracted_content != '' ORDER BY id DESC LIMIT 1",
        (file_hash,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_uploaded_file_content(file_id: int) -> Optional[str]:
    logging.debug(f"get_uploaded_file_content - Retrieving content for file_id: {file_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT extracted_content FROM uploaded_files WHERE id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result['extracted_content']:
        logging.debug(f"get_uploaded_file_content - Retrieved content length: {len(result['extracted_content'])}")
    else:
        logging.debug(f"get_uploaded_file_content - No content or empty content found for file_id: {file_id}")
    return result['extracted_content'] if result else None

def update_uploaded_file_task_id(file_id: int, task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE uploaded_files SET task_id = ? WHERE id = ?", (task_id, file_id))
    conn.commit()
    conn.close()


def insert_exam(online_exam_id: int, user_id: int, exam_name: str, exam_date_time: str, duration_minutes: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO exams (online_exam_id, user_id, exam_name, exam_date_time, duration_minutes, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (online_exam_id, user_id, exam_name, exam_date_time, duration_minutes, created_at)
    )
    conn.commit()
    exam_id = cursor.lastrowid
    conn.close()
    return exam_id

def link_question_to_exam(exam_id: int, question_id: int, bank_question_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO exam_questions (exam_id, question_id, bank_question_id) VALUES (?, ?, ?)",
        (exam_id, question_id, bank_question_id)
    )
    conn.commit()
    conn.close()
    
def get_finished_exams_for_user(user_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    # This query is a bit complex for SQLite string manipulation. It is better to do the logic in python.
    cursor.execute("SELECT * FROM exams WHERE user_id = ?", (user_id,))
    exams = cursor.fetchall()
    conn.close()

    finished_exams = []
    for exam in exams:
        exam_dict = dict(exam)
        # It's safer to parse the datetime string and handle potential errors
        try:
            exam_start_time = datetime.datetime.strptime(exam_dict['exam_date_time'], "%Y-%m-%d %H:%M:%S")
            duration = datetime.timedelta(minutes=int(exam_dict['duration_minutes']))
            exam_end_time = exam_start_time + duration
            now = datetime.datetime.now()
            logging.debug(f"Checking exam '{exam_dict['exam_name']}'. Start: {exam_start_time}, End: {exam_end_time}, Now: {now}")
            if now > exam_end_time:
                logging.debug(f"Exam '{exam_dict['exam_name']}' is finished.")
                finished_exams.append(exam_dict)
        except (ValueError, TypeError) as e:
            # Log an error if the date format is incorrect or types are wrong
            logging.error(f"Could not process exam id {exam_dict.get('id')}. Value was {exam_dict.get('exam_date_time')}, duration was {exam_dict.get('duration_minutes')}. Error: {e}")
            continue
            
    return finished_exams
    
def delete_exam_report(exam_id: int, user_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Verify exam ownership and get report_image_path
        cursor.execute("SELECT user_id, report_image_path FROM exams WHERE id = ?", (exam_id,))
        exam_row = cursor.fetchone()
        if not exam_row:
            logging.warning(f"Attempted to delete report for non-existent exam ID: {exam_id}")
            return False
        if exam_row['user_id'] != user_id:
            logging.warning(f"Unauthorized attempt to delete report for exam ID: {exam_id} by user ID: {user_id}")
            return False

        report_image_path = exam_row['report_image_path']

        # 2. Delete the actual report image file if it exists
        if report_image_path and os.path.exists(report_image_path):
            try:
                os.remove(report_image_path)
                logging.info(f"Successfully deleted report image file: {report_image_path}")
            except OSError as e:
                logging.error(f"Error deleting report image file {report_image_path}: {e}")
                # Continue to update DB even if file deletion fails

        # 3. Clear the report_image_path in the exams table
        cursor.execute("UPDATE exams SET report_image_path = NULL WHERE id = ?", (exam_id,))
        conn.commit()
        logging.info(f"Cleared report_image_path for exam ID: {exam_id}")
        return True
    except Exception as e:
        logging.error(f"Error deleting exam report for exam ID {exam_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
def get_question_ids_for_exam(exam_id: int) -> List[int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question_id FROM exam_questions WHERE exam_id = ?", (exam_id,))
    question_ids = [row['question_id'] for row in cursor.fetchall()]
    conn.close()
    return question_ids

def unhide_answers_for_questions(question_ids: List[int]):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Using a placeholder for each question_id to prevent SQL injection
    placeholders = ', '.join('?' for _ in question_ids)
    query = f"UPDATE questions SET hide_answers = 0 WHERE question_id IN ({placeholders})"
    cursor.execute(query, question_ids)
    conn.commit()
    conn.close()
