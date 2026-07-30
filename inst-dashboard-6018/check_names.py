import pymysql

config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'root',
    'database': 'schooldemo12',
    'cursorclass': pymysql.cursors.DictCursor
}

def check_student_names():
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        print("--- LATEST STUDENTS ---")
        cursor.execute("SELECT id, xId, name FROM student ORDER BY id DESC LIMIT 5")
        for s in cursor.fetchall():
            print(f"ID: {s['id']} | Login: {s['xId']} | Name: {s['name']}")

        print("--- LATEST EMPLOYEES ---")
        cursor.execute("SELECT id, name, email FROM employee ORDER BY id DESC LIMIT 5")
        for e in cursor.fetchall():
            print(f"ID: {e['id']} | Name: {e['name']} | Email: {e['email']}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_student_names()
