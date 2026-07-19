import pymysql
import os
from pathlib import Path
from fastapi import HTTPException, status
import datetime # New import
import re
import json # New import
from typing import Optional # Explicitly import Optional
from typing import Dict, Any, Optional
import httpx
import hashlib # New import for hashing

def flatten_dict_for_form(d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}[{k}]" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict_for_form(v, new_key).items())
        elif isinstance(v, list):
            for i, lv in enumerate(v):
                if isinstance(lv, dict):
                    items.extend(flatten_dict_for_form(lv, f"{new_key}[{i}]").items())
                else:
                    items.append((f"{new_key}[{i}]", lv))
        else:
            items.append((new_key, v))
    return dict(items)

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
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor # Return results as dictionaries
        )
        return conn
    except pymysql.Error as e:
        print(f"ERROR: Could not connect to online-exam MySQL database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {e}"
        )

def add_student_to_online_exam_db(username: str, email: str, raw_password: str, full_name: Optional[str] = None, mobile_phone: Optional[str] = None, country: Optional[str] = "USA") -> bool:
    """
    Adds a new student to the 'student' table in the online-exam database.
    Returns True on success, False on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_student_to_online_exam_db for user: {username}, email: {email}, full_name: {full_name}, mobile: {mobile_phone}, country: {country})")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Check if student already exists by username
        cursor.execute("SELECT id FROM student WHERE xId = %s", (username,))
        existing_student = cursor.fetchone()
        if existing_student:
            print(f"INFO: Student with username '{username}' already exists in online-exam DB (ID: {existing_student['id']}). Skipping insertion.")
            return False

        # Generate the online-exam specific password hash
        online_exam_hashed_password = generate_online_exam_password_hash(raw_password)
        print(f"DEBUG: Generated online-exam hashed password for {username}.")

        # Construct the 'data' JSON field, including email and country
        user_data_json = json.dumps({"street":"", "email": email, "country": country}) # Assuming "street" is an empty string
        print(f"DEBUG: Constructed user_data_json: {user_data_json}")

        insert_data = {
            "xId": username, # User's username as xId
            "name": full_name if full_name else username,
            "pass": online_exam_hashed_password,
            "cityID": 1, # Always 1 as per instruction
            "data": user_data_json, # Email is now part of this JSON
            "addressID": 0, # Changed from addressI back to addressID
            "Value": 0.00, # Always 0.00 as per instruction
            "lastLogin": "0000-00-00 00:00:00", # As per instruction
            "sessionID": None, # (NULL) as per instruction
        }

        # Remove keys with None values to let DB defaults apply or to insert NULL directly
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        print(f"DEBUG: Final insert_data for student table: {insert_data}")

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO student ({columns}) VALUES ({placeholders})"
        print(f"DEBUG: Insert query: {insert_query}")
        print(f"DEBUG: Insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        print(f"INFO: Student '{username}' successfully added to online-exam DB.")
        return True

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add student '{username}' to online-exam DB: {e}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding student '{username}' to online-exam DB: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_course_and_category_to_online_exam_db(username: str):
    """
    Adds a new course named after the current date to the 'course' table and then
    adds a new main category (parent=0) to the 'category' table, named after the username,
    linking it to the newly created or existing daily course.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Add course named after the current date
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        course_name = current_date
        course_id = None

        # Check if course already exists
        cursor.execute("SELECT id FROM course WHERE name = %s", (course_name,))
        existing_course = cursor.fetchone()

        if existing_course:
            course_id = existing_course['id']
            print(f"Course '{course_name}' already exists with ID: {course_id}")
        else:
            # Insert new course
            # Assuming 'name' is the only required field for a basic course entry
            cursor.execute("INSERT INTO course (name) VALUES (%s)", (course_name,))
            conn.commit()
            course_id = cursor.lastrowid
            print(f"Course '{course_name}' added with ID: {course_id}")

        # 2. Add a new main category to the 'category' table, linked to the course
        category_name = username # Use the logged-in username as the category name
        category_parent = 0 # As per user's request

        # Find the next available sequential number for the category name
        base_category_name = username
        next_category_number = 1
        
        # Query for existing categories for this user and course, starting with the base name
        cursor.execute(
            "SELECT name FROM category WHERE courseID = %s AND parent = %s AND name LIKE %s ORDER BY name DESC",
            (course_id, category_parent, f"{base_category_name}-%")
        )
        existing_categories = cursor.fetchall()

        if existing_categories:
            # Extract numbers from existing category names (e.g., "user-1" -> 1)
            numbers = []
            for cat in existing_categories:
                match = re.match(rf"^{base_category_name}-(\d+)$", cat['name'])
                if match:
                    numbers.append(int(match.group(1)))
            if numbers:
                next_category_number = max(numbers) + 1
        
        category_name = f"{base_category_name}-{next_category_number}"

        # Insert new category
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

        return {
            "status": "success",
            "message": f"Category '{category_name}' added for course '{course_name}' with ID: {category_id}.",
            "course_id": course_id,
            "category_id": category_id,
            "course_name": course_name
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
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Create the dynamic part for the filter names
        dynamic_part = f"{course_name}-{username}"

        # 1. Add default filters
        filters_to_add = [
            {
                "name": f"محتوى {dynamic_part}",
                "description": f"محتوى {dynamic_part}",
                "type": "select",
                "value": "وحدة 1,وحدة 2,وحدة 3,وحدة 4,وحدة 5,وحدة 6",
                "courseId": course_id,
                "parent": 0,
                "important": 2,
            },
            {
                "name": f"معرفة {dynamic_part}",
                "description": f"معرفة {dynamic_part}",
                "type": "select",
                "value": "تذكر,فهم,تطبيق,تحليل,تقويم,إبتكار",
                "courseId": course_id,
                "parent": 0,
                "important": 2,
            },
        ]

        for filter_data in filters_to_add:
            # Check if a filter with the same name and courseId already exists
            cursor.execute("SELECT id FROM filters WHERE name = %s AND courseId = %s", (filter_data["name"], course_id))
            if cursor.fetchone():
                print(f"Filter '{filter_data['name']}' already exists for course ID {course_id}. Skipping.")
                continue

            columns = ', '.join(filter_data.keys())
            placeholders = ', '.join(['%s'] * len(filter_data))
            insert_query = f"INSERT INTO filters ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(filter_data.values()))
            print(f"Added filter: {filter_data['name']}")

        # 2. Add default objectives
        
        # First, find the maximum current xId to increment from
        cursor.execute("SELECT MAX(CAST(xId AS UNSIGNED)) as max_xid FROM objective")
        result = cursor.fetchone()
        current_max_xid = result['max_xid'] if result and result['max_xid'] is not None else 0

        objectives_to_add = [
            {"name": "Students will list and identify main ideas from studied materials", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will explain concepts in their own words to demonstrate comprehension.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will summarize information from readings or discussions.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will use learned principles to solve routine problems.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will demonstrate learned procedures in practical tasks.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will differentiate between facts and opinions in various sources.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will assess arguments or solutions based on evidence and logic.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will critique their own or others’ work to suggest improvements.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will design original projects or products that demonstrate learned skills.", "courseId": course_id, "categorySet": str(category_id)},
            {"name": "Students will generate new ideas or hypotheses to address open-ended problems.", "courseId": course_id, "categorySet": str(category_id)},
        ]

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
            print(f"Added objective: {objective_data['name']} with xId: {objective_data['xId']}")

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
    username: str,  # Add username
    teacher_id: int = 11
):
    """
    Inserts a generated question into the 'bank' table of the online-exam database.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # ... (The existing logic for preparing bank_data remains the same)
        title = question_data.get("question_text", "")
        type_mapping = {
            "multiple choice": "mch", "yes no": "yn", "accept reject": "ar",
            "multi answer": "chbox", "text": "text", "hand write": "hw",
            "matching": "match", "open-ended": "open"
        }
        question_type_raw = question_data.get("question_type", "").lower()
        question_type_bank = type_mapping.get(question_type_raw, "mch")
        answers_list = []
        if question_type_bank in ["mch", "chbox"]:
            for i in range(1, 5):
                choice = question_data.get(f"choice_{i}")
                if choice:
                    answers_list.append(choice)
        elif question_type_bank == "open":
            solution_text = question_data.get("solution", "")
            if solution_text:
                answers_list.append(solution_text)
        answers = json.dumps(answers_list)
        correct = question_data.get("correct_option", "")
        if question_type_bank == "mch":
            if correct == "A": correct = "1"
            elif correct == "B": correct = "2"
            elif correct == "C": correct = "3"
            elif correct == "D": correct = "4"
        elif question_type_bank == "chbox":
            if isinstance(correct, list):
                correct = json.dumps(correct)
            else:
                correct = json.dumps([int(correct)]) if str(correct).isdigit() else json.dumps([])
        elif question_type_bank == "open":
            correct = question_data.get("solution", "")
        resources_data = question_data.get("resources", {"question":[],"answers":{}})
        resources = json.dumps(resources_data)
        bank_data = {
            "title": title, "answers": answers, "correct": correct, "teacherId": teacher_id,
            "courseId": course_id, "type": question_type_bank, "categorySet": str(category_id),
            "mark": float(question_data.get("mark") or 5.00),
            "duration": int(round((question_data.get("time_seconds") or 120) / 60)),
            "resources": resources, "trueAnswersCount": 0, "falseAnswersCount": 0, "parent": None,
        }

        columns = ', '.join(bank_data.keys())
        placeholders = ', '.join(['%s'] * len(bank_data))
        insert_query = f"INSERT INTO bank ({columns}) VALUES ({placeholders})"

        cursor.execute(insert_query, tuple(bank_data.values()))
        conn.commit()
        question_id = cursor.lastrowid # Get the ID of the newly inserted question
        print(f"Question '{title[:50]}...' successfully inserted into 'bank' table with ID: {question_id}.")

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

            filterdata_insert_query = "INSERT INTO filtersdata (bankId, filterId, value, type) VALUES (%s, %s, %s, %s)"
            
            cursor.executemany(filterdata_insert_query, filters_to_insert)
            conn.commit()
            print(f"DEBUG: Successfully added {len(filters_to_insert)} entries to filterdata for question ID {question_id}.")

        except pymysql.Error as e:
            print(f"ERROR: Failed to insert into filterdata table for question ID {question_id}: {e}")
        
        filterdata_summary = {
            "filters_added": len(filters_to_insert),
            "details": filters_to_insert
        }
        return {
            "question_id": question_id,
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
    Retrieves the latest course_id and category_id for a given username.
    Assumes the course name is the current date and category name is username-X.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        course_name = current_date

        # Get course_id
        cursor.execute("SELECT id FROM course WHERE name = %s", (course_name,))
        course_row = cursor.fetchone()
        if not course_row:
            print(f"WARNING: Course '{course_name}' not found for user '{username}'.")
            return {"course_id": None, "category_id": None}
        course_id = course_row['id']

        # Get latest category_id for the user within this course
        # Order by ID DESC to get the latest one created
        cursor.execute(
            "SELECT id FROM category WHERE courseID = %s AND name LIKE %s ORDER BY id DESC LIMIT 1",
            (course_id, f"{username}-%")
        )
        category_row = cursor.fetchone()
        if not category_row:
            print(f"WARNING: Category for user '{username}' not found in course '{course_name}'.")
            return {"course_id": course_id, "category_id": None}
        category_id = category_row['id']

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
            (f"{base_class_name}-%-{current_date}",)
        )
        existing_classes = cursor.fetchall()
        
        if existing_classes:
            for cls in existing_classes:
                match = re.search(rf"^{base_class_name}-(\d+)-{current_date}$", cls['name'])
                if match:
                    next_class_number = max(next_class_number, int(match.group(1)) + 1)
        
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
            (f"{base_faculty_name}-%-{current_date}",)
        )
        existing_faculty = cursor.fetchall()
        
        if existing_faculty:
            for fac in existing_faculty:
                match = re.search(rf"^{base_faculty_name}-(\d+)-{current_date}$", fac['name'])
                if match:
                    next_faculty_number = max(next_faculty_number, int(match.group(1)) + 1)
        
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
            (f"{base_major_name}-%-{current_date}",)
        )
        existing_majors = cursor.fetchall()
        
        if existing_majors:
            for maj in existing_majors:
                match = re.search(rf"^{base_major_name}-(\d+)-{current_date}$", maj['name'])
                if match:
                    next_major_number = max(next_major_number, int(match.group(1)) + 1)
        
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
            (f"{base_major_name}-%-{current_date}",)
        )
        existing_majors = cursor.fetchall()
        
        if existing_majors:
            for maj in existing_majors:
                match = re.search(rf"^{base_major_name}-(\d+)-{current_date}$", maj['name'])
                if match:
                    next_major_number = max(next_major_number, int(match.group(1)) + 1)
        
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
            (f"{base_appstatus_name}-%-{current_date}",)
        )
        existing_appstatus = cursor.fetchall()
        
        if existing_appstatus:
            for ad in existing_appstatus:
                match = re.search(rf"^{base_appstatus_name}-(\d+)-{current_date}$", ad['name'])
                if match:
                    next_appstatus_number = max(next_appstatus_number, int(match.group(1)) + 1)
        
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
            (f"{base_faculty_name}-%-{current_date}",)
        )
        existing_faculty = cursor.fetchall()
        
        if existing_faculty:
            for fac in existing_faculty:
                match = re.search(rf"^{base_faculty_name}-(\d+)-{current_date}$", fac['name'])
                if match:
                    next_faculty_number = max(next_faculty_number, int(match.group(1)) + 1)
        
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
            (f"{base_major_name}-%-{current_date}",)
        )
        existing_majors = cursor.fetchall()
        
        if existing_majors:
            for maj in existing_majors:
                match = re.search(rf"^{base_major_name}-(\d+)-{current_date}$", maj['name'])
                if match:
                    next_major_number = max(next_major_number, int(match.group(1)) + 1)
        
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
            (f"{base_appstatus_name}-%-{current_date}",)
        )
        existing_appstatus = cursor.fetchall()
        
        if existing_appstatus:
            for ad in existing_appstatus:
                match = re.search(rf"^{base_appstatus_name}-(\d+)-{current_date}$", ad['name'])
                if match:
                    next_appstatus_number = max(next_appstatus_number, int(match.group(1)) + 1)
        
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

def add_employee_to_online_exam_db(full_name: str, email: str, raw_password: str, mobile_phone: Optional[str] = None) -> bool:
    """
    Adds a new employee (teacher) to the 'employee' table in the online-exam database.
    Returns True on success, False on failure.
    """
    conn = None
    print(f"DEBUG: Entering add_employee_to_online_exam_db for email: {email}, full_name: {full_name}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Check if employee already exists by email
        cursor.execute("SELECT id FROM employee WHERE email = %s", (email,))
        existing_employee = cursor.fetchone()
        if existing_employee:
            print(f"INFO: Employee with email '{email}' already exists in online-exam DB (ID: {existing_employee['id']}). Skipping insertion.")
            return False

        # Generate the online-exam specific password hash
        online_exam_hashed_password = generate_online_exam_password_hash(raw_password)
        print(f"DEBUG: Generated online-exam hashed password for {email}.")

        # Predefined rules for a teacher, as per user's example
        teacher_rules = "admin-zone,resultsReport-can-access,lORep-can-access,qbankRep-can-access,studentsListReport-can-access,exam-can-correct,exam-can-edit,exam-can-add,exam-can-delete,exam-can-publish,exam-can-access,exam-can-view-all,exam-can-unpublish,exam-can-delete-publish,exam-can-duplicate,exam-can-delete-template,exam-can-export,exam-answers-can-export,show-all-exams,que-can-duplicate,qbank-can-import-file,qbank-can-approve-questions,qbank-can-access,que-can-move,que-can-delete,que-can-add,que-can-edit,cat-can-delete,cat-can-add,cat-can-edit"
        
        # Construct the 'data' JSON field
        employee_data_json = json.dumps({
            "address": "",
            "mobile": mobile_phone if mobile_phone else "",
            "facultyId": "" # As per example
        })
        print(f"DEBUG: Constructed employee_data_json: {employee_data_json}")

        insert_data = {
            "name": full_name,
            "email": email,
            "pass": online_exam_hashed_password,
            "rules": teacher_rules,
            "position": "teacher", # As per user's example
            "data": employee_data_json,
            "workGroup": 3, # As per user's example
        }

        # Remove keys with None values if the column does not allow NULL
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        print(f"DEBUG: Final insert_data for employee table: {insert_data}")

        columns = ', '.join(insert_data.keys())
        placeholders = ', '.join(['%s'] * len(insert_data))
        insert_query = f"INSERT INTO employee ({columns}) VALUES ({placeholders})"
        print(f"DEBUG: Insert query: {insert_query}")
        print(f"DEBUG: Insert values: {tuple(insert_data.values())}")
        
        cursor.execute(insert_query, tuple(insert_data.values()))
        conn.commit()
        print(f"INFO: Employee '{full_name}' successfully added to online-exam DB.")

        # --- NEW: Add related entries for the new employee (teacher) ---
        class_id = add_class_for_employee(full_name) # Assuming full_name is sufficient as username
        if class_id is None:
            print(f"ERROR: Failed to add class for employee '{full_name}'.")
            return False

        major_id = add_major_for_employee(full_name) # Assuming full_name is sufficient as username
        if major_id is None:
            print(f"ERROR: Failed to add major for employee '{full_name}'.")
            return False
        
        appstatus_id = add_appstatus_for_employee(full_name) # Assuming full_name is sufficient as username
        if appstatus_id is None:
            print(f"ERROR: Failed to add appstatus for employee '{full_name}'.")
            return False

        print(f"DEBUG: Calling add_faculty_for_employee with class_id: {class_id} and major_id: {major_id}")
        faculty_id = add_faculty_for_employee(full_name, class_id, major_id)
        if faculty_id is None:
            print(f"ERROR: Failed to add faculty for employee '{full_name}'.")
            return False
        # --- END NEW ---

        return True

    except pymysql.Error as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to add employee '{full_name}' to online-exam DB: {e}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding employee '{full_name}' to online-exam DB: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_student_status_to_online_exam_db(username: str) -> bool:
    """
    Adds a new entry to the 'studentstatus' table in the online-exam database.
    Retrieves studentID from the 'student' table using the username (xId).
    """
    conn = None
    print(f"DEBUG: Entering add_student_status_to_online_exam_db for user: {username}")
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # 1. Get studentID from the 'student' table
        cursor.execute("SELECT id FROM student WHERE xId = %s", (username,))
        student_row = cursor.fetchone()
        if not student_row:
            print(f"ERROR: Student with xId '{username}' not found in online-exam student table. Cannot add student status.")
            return False
        student_id = student_row['id']
        print(f"DEBUG: Retrieved studentID {student_id} for username {username}.")

        # 2. Insert into 'studentstatus' table
        insert_data = {
            "studentID": student_id,
            "classID": 7,
            "facultyID": 11,
            "majorID": 11,
            "teacherLinkSet": 29,
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
        print(f"ERROR: Failed to add student status for '{username}' to online-exam DB: {e}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while adding student status for '{username}' to online-exam DB: {e}")
        return False
    finally:
        if conn:
            conn.close()

async def create_exam_in_online_exam_db(exam_data: Dict[str, Any], username: str, online_exam_api_base_url: str) -> Dict[str, Any]:
    error_log(f"DEBUG: create_exam_in_online_exam_db received online_exam_api_base_url: {online_exam_api_base_url}")
    if not online_exam_api_base_url:
        error_log("ONLINE_EXAM_API_BASE_URL environment variable not set.")
        return {"status": "error", "message": "Online Exam API base URL not configured."}

    exam_endpoint = online_exam_api_base_url + "/exam" # Reverted: Appending "/exam" is necessary
    api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMSIsImlzX2FkbWluIjowLCJpc19zdXBlcl9hZG1pbiI6MSwidGVuYW50X2lkI xLCJleHAiOjE3NjI4Njk0MzZ9._jB-hjMVH4OG_I5WXfquoo8_sQGZS5AmX70jj_UfIrU" # Placeholder: Replace with a valid JWT token for Employee 11
    # exam_endpoint_with_token = f"{exam_endpoint}?token={api_token}" # REMOVE THIS LINE

    headers = {
        # "Authorization": f"Bearer {api_token}", # REMOVED
        # "Content-Type": "application/x-www-form-urlencoded" # REMOVED
    }

    # Always send teacherId, facultyID, and majorID as 11 as per user's instruction.
    exam_data["teacherId"] = 11
    exam_data["facultyID"] = 11
    exam_data["majorID"] = 11

    # Add the token to the exam_data before flattening
    exam_data["token"] = api_token # ADDED

    # Flatten exam_data for form submission
    flattened_exam_data = flatten_dict_for_form(exam_data)

    async with httpx.AsyncClient() as client:
        try:
            error_log(f"DEBUG: Calling Online Exam API at: {exam_endpoint}") # Debugging line
            error_log(f"DEBUG: Request Headers: {json.dumps(headers, indent=2)}") # NEW DEBUG LOG (will be empty now)
            response = await client.post(exam_endpoint, data=flattened_exam_data, headers=headers, timeout=30.0) # Pass headers here
            error_log(f"Online Exam API Raw Response - Status: {response.status_code}, Text: {response.text}")
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses

            response_json = response.json()
            if response_json.get("status") == True:
                return {"status": "success", "message": "Exam created successfully", "exam_id": response_json.get("last")}
            else:
                error_log(f"Online Exam API returned an error: {response_json.get('message', 'Unknown error')}")
                return {"status": "error", "message": response_json.get("message", "Failed to create exam in online-exam system.")}

        except httpx.HTTPStatusError as e:
            error_log(f"HTTP error creating exam: {e.response.status_code} - {e.response.text}")
            return {"status": "error", "message": f"HTTP error from Online Exam API: {e.response.status_code}"}
        except httpx.RequestError as e:
            error_log(f"Network error creating exam: {e}")
            return {"status": "error", "message": f"Network error connecting to Online Exam API: {e}"}
        except json.JSONDecodeError:
            error_log(f"Failed to decode JSON response from Online Exam API. Status Code: {response.status_code}, Headers: {response.headers}, Response Text: {response.text}")
            return {"status": "error", "message": "Invalid JSON response from Online Exam API."}
        except Exception as e:
            error_log(f"Unexpected error in create_exam_in_online_exam_db: {e}")
            return {"status": "error", "message": f"An unexpected error occurred: {e}"}

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
