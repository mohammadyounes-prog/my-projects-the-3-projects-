import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3
import os
import json
import sys
from contextlib import ExitStack 

# Define a temporary in-memory database path for testing
TEST_DB_PATH = ":memory:" 

# Custom Connection class that makes .close() a no-op
class NoOpConnection(sqlite3.Connection):
    def close(self):
        pass # Do nothing when close is called

@pytest.fixture(name="client")
def client_fixture():
    # Step 1: Create the SINGLE persistent in-memory database for the fixture FIRST.
    # This uses the original sqlite3.connect, but with our custom factory.
    # CRITICAL: Set check_same_thread=False to allow usage across different threads.
    shared_in_memory_db = sqlite3.connect(TEST_DB_PATH, factory=NoOpConnection, check_same_thread=False) 
    shared_in_memory_db.row_factory = sqlite3.Row

    with ExitStack() as stack:
        # Step 2: Patch sqlite3.connect globally to *always* return our shared_in_memory_db instance.
        # This prevents other calls from creating new in-memory databases and ensures they get our shared one.
        stack.enter_context(patch('sqlite3.connect', return_value=shared_in_memory_db))

        # Step 3: Create tables in our shared_in_memory_db *before* importing backend.database.
        cursor = shared_in_memory_db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                is_super_admin INTEGER DEFAULT 0,
                tenant_id INTEGER,
                email TEXT,
                audience_type TEXT,
                schooldemo12_user_id INTEGER,
                full_name TEXT,
                mobile_phone TEXT,
                role TEXT,
                institution TEXT,
                department TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tenant_id INTEGER,
                audience_type TEXT,
                question_text TEXT,
                choice_1 TEXT,
                choice_2 TEXT,
                choice_3 TEXT,
                choice_4 TEXT,
                correct_option TEXT,
                difficulty_level_id INTEGER,
                cognitive_level_id INTEGER,
                learning_outcome_id INTEGER,
                question_type_id INTEGER,
                task_id INTEGER,
                status TEXT DEFAULT 'pending',
                author_creator TEXT DEFAULT 'System',
                date_created TEXT,
                mark INTEGER DEFAULT 0,
                time_seconds INTEGER DEFAULT 0,
                discriminating_factor TEXT,
                school_type_id INTEGER,
                subject_id INTEGER,
                year_id INTEGER,
                major_id INTEGER,
                course_id INTEGER,
                material_id INTEGER,
                semester_id INTEGER,
                company_id INTEGER,
                department_id INTEGER,
                job_role_id INTEGER,
                solution TEXT,
                hide_answers INTEGER DEFAULT 0,
                variables TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tenant_id INTEGER,
                request_parameters TEXT,
                num_questions_requested INTEGER,
                num_questions_generated INTEGER,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_api_name TEXT NOT NULL UNIQUE,
                generation_method TEXT NOT NULL,
                tenant_id INTEGER,
                is_default BOOLEAN NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                api_key TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS difficulty_levels (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cognitive_levels (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_outcomes (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_types (id INTEGER PRIMARY KEY, name TEXT UNIQUE, api_name TEXT UNIQUE)
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS university_majors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS university_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS university_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS university_semesters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                country_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenant_countries (
                tenant_id INTEGER,
                country_id INTEGER,
                PRIMARY KEY (tenant_id, country_id),
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (country_id) REFERENCES countries(country_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_user_question_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                audience_type TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, audience_type)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_tenant_question_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                audience_type TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                UNIQUE (tenant_id, audience_type)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                model TEXT,
                questions_debited INTEGER,
                event_type TEXT NOT NULL,
                total_price_cents INTEGER,
                currency TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                audience_type TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                task_id INTEGER,
                model TEXT,
                questions_debited INTEGER,
                event_type TEXT NOT NULL,
                total_price_cents INTEGER,
                currency TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                audience_type TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        shared_in_memory_db.commit()

        # Step 4: Force reload backend.database to ensure it uses the patched sqlite3.connect.
        # This is CRITICAL for migrations to run on the shared_in_memory_db.
        if 'backend.database' in sys.modules:
            del sys.modules['backend.database']
        import backend.database # Import the real module (now using patched connect)

        # Step 7: Patch functions from online_exam_db_connector before backend.main is imported.
        stack.enter_context(patch('backend.online_exam_db_connector.add_student_to_online_exam_db', return_value=1))
        stack.enter_context(patch('backend.online_exam_db_connector.add_employee_to_online_exam_db', return_value={"teacherId": 1, "classId": 1, "facultyId": 1, "majorId": 1}))
        stack.enter_context(patch('backend.online_exam_db_connector.add_course_and_category_to_online_exam_db', return_value={"status": "success", "course_id": 1, "category_id": 1, "course_name": "Test Course"}))
        stack.enter_context(patch('backend.online_exam_db_connector.setup_course_defaults', return_value=None))
        stack.enter_context(patch('backend.online_exam_db_connector.add_teacher_link', return_value=1))
        stack.enter_context(patch('backend.online_exam_db_connector.add_student_status_to_online_exam_db', return_value=None))
        stack.enter_context(patch('backend.online_exam_db_connector.get_employee_id_by_email', return_value=1))
        stack.enter_context(patch('backend.online_exam_db_connector.get_teacher_link_id_by_teacher_id', return_value=1))
        stack.enter_context(patch('backend.online_exam_db_connector.get_teacher_link_details', return_value={"classId": 1, "facultyId": 1, "majorId": 1}))
        stack.enter_context(patch('backend.online_exam_db_connector._add_exam_specific_filters', return_value=None))
        stack.enter_context(patch('backend.online_exam_db_connector.get_online_exam_db_connection', return_value=MagicMock()))
        stack.enter_context(patch('backend.online_exam_db_connector.add_major_for_employee', return_value=None))
        stack.enter_context(patch('backend.online_exam_db_connector.add_appstatus_for_employee', return_value=None))
        from main import app

        # Step 5: Override FastAPI's get_db dependency to return our shared_in_memory_db.
        app.dependency_overrides[backend.database.get_db] = lambda: shared_in_memory_db
        stack.callback(app.dependency_overrides.clear) # Clear overrides after the fixture runs

        # Step 6: Patch backend.database.get_db_connection to *also* return our shared_in_memory_db.
        # This covers any direct calls to get_db_connection that might not go through FastAPI Depends.
        stack.enter_context(patch.object(backend.database, 'get_db_connection', return_value=shared_in_memory_db))

        
        # Seed initial data for lookup tables
        cursor.execute("INSERT INTO difficulty_levels (name) VALUES (?)", ("Easy",))
        cursor.execute("INSERT INTO cognitive_levels (name) VALUES (?)", ("Recall",))
        cursor.execute("INSERT INTO learning_outcomes (name) VALUES (?)", ("Understand",))
        cursor.execute("INSERT INTO question_types (name, api_name) VALUES (?, ?)", ("Multiple Choice", "multiple choice"))
        cursor.execute("INSERT INTO countries (name) VALUES (?)", ("TestCountry",))
        
        # Seed initial data for billing_user_question_balances
        cursor.execute("INSERT INTO billing_user_question_balances (user_id, audience_type, balance) VALUES (?, ?, ?)", (1, 'school', 100))
        cursor.execute("INSERT INTO billing_user_question_balances (user_id, audience_type, balance) VALUES (?, ?, ?)", (2, 'university', 100))
        cursor.execute("INSERT INTO billing_user_question_balances (user_id, audience_type, balance) VALUES (?, ?, ?)", (3, 'company', 100))
        shared_in_memory_db.commit()


        with TestClient(app) as client:
            yield client

    shared_in_memory_db.close() # Close the shared connection at the end of the fixture


def register_user_and_get_token(client, username, password, audience_type):
    # Register user
    register_response = client.post(
        "/register",
        json={
            "username": username,
            "password": password,
            "email": f"{username}@example.com",
            "country": "TestCountry",
            "audience_type": audience_type
        }
    )
    # Check for HTTP 500 and print more details if it's an internal server error
    if register_response.status_code != 200:
        print(f"DEBUG: Registration failed for {username}. Status: {register_response.status_code}, Detail: {register_response.json()}")
    assert register_response.status_code == 200, f"Registration failed for {username}: {register_response.json()}"

    # Login user and get token
    token_response = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    assert token_response.status_code == 200, f"Login failed for {username}: {token_response.json()}"
    return token_response.json()["access_token"]

def generate_question(client, token, topic_context, audience_type):
    headers = {"Authorization": f"Bearer {token}"}
    question_data = {
        "topic_context": topic_context,
        "question_type": "multiple choice",
        "difficulty_level": "Easy",
        "country": "TestCountry",
        "audience_type": audience_type,
        "num_questions": 1,
        "model_api_name": "dummy"
    }
    response = client.post("/generate", json=question_data, headers=headers)
    assert response.status_code == 200, f"Question generation failed: {response.json()}"
    return response.json()[0]["question_id"]

def get_questions_for_user(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/questions", headers=headers)
    assert response.status_code == 200, f"Fetching questions failed: {response.json()}"
    return response.json()["questions"]


def test_get_question_by_id_filtering(client):
    # Register two users in different tenants and audience types
    school_user_token = register_user_and_get_token(client, "schooluser2", "password123", "school")
    university_user_token = register_user_and_get_token(client, "universityuser2", "password123", "university")

    # Generate a question for the school user
    school_q_id = generate_question(client, school_user_token, "Another school topic", "school")

    # Generate a question for the university user
    university_q_id = generate_question(client, university_user_token, "Another university topic", "university")

    # --- Test 1: School user can retrieve their own question ---
    headers = {"Authorization": f"Bearer {school_user_token}"}
    response = client.get(f"/questions/{school_q_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["question_id"] == school_q_id
    assert response.json()["audience_type"] == "school"

    # --- Test 2: School user CANNOT retrieve university user's question ---
    response = client.get(f"/questions/{university_q_id}", headers=headers)
    assert response.status_code == 404 # Should not be found due to filtering

    # --- Test 3: University user can retrieve their own question ---
    headers = {"Authorization": f"Bearer {university_user_token}"}
    response = client.get(f"/questions/{university_q_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["question_id"] == university_q_id
    assert response.json()["audience_type"] == "university"

    # --- Test 4: University user CANNOT retrieve school user's question ---
    response = client.get(f"/questions/{school_q_id}", headers=headers)
    assert response.status_code == 404 # Should not be found due to filtering

    print("All get_question_by_id filtering tests passed!")

def test_audience_type_separation(client):
    # Register users
    school_token = register_user_and_get_token(client, "schooluser", "password123", "school")
    university_token = register_user_and_get_token(client, "universityuser", "password123", "university")
    company_token = register_user_and_get_token(client, "companyuser", "password123", "company")

    # Generate questions
    school_q_id = generate_question(client, school_token, "School topic 1", "school")
    university_q_id = generate_question(client, university_token, "University topic 1", "university")
    company_q_id = generate_question(client, company_token, "Company topic 1", "company")

    # Verify separation for school user
    school_questions = get_questions_for_user(client, school_token)
    assert len(school_questions) == 1
    assert school_questions[0]["question_id"] == school_q_id
    assert school_questions[0]["audience_type"] == "school"

    # Verify separation for university user
    university_questions = get_questions_for_user(client, university_token)
    assert len(university_questions) == 1
    assert university_questions[0]["question_id"] == university_q_id
    assert university_questions[0]["audience_type"] == "university"

    # Verify separation for company user
    company_questions = get_questions_for_user(client, company_token)
    assert len(company_questions) == 1
    assert company_questions[0]["question_id"] == company_q_id
    assert company_questions[0]["audience_type"] == "company"

    # Negative test: School user should not see university or company questions
    school_user_all_questions = get_questions_for_user(client, school_token)
    assert school_q_id in [q["question_id"] for q in school_user_all_questions]
    assert university_q_id not in [q["question_id"] for q in school_user_all_questions]
    assert company_q_id not in [q["question_id"] for q in school_user_all_questions]

    # Negative test: University user should not see school or company questions
    university_user_all_questions = get_questions_for_user(client, university_token)
    assert university_q_id in [q["question_id"] for q in university_user_all_questions]
    assert school_q_id not in [q["question_id"] for q in university_user_all_questions]
    assert company_q_id not in [q["question_id"] for q in university_user_all_questions]

    # Negative test: Company user should not see school or university questions
    company_user_all_questions = get_questions_for_user(client, company_token)
    assert company_q_id in [q["question_id"] for q in company_user_all_questions]
    assert school_q_id not in [q["question_id"] for q in company_user_all_questions]
    assert university_q_id not in [q["question_id"] for q in company_user_all_questions]

    print("All audience type separation tests passed!")
