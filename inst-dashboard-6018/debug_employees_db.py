import mysql.connector
import json

def check_employees():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': '3307',
        'database': 'schooldemo12'
    }
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        # Check specific teachers
        print("--- Employees Info ---")
        cursor.execute("SELECT id, name, email, rules FROM employee")
        employees = cursor.fetchall()
        for emp in employees:
            print(f"ID: {emp['id']}, Name: {emp['name']}, Email: {emp['email']}, Rules: {emp['rules']}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_employees()
