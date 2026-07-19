
import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from backend.online_exam_db_connector import get_online_exam_db_connection

try:
    conn = get_online_exam_db_connection()
    cur = conn.cursor()
    
    print("--- Searching Student Table ---")
    cur.execute("SELECT id, xId, name FROM student WHERE xId LIKE '%teacher110%'")
    students = cur.fetchall()
    print(f"Found {len(students)} students:")
    for s in students:
        print(s)
        
    print("
--- Searching Employee Table ---")
    cur.execute("SELECT id, name, email FROM employee WHERE name LIKE '%teacher110%' OR email LIKE '%teacher110%'")
    employees = cur.fetchall()
    print(f"Found {len(employees)} employees:")
    for e in employees:
        print(e)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
