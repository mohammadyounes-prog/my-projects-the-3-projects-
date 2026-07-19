import sys
import os
import pymysql
from backend.online_exam_db_connector import get_online_exam_db_connection

def check_rules():
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("\nChecking employees and their rules...")
        cursor.execute('SELECT id, name, email, rules FROM employee')
        employees = cursor.fetchall()
        
        if not employees:
            print("No employees found in 'employee' table.")
        else:
            for e in employees:
                print(f"ID: {e['id']}, Name: {e['name']}, Email: {e['email']}")
                print(f"Rules: {e['rules']}\n")
        
        conn.close()
    except Exception as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    check_rules()
