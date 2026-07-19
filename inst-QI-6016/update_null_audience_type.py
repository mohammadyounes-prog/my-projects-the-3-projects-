import sqlite3
import os

db_path = 'questions.db'

def get_user_audience_type(cursor, user_id):
    cursor.execute("SELECT audience_type FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    return result['audience_type'] if result else None

def update_null_audience_types():
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("Starting migration to update NULL audience_type in questions table...")

        # Select questions where audience_type is NULL
        cursor.execute("SELECT question_id, user_id FROM questions WHERE audience_type IS NULL")
        questions_to_update = cursor.fetchall()

        if not questions_to_update:
            print("No questions found with NULL audience_type. Migration complete.")
            return

        print(f"Found {len(questions_to_update)} questions with NULL audience_type to update.")

        updated_count = 0
        for q in questions_to_update:
            question_id = q['question_id']
            user_id = q['user_id']

            if user_id:
                user_audience_type = get_user_audience_type(cursor, user_id)
                if user_audience_type:
                    cursor.execute("UPDATE questions SET audience_type = ? WHERE question_id = ?", (user_audience_type, question_id))
                    updated_count += 1
                    print(f"Updated QID: {question_id} (UID: {user_id}) with Audience: {user_audience_type}")
                else:
                    print(f"Warning: Could not find audience_type for UID: {user_id} (QID: {question_id}). Skipping.")
            else:
                print(f"Warning: QID: {question_id} has NULL user_id. Skipping.")

        conn.commit()
        print(f"Migration complete. Successfully updated {updated_count} questions.")

    except sqlite3.Error as e:
        print(f"SQLite error during migration: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_null_audience_types()
