import sys
import os
import logging

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.online_exam_db_connector import get_online_exam_db_connection
import pymysql

logging.basicConfig(level=logging.INFO)

print("Script started...")
try:
    print("Attempting to connect...")
    conn = get_online_exam_db_connection()
    print("Connected successfully.")
    cursor = conn.cursor()
    
    print("Checking students...")
    cursor.execute('SELECT id, xId, name FROM student ORDER BY id DESC LIMIT 10')
    students = cursor.fetchall()
    if not students:
        print("No students found in 'student' table.")
    for s in students:
        print(s)
        
    print("\nChecking employees...")
    cursor.execute('SELECT id, name, email FROM employee ORDER BY id DESC LIMIT 10')
    employees = cursor.fetchall()
    if not employees:
        print("No employees found in 'employee' table.")
    for e in employees:
        print(e)
        
    conn.close()
except pymysql.Error as e:
    print(f"MySQL Error: {e}")
except Exception as ex:
    print(f"General Error: {ex}")
    import traceback
    traceback.print_exc()
