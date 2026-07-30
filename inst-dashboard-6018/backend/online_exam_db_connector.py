import pymysql
import os
from pathlib import Path
from fastapi import HTTPException, status
import datetime # New import
import re
import json # New import
import logging # Added to resolve "name 'logging' is not defined" error
from typing import Optional # Explicitly import Optional
from typing import Dict, Any, Optional
import httpx
import hashlib # New import for hashing
from starlette.concurrency import run_in_threadpool

def flatten_dict_for_form(d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
    """
    Flattens a nested dictionary for PHP-style form-urlencoded submission.
    Uses dictionary with lists for repeated keys (handled correctly by httpx).
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}[{k}]" if parent_key else k
        
        if isinstance(v, dict):
            items.update(flatten_dict_for_form(v, new_key))
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                # List of dictionaries (like questions)
                for i, lv in enumerate(v):
                    items.update(flatten_dict_for_form(lv, f"{new_key}[{i}]"))
            else:
                # List of primitives (like link[])
                items[f"{new_key}[]"] = [str(x) for x in v]
        else:
            items[new_key] = str(v) if v is not None else ""
    return items

def error_log(message: str):
    print(f"ERROR: {message}")

# Database configuration for the online-exam project's MySQL database
# These values are derived from D:\QuestionRetrieval\new-q-bank\TAMS\app\schooldemo12\apps\online-exam\config.php
MYSQL_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("ONLINE_EXAM_MYSQL_PORT", 3307))
MYSQL_DB = os.getenv("ONLINE_EXAM_MYSQL_DB", "schooldemo12")
MYSQL_USER = os.getenv("ONLINE_EXAM_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD", "root")

# Secret for online-exam password hashing, derived from config.php
ONLINE_EXAM_PASSWORD_SECRET = '0598251486UserPassSecret'
SECURITY_HASH = hashlib.md5(ONLINE_EXAM_PASSWORD_SECRET.encode()).hexdigest()

_BASE36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'

def _base_encode(number, base, alphabet=_BASE36_ALPHABET):
    """Converts an integer to a base-N string."""
    if number < 0:
        return '-' + _base_encode(-number, base, alphabet)
    res = []
    while number:
        number, idx = divmod(number, base)
        res.append(alphabet[idx])
    return ''.join(reversed(res or '0'))

def php_string_encrypt(input_string: str, key: str) -> str:
    """
    Replicates the PHP String::encrypt function.
    """
    key_sha1 = hashlib.sha1(key.encode()).hexdigest()
    
    str_len = len(input_string)
    key_len = len(key_sha1)
    
    j = 0
    hash_str = ''
    
    for i in range(str_len):
        ord_str = ord(input_string[i])
        if j == key_len:
            j = 0
        ord_key = ord(key_sha1[j])
        j += 1
        
        # PHP: strrev(base_convert(dechex($ordStr + $ordKey),16,36))
        # Python equivalent:
        sum_val = ord_str + ord_key
        hex_val = hex(sum_val)[2:] # Convert to hex, remove '0x' prefix
        base36_val = _base_encode(int(hex_val, 16), 36) # Convert hex to decimal, then to base 36
        hash_str += base36_val[::-1] # Reverse and append
        
    return hash_str

def generate_online_exam_password_hash(raw_password: str) -> str:
    """
    Replicates the PHP hashing scheme for online-exam:
    final_hash = md5(String::encrypt(pass)) . sha1(String::encrypt(pass))
    """
    encrypted_string = php_string_encrypt(raw_password, SECURITY_HASH)
    
    md5_hash = hashlib.md5(encrypted_string.encode()).hexdigest()
    sha1_hash = hashlib.sha1(encrypted_string.encode()).hexdigest()
    
    return md5_hash + sha1_hash

def get_online_exam_db_connection():
    """Establishes and returns a connection to the online-exam project's MySQL database."""
    # We allow pymysql.Error to propagate so callers can handle it (e.g., by skipping online-exam integration)
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor, # Return results as dictionaries
        charset='utf8mb4',
        use_unicode=True
    )

def add_student_to_online_exam_db(username: str, email: str, raw_password: str, full_name: Optional[str] = None, mobile_phone: Optional[str] = None, country: Optional[str] = "USA", role: Optional[str] = None) -> Optional[int]:
    """
    Adds a new student to the 'student' table in the online-exam database.
    Returns the student's ID on success, None on failure.
    """
    conn = None
    
    # Conditionally add S- prefix based on role (case-insensitive and robust)
    display_name = full_name if full_name else username
    role_clean = str(role).lower().strip() if role else ""
    
    if role_clean in ['teacher', 'instructor', 'manager']:
        student_xid = f"s-{username}"
        student_name = f"s-{display_name}"
    else:
        student_xid = username
        student_name = display_name

    print(f"DEBUG: Entering add_student_to_online_exam_db for user: {username}, student_xid: {student_xid}, role: {role})")
    
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Check if student already exists by the actual xId being used
        print(f"DEBUG: add_student_to_online_exam_db - Checking if student '{student_xid}' already exists.")
        cursor.execute("SELECT id FROM student WHERE xId = %s", (student_xid,))
        existing_student = cursor.fetchone()
        
        if existing_student:
            print(f"INFO: Student with login '{student_xid}' already exists. Skipping insertion.")
            return existing_student['id']

        # Generate the online-exam specific password hash
        online_exam_hashed_password = generate_online_exam_password_hash(raw_password)

        # Construct the 'data' JSON field
        user_data_json = json.dumps({"street":"", "email": email, "country": country})

        insert_data = {
            "xId": student_xid, # Use prefixed xId if applicable
            "name": student_name,
            "pass": online_exam_hashed_password,
            "cityID": 1, # Always 1 as per instruction
            "data": user_data_json, # Email is now part of this JSON
            "addressID": 0, 
            "Value": 0.00, # Always 0.00 as per instruction
            "lastLogin": None, 
            "sessionID": None, 
        }

        # Remove keys with None values to let DB defaults apply (especially for NULLable columns)
        # However, for lastLogin and sessionID, we want to explicitly insert NULL if allowed.
        # Constructing query manually to ensure reserved words like 'Value' are handled.
        
        cols = []
        placeholders = []
        vals = []
        for k, v in insert_data.items():
            # Wrap column names in backticks to handle reserved words like 'Value'
            cols.append(f"`{k}`")
            placeholders.append("%s")
            vals.append(v)

        columns_str = ', '.join(cols)
        placeholders_str = ', '.join(placeholders)
        insert_query = f"INSERT INTO student ({columns_str}) VALUES ({placeholders_str})"
        
        print(f"DEBUG: add_student_to_online_exam_db - Executing INSERT query: {insert_query}")
        cursor.execute(insert_query, tuple(vals))
        new_student_id = cursor.lastrowid
        conn.commit()
        print(f"DEBUG: add_student_to_online_exam_db - INSERT query executed, new_student_id: {new_student_id}")
        print(f"INFO: Student '{username}' successfully added to online-exam DB with ID: {new_student_id}.")
        return new_student_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add student '{username}' to online-exam DB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding student '{username}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()

def _add_exam_specific_filters(conn, cursor, course_id: int, username: str, current_date: str, course_sequential_number: int):
    """
    Helper function to add the two specific filters required for each exam.
    """
    # Use the connection and cursor passed from the calling function
    
    # Filter 1: Cognitive Level
    base_name_cognition = f"{username}-{course_sequential_number}-{current_date}"
    name_cognition = base_name_cognition
    description_cognition = f"{base_name_cognition} معرفة"
    value_cognition = "تذكر,إستيعاب,فهم,تحليل,تطبيق,إبداع"

    insert_data_cognition = {
        "name": name_cognition,
        "description": description_cognition,
        "type": "select",
        "value": value_cognition,
        "courseId": course_id,
        "parent": 0,
        "important": 2,
    }
    
    columns_cognition = ', '.join(insert_data_cognition.keys())
    placeholders_cognition = ', '.join(['%s'] * len(insert_data_cognition))
    insert_query_cognition = f"INSERT INTO filters ({columns_cognition}) VALUES ({placeholders_cognition})"
    cursor.execute(insert_query_cognition, tuple(insert_data_cognition.values()))
    print(f"Added exam-specific filter: {insert_data_cognition['name']}")

    # Filter 2: Content
    base_name_content = f"{username}-{course_sequential_number}-{current_date}"
    name_content = base_name_content
    description_content = f"{base_name_content} محتوى"
    value_content = "وحدة اولى,وحدة 2,وحدة 3,وحدة 4,وحدة 5,وحدة 6"

    insert_data_content = {
        "name": name_content,
        "description": description_content,
        "type": "select",
        "value": value_content,
        "courseId": course_id,
        "parent": 0,
        "important": 2,
    }
    
    columns_content = ', '.join(insert_data_content.keys())
    placeholders_content = ', '.join(['%s'] * len(insert_data_content))
    insert_query_content = f"INSERT INTO filters ({columns_content}) VALUES ({placeholders_content})"
    cursor.execute(insert_query_content, tuple(insert_data_content.values()))
    print(f"Added exam-specific filter: {insert_data_content['name']}")


def add_course_and_category_to_online_exam_db(username: str):
    """
    Adds a course for the user if it doesn't exist, and then adds a new main category.
    Course name is now permanent: 'COR-username'.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Find or create the user's single, permanent course
        course_name = f"COR-{username}"
        cursor.execute("SELECT id FROM course WHERE name = %s", (course_name,))
        existing_course = cursor.fetchone()

        if existing_course:
            course_id = existing_course['id']
            print(f"Found existing course '{course_name}' with ID: {course_id}")
        else:
            # Insert the new permanent course
            cursor.execute("INSERT INTO course (name) VALUES (%s)", (course_name,))
            conn.commit()
            course_id = cursor.lastrowid
            print(f"Created new permanent course '{course_name}' with ID: {course_id}")

        # 2. Add a new main category to the 'category' table, linked to the permanent course
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_category_name = f"CAT-{username}"
        category_parent = 0

        # Find the next available sequential number for the category name for this course
        next_category_number = 1
        cursor.execute(
            "SELECT name FROM category WHERE courseID = %s AND name LIKE %s ORDER BY name DESC",
            (course_id, f"{base_category_name}-%%-{current_date}")
        )
        existing_categories = cursor.fetchall()

        if existing_categories:
            numbers = []
            for cat in existing_categories:
                match = re.search(rf"^{re.escape(base_category_name)}-(\d+)-{re.escape(current_date)}$", cat['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_category_number = max(numbers) + 1
        
        category_name = f"{base_category_name}-{next_category_number}-{current_date}"

        # Insert new category, linked to the single course
        new_category_data = {
            "name": category_name,
            "parent": category_parent,
            "courseID": course_id,
        }
        
        columns = ', '.join(new_category_data.keys())
        placeholders = ', '.join(['%s'] * len(new_category_data))
        insert_query = f"INSERT INTO category ({columns}) VALUES ({placeholders})"

        cursor.execute(insert_query, tuple(new_category_data.values()))
        conn.commit()
        category_id = cursor.lastrowid
        print(f"Category '{category_name}' added for course '{course_name}' with ID: {category_id}")

        # The course sequential number is no longer relevant for the course itself,
        # but we can return the category's sequential number for any dependent logic.
        return {
            "status": "success",
            "message": f"Category '{category_name}' added for course '{course_name}' with ID: {category_id}.",
            "course_id": course_id,
            "category_id": category_id,
            "course_name": course_name,
            "course_sequential_number": next_category_number 
        }

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Database operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {e}"
        )
    finally:
        if conn:
            conn.close()

def setup_course_defaults(course_id: int, category_id: int, course_name: str, username: str):
    """
    Adds default filters and objectives for a new course and category.
    """
    from database import get_all_learning_outcomes
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Add default filters (Removed from here - now added per exam in _add_exam_specific_filters)

        # 2. Add default objectives
        
        # First, find the maximum current xId to increment from
        cursor.execute("SELECT MAX(CAST(xId AS UNSIGNED)) as max_xid FROM objective")
        result = cursor.fetchone()
        current_max_xid = result['max_xid'] if result and result['max_xid'] is not None else 0

        learning_outcomes = get_all_learning_outcomes()
        objectives_to_add = []
        for lo in learning_outcomes:
            objectives_to_add.append({"name": lo['name'], "courseId": course_id, "categorySet": str(category_id)})
            if lo.get('name_ar'):
                objectives_to_add.append({"name": lo['name_ar'], "courseId": course_id, "categorySet": str(category_id)})

        for objective_data in objectives_to_add:
            # Check if an objective with the same name and courseId/categorySet already exists
            cursor.execute("SELECT xId FROM objective WHERE name = %s AND courseId = %s AND categorySet = %s", (objective_data["name"], course_id, str(category_id)))
            if cursor.fetchone():
                print(f"Objective '{objective_data['name']}' already exists for course/category. Skipping.")
                continue
            
            # Increment xId and add it to the data for insertion
            current_max_xid += 1
            objective_data['xId'] = str(current_max_xid)

            columns = ', '.join(objective_data.keys())
            placeholders = ', '.join(['%s'] * len(objective_data))
            insert_query = f"INSERT INTO objective ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(objective_data.values()))
            # Silenced: print(f"Added objective: {objective_data['name']} with xId: {objective_data['xId']}")

        conn.commit()
        print("Default filters and objectives setup complete.")
        return True

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Default setup failed: {e}")
        # We don't raise an HTTPException here because this is a secondary operation.
        # The main operation of creating the course/category might have succeeded.
        return False
    finally:
        if conn:
            conn.close()

def insert_question_to_bank(
    question_data: Dict[str, Any],
    course_id: int,
    category_id: int,
    username: str, teacher_id: int = 11
):
    """
    Inserts a generated question into the 'bank' table of the online-exam database.
    """
    print("DEBUG: Using the primary connector file. This is the correct file.")
    print(f"DEBUG: Incoming correct_option: {question_data.get('correct_option')}")
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        title = question_data.get("question_text", "")
        # Normalize question_type_raw for better matching
        question_type_raw = str(question_data.get("question_type") or "").lower().strip()
        
        # Add more direct mappings and normalization for question types
        normalized_question_type_map = {
            "multiple choice": "mch",
            "multiple_choice": "mch",
            "mcq": "mch",
            "yes no": "yn",
            "yes_no": "yn",
            "yn": "yn",
            "true/false": "yn",
            "true_false": "yn",
            "accept reject": "ar",
            "accept_reject": "ar",
            "multi answer": "chbox",
            "multiple answer": "chbox",
            "multiple_answer": "chbox",
            "checkbox": "chbox",
            "chbox": "chbox",
            "text": "text",
            "fill in the blank": "text",
            "fill_in_the_blank": "text",
            "essay": "open",
            "open-ended": "open",
            "short answer": "text",
            "short_answer": "text",
            "hand write": "hw",
            "hand_write": "hw",
            "matching": "match",
            "scenario_based": "open",
            "case_study": "open",
        }
        
        # Try to get the mapped type, then fallback to raw if not found
        mapped_type = normalized_question_type_map.get(question_type_raw)
        
        if mapped_type:
            question_type_bank = mapped_type
        else:
            # If the normalized type is not in our map, it's unrecognized.
            # Log a warning and use 'mch' as fallback, as per original logic, but highlight it.
            print(f"WARNING: Unrecognized question type '{question_data.get('question_type')}' received from AI generation. Raw input was: '{question_type_raw}'. Falling back to 'mch'.")
            question_type_bank = "mch" 

        # Prepare answers, correct, and resources
        answers_list = []
        
        # We need to know which choices are correct for 'chbox' to assign marks
        correct_raw = question_data.get("correct_option", "")
        correct_indices = []
        if question_type_bank == "chbox":
            if isinstance(correct_raw, list):
                correct_indices = [int(x) for x in correct_raw]
            elif isinstance(correct_raw, str):
                if correct_raw.isdigit():
                    correct_indices = [int(correct_raw)]
                else:
                    letter_to_idx = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
                    correct_indices = [letter_to_idx[l] for l in correct_raw.upper() if l in letter_to_idx]
            
            num_correct = len(correct_indices)
            question_total_mark = float(question_data.get("mark", 0))
            mark_per_answer = question_total_mark / num_correct if num_correct > 0 else 0

        if question_type_bank in ["mch", "chbox", "yn", "ar"]:
            for i in range(1, 5):
                choice = question_data.get(f"choice_{i}")
                if choice:
                    if question_type_bank == "chbox":
                        is_correct = i in correct_indices
                        answers_list.append({
                            "text": choice,
                            "mark": mark_per_answer if is_correct else 0
                        })
                    else:
                        answers_list.append(choice)
        elif question_type_bank in ["open", "text"]:
            solution_text = question_data.get("solution", "")
            if solution_text:
                answers_list.append(solution_text)
        
        answers = json.dumps(answers_list, ensure_ascii=False)

        correct = correct_raw
        if question_type_bank in ["mch", "yn", "ar"]:
            if correct == "A": correct = "1"
            elif correct == "B": correct = "2"
            elif correct == "C": correct = "3"
            elif correct == "D": correct = "4"
        elif question_type_bank == "chbox":
            if isinstance(correct, list):
                correct = json.dumps(correct)
            else:
                # Handle multiple letters like "AB" or single letters/digits
                if isinstance(correct, str):
                    if correct.isdigit():
                        correct = json.dumps([int(correct)])
                    else:
                        # Map letters to indices
                        letter_to_idx = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
                        indices = [letter_to_idx[l] for l in correct.upper() if l in letter_to_idx]
                        correct = json.dumps(indices)
                else:
                    correct = json.dumps([])
        elif question_type_bank in ["open", "text"]:
            correct = question_data.get("correct_option", "") or question_data.get("solution", "")

        resources_data = question_data.get("resources", {"question":[],"answers":{}})
        resources = json.dumps(resources_data)

        bank_data = {
            "title": title,
            "answers": answers,
            "correct": correct,
            "teacherId": teacher_id,
            "courseId": course_id,
            "type": question_type_bank, # <-- This is where the corrected type is used
            "categorySet": str(category_id),
            "mark": float(question_data.get("mark") or 5.00),
            "duration": int(round((question_data.get("time_seconds") or 120) / 60)),
            "resources": resources,
            "trueAnswersCount": 0,
            "falseAnswersCount": 0,
            "parent": None,
        }

        columns = ', '.join(bank_data.keys())
        placeholders = ', '.join(['%s'] * len(bank_data))
        insert_query = f"INSERT INTO bank ({columns}) VALUES ({placeholders})"

        cursor.execute(insert_query, tuple(bank_data.values()))
        conn.commit()
        question_id = cursor.lastrowid # Get the ID of the newly inserted question
        logging.info(f"TAMS_SYNC: Question '{title[:50]}...' successfully inserted into 'bank' table with ID: {question_id}.")

        # Insert into objective table and get the new objective_id
        objective_id = None
        try:
            learning_outcome = question_data.get("learning_outcome")
            if learning_outcome:
                logging.info(f"TAMS_SYNC: Processing objective for learning outcome: '{learning_outcome}'")
                # Check if an objective with the same name, courseId, and categorySet already exists
                cursor.execute(
                    "SELECT id FROM objective WHERE name = %s AND courseId = %s AND categorySet = %s",
                    (learning_outcome, course_id, str(category_id))
                )
                existing_objective = cursor.fetchone()

                if existing_objective:
                    objective_id = existing_objective['id']
                    logging.info(f"TAMS_SYNC: Using existing objective '{learning_outcome}' with ID: {objective_id}")
                else:
                    # Find the next available sequential number for the xId for this user
                    cursor.execute(
                        "SELECT xId FROM objective WHERE xId LIKE %s ORDER BY xId DESC",
                        (f"obj-{username}-%%",)
                    )
                    existing_xIds = cursor.fetchall()
                    next_xid_number = 1
                    if existing_xIds:
                        numbers = []
                        for row in existing_xIds:
                            match = re.search(rf"^obj-{re.escape(username)}-(\d+)$", row['xId'])
                            if match:
                                numbers.append(int(match.group(1)))
                        if numbers:
                            next_xid_number = max(numbers) + 1
                    
                    new_xId = f"obj-{username}-{next_xid_number}"

                    objective_data = {
                        "xId": new_xId,
                        "name": learning_outcome,
                        "courseId": course_id,
                        "categorySet": str(category_id),
                    }
                    
                    obj_columns = ', '.join(objective_data.keys())
                    obj_placeholders = ', '.join(['%s'] * len(objective_data))
                    objective_insert_query = f"INSERT INTO objective ({obj_columns}) VALUES ({obj_placeholders})"
                    
                    cursor.execute(objective_insert_query, tuple(objective_data.values()))
                    objective_id = cursor.lastrowid # Get the new objective ID
                    conn.commit()
                    logging.info(f"TAMS_SYNC: Successfully added objective '{learning_outcome}' with xId '{new_xId}' and objective_id {objective_id}.")

                    # --- NEW: Mirror the objective in the 'filters' table ---
                    # Many TamsQB reports rely on the 'filters' table for categorizing data.
                    try:
                        cursor.execute(
                            "SELECT id FROM filters WHERE name = %s AND courseId = %s AND type = 'objective'",
                            (learning_outcome, course_id)
                        )
                        existing_filter = cursor.fetchone()
                        if not existing_filter:
                            filter_data = {
                                "name": learning_outcome,
                                "description": f"Learning Outcome: {learning_outcome}",
                                "type": "objective",
                                "value": learning_outcome,
                                "courseId": course_id,
                                "parent": 0,
                                "important": 1,
                                "xId": f"flt-obj-{new_xId}"
                            }
                            cols = ', '.join(filter_data.keys())
                            placeholders = ', '.join(['%s'] * len(filter_data))
                            cursor.execute(f"INSERT INTO filters ({cols}) VALUES ({placeholders})", tuple(filter_data.values()))
                            conn.commit()
                            logging.info(f"TAMS_SYNC: Mirrored objective '{learning_outcome}' in 'filters' table.")
                        else:
                            logging.info(f"TAMS_SYNC: Filter entry for objective '{learning_outcome}' already exists.")
                    except Exception as fe:
                        logging.error(f"TAMS_SYNC WARNING: Could not mirror objective in filters table: {fe}")
                    # --- END MIRRORING ---

        except pymysql.Error as e:
            logging.error(f"TAMS_SYNC ERROR: Failed to insert into objective table for question ID {question_id}: {e}")


        # Insert into filterdata table
        try:
            filters_to_insert = []
            
            # 1. Mark Filter (ID 1)
            mark_value = str(question_data.get("mark", 0))
            filters_to_insert.append((question_id, 1, mark_value, 1))

            # 2. Time Filter (ID 2)
            time_in_minutes = str(round((question_data.get("time_seconds", 0) / 60)))
            filters_to_insert.append((question_id, 2, time_in_minutes, 1))

            # 3. Difficulty Filter (ID 32)
            difficulty_value = str(question_data.get("difficulty_level", "medium")).lower()
            filters_to_insert.append((question_id, 32, difficulty_value, 1))
            
            # 4. Creator Filter (ID 53)
            creator_value = str(username)
            filters_to_insert.append((question_id, 53, creator_value, 1))
            
            # 5. Discrimination Factor Filter (ID 33)
            filters_to_insert.append((question_id, 33, "1", 1))
            
            # 6. Learning Outcome Filter (New Entry)
            learning_outcome_name = question_data.get("learning_outcome")
            if learning_outcome_name:
                # CRITICAL FIX: The report logic uses the 'filters' table.
                # We must find the ID in the 'filters' table for this objective.
                cursor.execute(
                    "SELECT id FROM filters WHERE name = %s AND courseId = %s AND type = 'objective'",
                    (learning_outcome_name, course_id)
                )
                filter_row = cursor.fetchone()
                if filter_row:
                    actual_filter_id = filter_row['id']
                    filters_to_insert.append((question_id, actual_filter_id, learning_outcome_name, 3))
                    logging.info(f"TAMS_SYNC: Added Learning Outcome filter: bankId={question_id}, filterId={actual_filter_id}, value='{learning_outcome_name}', type=3")
                else:
                    # Fallback to objective_id if filter not found, but we should have created it above
                    if objective_id:
                        filters_to_insert.append((question_id, objective_id, learning_outcome_name, 3))
                        logging.info(f"TAMS_SYNC: Falling back to objective_id: bankId={question_id}, filterId={objective_id}, value='{learning_outcome_name}', type=3")


            filterdata_insert_query = "INSERT INTO filtersdata (bankId, filterId, value, type) VALUES (%s, %s, %s, %s)"
            
            cursor.executemany(filterdata_insert_query, filters_to_insert)
            conn.commit()
            logging.info(f"TAMS_SYNC: Successfully added {len(filters_to_insert)} entries to filterdata for question ID {question_id}.")

        except pymysql.Error as e:
            logging.error(f"TAMS_SYNC ERROR: Failed to insert into filterdata table for question ID {question_id}: {e}")
        
        filterdata_summary = {
            "filters_added": len(filters_to_insert),
            "details": filters_to_insert
        }

        return {
            "question_id": question_id,
            "objective_id": objective_id,
            "filterdata": filterdata_summary
        }

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to insert question into 'bank' table: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_course_category_ids(username: str) -> Dict[str, Any]:
    """
    Retrieves the course_id for the user's permanent course and their latest category_id.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Get the user's permanent course_id
        course_name = f"COR-{username}"
        cursor.execute(
            "SELECT id FROM course WHERE name = %s",
            (course_name,)
        )
        course_row = cursor.fetchone()
        
        if not course_row:
            print(f"WARNING: No permanent course '{course_name}' found for user '{username}'.")
            return {"course_id": None, "category_id": None}
        
        course_id = course_row['id']
        print(f"DEBUG: Found permanent course '{course_name}' with ID: {course_id} for user '{username}'.")

        # 2. Get the latest category_id for this course and user
        # The category naming still includes date and sequence to distinguish batches of questions.
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_category_name_prefix = f"CAT-{username}-"
        category_parent = 0 # Main categories have parent 0

        cursor.execute(
            "SELECT id, name FROM category WHERE courseID = %s AND parent = %s AND name LIKE %s ORDER BY id DESC LIMIT 1",
            (course_id, category_parent, f"{base_category_name_prefix}%%-{current_date}")
        )
        category_row = cursor.fetchone()
        
        if not category_row:
            # Fallback: if no category for today, just get the latest one for this user's course
            cursor.execute(
                "SELECT id, name FROM category WHERE courseID = %s AND parent = %s AND name LIKE %s ORDER BY id DESC LIMIT 1",
                (course_id, category_parent, f"{base_category_name_prefix}%")
            )
            category_row = cursor.fetchone()

        if not category_row:
            print(f"WARNING: No category found for course ID {course_id} and user '{username}'.")
            return {"course_id": course_id, "category_id": None}

        category_id = category_row['id']
        category_name = category_row['name']
        print(f"DEBUG: Found latest category '{category_name}' with ID: {category_id} for course ID {course_id}.")

        return {"course_id": course_id, "category_id": category_id}

    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_user_course_category_ids: {e}")
        return {"course_id": None, "category_id": None}
    finally:
        if conn:
            conn.close()

def publish_exam_status(exam_id: int) -> bool:
    """
    Updates the status of a given exam to 'published' in the 'exam' table.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        update_query = "UPDATE exam SET status = %s WHERE id = %s"
        cursor.execute(update_query, ("published", exam_id))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Exam ID {exam_id} status updated to 'published'.")
            return True
        else:
            print(f"Exam ID {exam_id} not found or status already 'published'.")
            return False

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to update exam status for ID {exam_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {e}"
        )
    finally:
        if conn:
            conn.close()

def add_class_for_employee(username: str) -> Optional[int]:
    """
    Adds a new class to the 'class' table in the online-exam database for a newly registered teacher.
    Returns the class_id on success, None on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_class_for_employee for username: {username}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_class_name = f"cla-{username}"
        
        # Find the next available sequential number for the class name
        next_class_number = 1
        cursor.execute(
            "SELECT name FROM class WHERE name LIKE %s ORDER BY name DESC",
            (f"{base_class_name}-%%-{current_date}",)
        )
        existing_classes = cursor.fetchall()
        
        if existing_classes:
            numbers = []
            for cls in existing_classes:
                match = re.search(rf"^{re.escape(base_class_name)}-(\d+)-{re.escape(current_date)}$", cls['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_class_number = max(numbers) + 1
        
        class_name = f"{base_class_name}-{next_class_number}-{current_date}"

        insert_data = {
            "xId": 0, # Always 0 as per instruction
            "name": class_name,
            "supervisorId": 0, # Always 0 as per instruction
            "data": None, # Null as per instruction
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO class ({columns}) VALUES ({placeholders})"
        
        print(f"DEBUG: Class insert query: {insert_query}")
        print(f"DEBUG: Class insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        class_id = cursor.lastrowid
        print(f"INFO: Class '{class_name}' successfully added to online-exam DB with ID: {class_id}.")
        return class_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add class for employee '{username}' to online-exam DB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding class for employee '{username}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_faculty_for_employee(username: str, class_id: int, major_id: int) -> Optional[int]:
    """
    Adds a new faculty entry to the 'faculty' table in the online-exam database.
    Returns the faculty_id on success, None on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_faculty_for_employee for username: {username}, class_id: {class_id}, major_id: {major_id}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_faculty_name = f"Fac-{username}"
        
        next_faculty_number = 1
        cursor.execute(
            "SELECT name FROM faculty WHERE name LIKE %s ORDER BY name DESC",
            (f"{base_faculty_name}-%%-{current_date}",)
        )
        existing_faculty = cursor.fetchall()
        
        if existing_faculty:
            numbers = []
            for fac in existing_faculty:
                match = re.search(rf"^{re.escape(base_faculty_name)}-(\d+)-{re.escape(current_date)}$", fac['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_faculty_number = max(numbers) + 1
        
        faculty_name = f"{base_faculty_name}-{next_faculty_number}-{current_date}"

        insert_data = {
            "xId": 0, # Always 0 as per instruction
            "name": faculty_name,
            "classSet": str(class_id), # Store as string
            "majorSet": str(major_id), # Store as string
            "data": None, # Null as per instruction
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO faculty ({columns}) VALUES ({placeholders})"
        
        print(f"DEBUG: Faculty insert query: {insert_query}")
        print(f"DEBUG: Faculty insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        faculty_id = cursor.lastrowid
        print(f"INFO: Faculty '{faculty_name}' successfully added to online-exam DB with ID: {faculty_id}.")
        return faculty_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add faculty for employee '{username}' to online-exam DB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding faculty for employee '{username}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_major_for_employee(username: str) -> Optional[int]:
    """
    Adds a new major entry to the 'major' table in the online-exam database.
    Returns the major_id on success, None on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_major_for_employee for username: {username}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_major_name = f"Maj-{username}"
        
        next_major_number = 1
        cursor.execute(
            "SELECT name FROM major WHERE name LIKE %s ORDER BY name DESC",
            (f"{base_major_name}-%%-{current_date}",)
        )
        existing_majors = cursor.fetchall()
        
        if existing_majors:
            numbers = []
            for maj in existing_majors:
                match = re.search(rf"^{re.escape(base_major_name)}-(\d+)-{re.escape(current_date)}$", maj['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_major_number = max(numbers) + 1
        
        major_name = f"{base_major_name}-{next_major_number}-{current_date}"

        insert_data = {
            "name": major_name,
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO major ({columns}) VALUES ({placeholders})"
        
        print(f"DEBUG: Major insert query: {insert_query}")
        print(f"DEBUG: Major insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        major_id = cursor.lastrowid
        print(f"INFO: Major '{major_name}' successfully added to online-exam DB with ID: {major_id}.")
        return major_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add major for employee '{username}' to online-exam DB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding major for employee '{username}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_appstatus_for_employee(username: str) -> Optional[int]:
    """
    Adds a new appstatus entry to the 'appstatus' table in the online-exam database.
    Returns the appstatus_id on success, None on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_appstatus_for_employee for username: {username}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        base_appstatus_name = f"App-{username}"
        
        next_appstatus_number = 1
        cursor.execute(
            "SELECT name FROM appstatus WHERE name LIKE %s ORDER BY name DESC",
            (f"{base_appstatus_name}-%%-{current_date}",)
        )
        existing_appstatus = cursor.fetchall()
        
        if existing_appstatus:
            numbers = []
            for ad in existing_appstatus:
                match = re.search(rf"^{re.escape(base_appstatus_name)}-(\d+)-{re.escape(current_date)}$", ad['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_appstatus_number = max(numbers) + 1
        
        appstatus_name = f"{base_appstatus_name}-{next_appstatus_number}-{current_date}"

        insert_data = {
            "name": appstatus_name,
            "current": 0, # Always 0 as per instruction
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO appstatus ({columns}) VALUES ({placeholders})"
        
        print(f"DEBUG: Appstatus insert query: {insert_query}")
        print(f"DEBUG: Appstatus insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        appstatus_id = cursor.lastrowid
        print(f"INFO: Appstatus '{appstatus_name}' successfully added to online-exam DB with ID: {appstatus_id}.")
        return appstatus_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add appstatus for employee '{username}' to online-exam DB: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding appstatus for employee '{username}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_employee_to_online_exam_db(full_name: str, email: str, raw_password: str, mobile_phone: Optional[str] = None) -> Optional[Dict[str, int]]:
    """
    Adds a new employee (teacher) and their related entities to the online-exam database.
    If employee exists, fetches their existing details.
    Returns a dictionary of created or fetched IDs on success, None on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_employee_to_online_exam_db for email: {email}, full_name: {full_name}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Check if employee already exists by email
        print(f"DEBUG: add_employee_to_online_exam_db - Checking if employee with email '{email}' already exists.")
        cursor.execute("SELECT id FROM employee WHERE email = %s", (email,))
        existing_employee = cursor.fetchone()
        print(f"DEBUG: add_employee_to_online_exam_db - Existing employee result: {existing_employee}")
        if existing_employee:
            print(f"INFO: Employee with email '{email}' already exists in online-exam DB (ID: {existing_employee['id']}). Fetching associated data.")
            teacher_id = existing_employee['id']
            
            # Fetch associated details from teacherLink
            teacher_link_id = get_teacher_link_id_by_teacher_id(teacher_id)
            if teacher_link_id:
                link_details = get_teacher_link_details(teacher_link_id)
                if link_details:
                    print(f"DEBUG: Found existing link details for teacher {teacher_id}: {link_details}")
                    return {
                        "teacherId": teacher_id,
                        "classId": link_details.get('classId'),
                        "facultyId": link_details.get('facultyId'),
                        "majorId": link_details.get('majorId')
                    }
            
            print(f"WARNING: Existing employee {teacher_id} found, but could not find their link details (teacherLink). This may cause issues if the registration flow depends on them.")
            return {
                "teacherId": teacher_id,
                "classId": None,
                "facultyId": None,
                "majorId": None
            }

        # Generate the online-exam specific password hash
        online_exam_hashed_password = generate_online_exam_password_hash(raw_password)

        teacher_rules = "admin-zone,resultsReport-can-access,lORep-can-access,qbankRep-can-access,studentsListReport-can-access,exam-can-correct,exam-can-edit,exam-can-add,exam-can-delete,exam-can-publish,exam-can-access,exam-can-unpublish,exam-can-delete-publish,exam-can-duplicate,exam-can-delete-template,exam-can-export,exam-answers-can-export,que-can-duplicate,qbank-can-import-file,qbank-can-approve-questions,qbank-can-access,que-can-move,que-can-delete,que-can-add,que-can-edit,cat-can-delete,cat-can-add,cat-can-edit,stdRep-can-access,exam-can-view-all,"
        
        employee_data_json = json.dumps({
            "address": "",
            "mobile": mobile_phone if mobile_phone else "",
            "facultyId": "" 
        })

        insert_data = {
            "name": full_name,
            "email": email,
            "pass": online_exam_hashed_password,
            "rules": teacher_rules,
            "position": "teacher",
            "data": employee_data_json,
            "workGroup": 3,
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO employee ({columns}) VALUES ({placeholders})"
        
        print(f"DEBUG: add_employee_to_online_exam_db - Executing INSERT query.")
        cursor.execute(insert_query, tuple(insert_data.values()))
        employee_id = cursor.lastrowid
        print(f"DEBUG: add_employee_to_online_exam_db - INSERT query executed, employee_id: {employee_id}")
        print(f"INFO: Employee '{full_name}' successfully added to online-exam DB with ID: {employee_id}.")

        # --- Add related entries for the new employee (teacher) ---
        class_id = add_class_for_employee(full_name)
        if class_id is None:
            print(f"ERROR: Failed to add class for employee '{full_name}'. Rolling back.")
            conn.rollback()
            return None

        major_id = add_major_for_employee(full_name)
        if major_id is None:
            print(f"ERROR: Failed to add major for employee '{full_name}'. Rolling back.")
            conn.rollback()
            return None
        
        appstatus_id = add_appstatus_for_employee(full_name)
        if appstatus_id is None:
            print(f"ERROR: Failed to add appstatus for employee '{full_name}'. Rolling back.")
            conn.rollback()
            return None

        faculty_id = add_faculty_for_employee(full_name, class_id, major_id)
        if faculty_id is None:
            print(f"ERROR: Failed to add faculty for employee '{full_name}'. Rolling back.")
            conn.rollback()
            return None
        
        conn.commit()

        print(f"DEBUG: add_employee_to_online_exam_db - Returning employee_data: {{'teacherId': {employee_id}, 'classId': {class_id}, 'majorId': {major_id}, 'facultyId': {faculty_id}}}")
        return {
            "teacherId": employee_id,
            "classId": class_id,
            "majorId": major_id,
            "facultyId": faculty_id
        }

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add employee '{full_name}' to online-exam DB: {e}")
        return None
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR: An unexpected error occurred while adding employee '{full_name}' to online-exam DB: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_teacher_link(teacher_id: int, course_id: int, class_id: int, faculty_id: int, major_id: int) -> Optional[int]:
    """
    Adds a new entry to the 'teacherLink' table if it doesn't already exist.
    Returns the ID of the new or existing teacherLink entry on success, None on failure.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Check if a link with this exact configuration already exists
        select_query = """
            SELECT id FROM teacherLink 
            WHERE teacherId = %s AND courseId = %s AND classId = %s AND facultyId = %s AND majorId = %s AND statusId = %s
        """
        cursor.execute(select_query, (teacher_id, course_id, class_id, faculty_id, major_id, 1))
        existing_link = cursor.fetchone()

        if existing_link:
            teacher_link_id = existing_link['id']
            print(f"INFO: Found existing teacher link for teacher ID {teacher_id} with ID: {teacher_link_id}.")
            return teacher_link_id

        # If no existing link is found, insert a new one
        insert_data = {
            "teacherId": teacher_id,
            "courseId": course_id,
            "classId": class_id,
            "facultyId": faculty_id,
            "majorId": major_id,
            "statusId": 1,
            "type": "required"
        }

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO teacherLink ({columns}) VALUES ({placeholders})"

        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        teacher_link_id = cursor.lastrowid
        print(f"INFO: Successfully added new teacher link for teacher ID {teacher_id} with ID: {teacher_link_id}.")
        return teacher_link_id

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add teacher link for teacher ID {teacher_id}: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding teacher link: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_teacher_link_id_by_teacher_id(teacher_id: int) -> Optional[int]:
    """
    Retrieves the latest teacherLink ID from the online-exam database for a given teacherId.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teacherLink WHERE teacherId = %s ORDER BY id DESC LIMIT 1", (teacher_id,))
        teacher_link = cursor.fetchone()
        if teacher_link:
            return teacher_link['id']
        return None
    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_teacher_link_id_by_teacher_id: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_teacher_link_details(teacher_link_id: int) -> Optional[Dict[str, int]]:
    """
    Retrieves details (classId, facultyId, majorId) from the teacherLink table for a given teacher_link_id.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT classId, facultyId, majorId FROM teacherLink WHERE id = %s", (teacher_link_id,))
        link_details = cursor.fetchone()
        if link_details:
            return link_details
        return None
    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_teacher_link_details: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_employee_by_id(employee_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves employee details from the 'employee' table by ID."""
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM employee WHERE id = %s", (employee_id,))
        employee = cursor.fetchone()
        return employee
    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_employee_by_id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_employee_api_token(username: str) -> Optional[str]:
    """
    Retrieves the actual API token for a teacher/employee from the online-exam database.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        # Use DictCursor to access results by column name
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Try finding by username first, then fallback to common patterns if needed
        sql = "SELECT api_token FROM employee WHERE username = %s OR email = %s"
        cursor.execute(sql, (username, f"{username}@tdm.com"))
        row = cursor.fetchone()
        
        if row and row['api_token']:
            logging.info(f"Successfully retrieved API token for employee: {username}")
            return row['api_token']
        else:
            logging.warning(f"No API token found for employee: {username}")
            return None
    except pymysql.Error as e:
        logging.error(f"ERROR: Failed to retrieve API token for employee '{username}': {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_student_status_to_online_exam_db(username: str, class_id: int, faculty_id: int, major_id: int, teacher_link_id: int, role: Optional[str] = None) -> bool:
    """
    Adds a new entry to the 'studentstatus' table in the online-exam database.
    Retrieves studentID from the 'student' table using the username (xId)
    and uses provided class_id, faculty_id, major_id, and teacher_link_id.
    """
    conn = None
    
    # Determine the actual xId used in the student table
    role_clean = str(role).lower().strip() if role else ""
    if role_clean in ['teacher', 'instructor', 'manager']:
        student_xid = f"s-{username}"
    else:
        student_xid = username

    print(f"DEBUG: Entering add_student_status_to_online_exam_db for user: {username}, student_xid: {student_xid}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Get studentID from the 'student' table using the correct xId
        cursor.execute("SELECT id FROM student WHERE xId = %s", (student_xid,))
        student_row = cursor.fetchone()
        if not student_row:
            print(f"ERROR: Student with xId '{student_xid}' not found in online-exam student table. Cannot add student status.")
            return False
        student_id = student_row['id']
        print(f"DEBUG: Retrieved studentID {student_id} for xId {student_xid}.")

        # 2. Check if student status entry already exists based on the unique key
        check_query_unique_key = """
            SELECT teacherLinkSet FROM studentstatus
            WHERE studentID = %s AND classID = %s AND facultyID = %s AND majorID = %s AND statusID = %s
        """
        cursor.execute(check_query_unique_key, (student_id, class_id, faculty_id, major_id, 1))
        existing_student_status = cursor.fetchone()

        if existing_student_status:
            # Entry exists, so update its teacherLinkSet
            update_query = """
                UPDATE studentstatus
                SET teacherLinkSet = %s
                WHERE studentID = %s AND classID = %s AND facultyID = %s AND majorID = %s AND statusID = %s
            """
            cursor.execute(update_query, (teacher_link_id, student_id, class_id, faculty_id, major_id, 1))
            conn.commit()
            print(f"INFO: Updated teacherLinkSet for existing student status entry (studentID: {student_id}) to {teacher_link_id}.")
            return True
        else:
            # No entry exists, proceed with insert
            insert_data = {
                "studentID": student_id,
                "classID": class_id,
                "facultyID": faculty_id,
                "majorID": major_id,
                "teacherLinkSet": teacher_link_id,
                "statusID": 1,
            }

            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            insert_query = f"INSERT INTO studentstatus ({columns}) VALUES ({placeholders})"
            
            print(f"DEBUG: Studentstatus insert query: {insert_query}")
            print(f"DEBUG: Studentstatus insert values: {tuple(insert_data.values())}")

            cursor.execute(insert_query, tuple(insert_data.values()))
            conn.commit()
            print(f"INFO: Successfully added student status for studentID {student_id} to online-exam DB.")
            return True

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to process student status for '{username}' to online-exam DB: {e}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while processing student status for '{username}' to online-exam DB: {e}")
        return False
    finally:
        if conn:
            conn.close()

async def create_exam_in_online_exam_db(exam_data: Dict[str, Any], username: str, online_exam_api_base_url: str, teacher_api_token: str) -> Dict[str, Any]:
    
    if not online_exam_api_base_url:
        return {"status": "error", "message": "Online Exam API base URL not configured."}

    # Use path-based routing (/api/exam) which is more standard for codeHive
    base_url = online_exam_api_base_url.rstrip('/')
    if base_url.endswith('/api'):
        exam_endpoint = f"{base_url}/exam"
    else:
        exam_endpoint = f"{base_url}/api/exam"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Use provided IDs if available, otherwise default to 11.
    exam_data["teacherId"] = exam_data.get("teacherId") or 11
    exam_data["facultyID"] = exam_data.get("facultyID") or 11
    exam_data["majorID"] = exam_data.get("majorID") or 11

    # Add the token to the exam_data before flattening
    exam_data["token"] = teacher_api_token

    # Flatten exam_data for form submission
    # returns a list of tuples like [('link[]', '1'), ('questions[0][title]', 'Q1')]
    flattened_exam_data = flatten_dict_for_form(exam_data)

def _sync_create_exam(exam_endpoint, flattened_exam_data, headers):
    """Internal sync helper to avoid AsyncClient issues in certain environments."""
    with httpx.Client(verify=False) as client:
        return client.post(exam_endpoint, data=flattened_exam_data, headers=headers, timeout=30.0)

async def create_exam_in_online_exam_db(exam_data: Dict[str, Any], username: str, online_exam_api_base_url: str, teacher_api_token: str) -> Dict[str, Any]:
    
    if not online_exam_api_base_url:
        return {"status": "error", "message": "Online Exam API base URL not configured."}

    # Use path-based routing (/api/exam) which is more standard for codeHive
    base_url = online_exam_api_base_url.rstrip('/')
    if base_url.endswith('/api'):
        exam_endpoint = f"{base_url}/exam"
    else:
        exam_endpoint = f"{base_url}/api/exam"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Use provided IDs if available, otherwise default to 11.
    exam_data["teacherId"] = exam_data.get("teacherId") or 11
    exam_data["facultyID"] = exam_data.get("facultyID") or 11
    exam_data["majorID"] = exam_data.get("majorID") or 11

    # Add the token to the exam_data before flattening
    exam_data["token"] = teacher_api_token

    # Flatten exam_data for form submission
    flattened_exam_data = flatten_dict_for_form(exam_data)

    try:
        logging.debug(f"DEBUG: Online Exam API Endpoint: {exam_endpoint}")
        
        # Run sync request in a thread pool to guarantee no AsyncClient sync errors
        response = await run_in_threadpool(_sync_create_exam, exam_endpoint, flattened_exam_data, headers)
        
        # CRITICAL LOGGING: Log the raw response to find out why JSON parsing fails
        logging.debug(f"DEBUG: Online Exam API Status Code: {response.status_code}")
        
        if response.status_code != 200:
            logging.error(f"Online Exam API returned HTTP {response.status_code}. Content snippet: {response.text[:500]}")

        # Try to parse JSON robustly
        try:
            raw_text = response.text.strip()
            # Log small responses which are often PHP errors/notices
            if len(raw_text) < 200:
                logging.debug(f"DEBUG: Online Exam API Small Response: {raw_text}")

            # Find the first '{' and last '}' to strip any PHP notices or HTML
            start_index = raw_text.find('{')
            end_index = raw_text.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_candidate = raw_text[start_index:end_index + 1]
                response_json = json.loads(json_candidate)
            else:
                # If no JSON braces found, try direct parse
                response_json = response.json()
        except (json.JSONDecodeError, Exception) as e:
            logging.error(f"Failed to decode JSON response from Online Exam API. Status Code: {response.status_code}")
            logging.error(f"RAW RESPONSE CONTENT: {response.text}")
            return {"status": "error", "message": f"Invalid JSON response from Online Exam API: {response.text[:100]}"}

        if response_json.get("status") == True:
            return {
                "status": "success",
                "message": "Exam created successfully",
                "exam_id": response_json.get("last"),
                "exam_name": exam_data.get("name"),
                "exam_date_time": exam_data.get("date"),
                "exam_total_time": exam_data.get("duration"),
                "redirect_url": ""
            }
        else:
            error_msg = response_json.get('message') or response_json.get('error') or 'Unknown error'
            
            # SPECIAL HANDLING: If the error is 'you need rules exam-can-publish', retry as a draft
            if "exam-can-publish" in str(error_msg) and exam_data.get("status") != "draft":
                logging.warning("User lacks 'exam-can-publish' permission. Retrying exam creation as 'draft'...")
                exam_data["status"] = "draft"
                # Re-flatten with the new status
                flattened_exam_data_retry = flatten_dict_for_form(exam_data)
                
                retry_response = await run_in_threadpool(_sync_create_exam, exam_endpoint, flattened_exam_data_retry, headers)
                
                # Try to parse retry JSON
                try:
                    retry_raw = retry_response.text.strip()
                    s_idx = retry_raw.find('{')
                    e_idx = retry_raw.rfind('}')
                    if s_idx != -1 and e_idx != -1:
                        retry_json = json.loads(retry_raw[s_idx:e_idx + 1])
                    else:
                        retry_json = retry_response.json()
                        
                    if retry_json.get("status") == True:
                        return {
                            "status": "success",
                            "message": "Exam created as draft (publishing permission missing)",
                            "exam_id": retry_json.get("last"),
                            "exam_name": exam_data.get("name"),
                            "exam_date_time": exam_data.get("date"),
                            "exam_total_time": exam_data.get("duration"),
                            "redirect_url": ""
                        }
                except:
                    pass # Fall through to original error if retry fails to parse

            error_log(f"Online Exam API returned an error status: {error_msg}")
            return {"status": "error", "message": error_msg}

    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error from Online Exam API: {e.response.status_code}. Response snippet: {e.response.text[:500]}")
        return {"status": "error", "message": f"HTTP error from Online Exam API: {e.response.status_code}"}
    except httpx.RequestError as e:
        error_log(f"Network error connecting to Online Exam API: {e}")
        return {"status": "error", "message": f"Network error connecting to Online Exam API: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error in create_exam_in_online_exam_db: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

def clear_student_session_in_online_exam_db(username: str):
    """
    Clears the sessionId and lastLogin for a student in the online-exam database.
    This allows a fresh login from a browser after the backend has made an API call.
    """
    conn = None
    # Ensure lowercase prefix to match PHP logic
    student_xid = f"s-{username.lower()}"
    
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        
        # Clear session for both prefixed and non-prefixed username to be safe
        sql = "UPDATE student SET sessionId = NULL, lastLogin = '0000-00-00 00:00:00' WHERE xId = %s OR xId = %s"
        cursor.execute(sql, (student_xid, username.lower()))
        conn.commit()
        logging.info(f"Successfully cleared PHP session for student: {student_xid}")
    except pymysql.Error as e:
        logging.error(f"ERROR: Failed to clear student session in online-exam DB: {e}")
    finally:
        if conn:
            conn.close()

def log_questions_for_exam(exam_id: int):
    """
    Logs all questions (bankIDs) for a given exam into the banklog table.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Get all bankIDs for the given exam_id from the examdata table
        cursor.execute("SELECT bankId FROM examdata WHERE examId = %s", (exam_id,))
        question_rows = cursor.fetchall()

        if not question_rows:
            print(f"INFO: No questions found in examdata for exam ID {exam_id}. Nothing to log in banklog.")
            return True

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. For each bankId, insert a record into banklog
        bank_logs_to_insert = []
        for row in question_rows:
            bank_logs_to_insert.append((row['bankId'], exam_id, current_time))
        
        if bank_logs_to_insert:
            insert_query = "INSERT INTO banklog (bankID, examID, `time`) VALUES (%s, %s, %s)"
            cursor.executemany(insert_query, bank_logs_to_insert)
            conn.commit()
            print(f"INFO: Successfully logged {len(bank_logs_to_insert)} questions for exam ID {exam_id} in banklog.")

        return True

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        # Check for "Table doesn't exist" error
        if e.args[0] == 1146: # MySQL error code for "Table ... doesn't exist"
            print(f"ERROR: The 'banklog' table does not exist in the '{MYSQL_DB}' database. Please create it.")
            # We can optionally try to create it here.
            # For now, just raising an exception to signal the problem.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The 'banklog' table does not exist. Please create it with columns: id (INT, AUTO_INCREMENT, PRIMARY KEY), bankID (INT), examID (INT), time (DATETIME)."
            ) from e
        else:
            print(f"ERROR: Database operation failed in log_questions_for_exam: {e}")
            # Do not raise HTTPException here, to avoid breaking the publish flow if logging fails for other reasons.
            return False
    finally:
        if conn:
            conn.close()

def get_all_exam_names() -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM exam ORDER BY name ASC")
        exams = cursor.fetchall()
        return exams
    except pymysql.Error as e:
        print(f"ERROR: Failed to retrieve exam names from online-exam DB: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_employee_id_by_email(email: str) -> Optional[int]:
    """
    Retrieves the employee ID from the online-exam database for a given email.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM employee WHERE email = %s", (email,))
        employee = cursor.fetchone()
        if employee:
            return employee['id']
        return None
    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_employee_id_by_email: {e}")
        return None
    finally:
        if conn:
            conn.close()

