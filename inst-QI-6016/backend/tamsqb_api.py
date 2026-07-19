import pymysql
import json
from typing import List, Dict, Any
from online_exam_db_connector import get_online_exam_db_connection
import datetime

def get_courses_for_user(username: str):
    """
    Retrieves the courses for a given user from the online-exam database.
    Courses are identified by the 'crs-username-number' naming convention.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        # Construct the expected course name pattern
        course_name_pattern = f"crs-{username}-%"

        # Get course details that match the pattern for the current user
        cursor.execute("SELECT id, name FROM course WHERE name LIKE %s ORDER BY name DESC", (course_name_pattern,))
        courses = cursor.fetchall()

        return courses

    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_courses_for_user: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_questions_for_course(course_id: int):
    """
    Retrieves questions for a given course from the 'bank' table of the online-exam database.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                b.id AS question_id,
                b.title AS question_text,
                b.answers,
                b.correct AS correct_option,
                b.type AS question_type,
                b.mark,
                b.duration,
                b.resources,
                GROUP_CONCAT(f.name || ':' || fd.value) AS filters_data
            FROM
                bank b
            LEFT JOIN
                filtersdata fd ON b.id = fd.bankId
            LEFT JOIN
                filters f ON fd.filterId = f.id
            WHERE
                b.courseId = %s
            GROUP BY
                b.id
            ORDER BY
                b.id
        """
        cursor.execute(query, (course_id,))
        questions = cursor.fetchall()

        # Parse JSON fields and format as needed
        for q in questions:
            if q['answers']:
                q['answers'] = json.loads(q['answers'])
            if q['resources']:
                q['resources'] = json.loads(q['resources'])
            
            # Reconstruct filters into a dictionary for easier frontend processing
            q['filters'] = {}
            if q['filters_data']:
                # The GROUP_CONCAT might return a single string "filter1:value1,filter2:value2"
                # Need to split by comma, then by colon.
                for item in q['filters_data'].split(','):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        q['filters'][key] = value
            del q['filters_data'] # Remove the raw concatenated string

        return questions

    except pymysql.Error as e:
        print(f"ERROR: Database operation failed in get_questions_for_course: {e}")
        return []
    finally:
        if conn:
            conn.close()
