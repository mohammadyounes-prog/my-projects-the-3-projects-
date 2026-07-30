import sqlite3
import datetime

DATABASE_FILE = 'questions.db'
HASHED_PASSWORD = '$2b$12$iTqkspYn5KVAkWcLjbmVBOF6lhbwdDhbpXcFjuuw0chF64kbdShla' # a hash for "test"

def populate_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create user test2 with id 2
    try:
        cursor.execute("INSERT INTO users (id, username, password, is_admin) VALUES (?, ?, ?, ?)", (2, 'test2', HASHED_PASSWORD, 0))
        print("User 'test2' created with id 2.")
    except sqlite3.IntegrityError:
        print("User with id 2 already exists.")

    # Create user test3 
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ('test3', HASHED_PASSWORD, 0))
        print("User 'test3' created.")
    except sqlite3.IntegrityError:
        print("User 'test3' already exists.")

    # Insert a question for user 1
    try:
        cursor.execute("""INSERT INTO questions 
            (author_creator, date_created, question_text, choice_1, choice_2, choice_3, choice_4, correct_option, 
            difficulty_level_id, cognitive_level_id, learning_outcome_id, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            ('tdmsystems', str(datetime.date.today()), 'What is the capital of France?', 'Berlin', 'Madrid', 'Paris', 'Rome', 'Paris', 1, 1, 1, 'approved', 1))
        print("Inserted question for user 1.")
    except Exception as e:
        print(f"Error inserting question for user 1: {e}")

    # Insert a question for user 2
    try:
        cursor.execute("""INSERT INTO questions 
            (author_creator, date_created, question_text, choice_1, choice_2, choice_3, choice_4, correct_option, 
            difficulty_level_id, cognitive_level_id, learning_outcome_id, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            ('test2', str(datetime.date.today()), 'What is 2 + 2?', '3', '4', '5', '6', '4', 1, 1, 1, 'approved', 2))
        print("Inserted question for user 2.")
    except Exception as e:
        print(f"Error inserting question for user 2: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_database()
