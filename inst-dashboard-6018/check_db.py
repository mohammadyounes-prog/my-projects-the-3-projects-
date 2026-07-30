import sqlite3

def check_questions():
    conn = sqlite3.connect('questions.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- Questions Table ---")
    try:
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()
        if not questions:
            print("No questions found.")
        else:
            for row in questions:
                print(dict(row))
    except sqlite3.OperationalError as e:
        print(f"Error querying questions table: {e}")

    print("\n--- Users Table ---")
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if not users:
            print("No users found.")
        else:
            for row in users:
                print(dict(row))
    except sqlite3.OperationalError as e:
        print(f"Error querying users table: {e}")

    conn.close()

if __name__ == "__main__":
    check_questions()
