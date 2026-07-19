import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def remove_duplicate_questions():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Dictionary to store fingerprints and the ID of the first occurrence
    seen_questions = {}
    duplicates_to_remove = []

    # Fetch all questions
    cursor.execute("""
        SELECT question_id, question_text, choice_1, choice_2, choice_3, choice_4, correct_option
        FROM questions
    """)
    all_questions = cursor.fetchall()

    for q in all_questions:
        # Create a tuple as a fingerprint for the question content
        fingerprint = (
            q['question_text'],
            q['choice_1'],
            q['choice_2'],
            q['choice_3'],
            q['choice_4'],
            q['correct_option']
        )

        if fingerprint in seen_questions:
            # This is a duplicate, add its ID to the list for removal
            duplicates_to_remove.append(q['question_id'])
        else:
            # First time seeing this question content
            seen_questions[fingerprint] = q['question_id']

    if duplicates_to_remove:
        print(f"Found {len(duplicates_to_remove)} duplicate questions. Removing them...")
        # Convert list of IDs to a comma-separated string for the IN clause
        placeholders = ','.join('?' * len(duplicates_to_remove))
        cursor.execute(f"DELETE FROM questions WHERE question_id IN ({placeholders})", duplicates_to_remove)
        conn.commit()
        print("Duplicate questions removed successfully.")
    else:
        print("No duplicate questions found.")

    conn.close()

if __name__ == "__main__":
    print(f"Processing database: {DATABASE_FILE}")
    remove_duplicate_questions()
    print("Done.")
