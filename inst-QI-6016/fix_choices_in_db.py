import sqlite3
import re
import os
from pathlib import Path

def fix_choices_in_db():
    db_path = Path(__file__).resolve().parent.parent / 'questions.db'
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Select all questions that might have "Choice" or "Answer" in their choices
        cursor.execute("SELECT question_id, choice_1, choice_2, choice_3, choice_4 FROM questions")
        questions_to_update = cursor.fetchall()

        updated_count = 0
        for q_id, c1, c2, c3, c4 in questions_to_update:
            choices = [c1, c2, c3, c4]
            updated_choices = []
            needs_update = False

            for choice in choices:
                if choice is not None:
                    # Remove "Choice", "Answer", "خيارات", "اختيار", "إجابة" (case-insensitive) from the start
                    cleaned_choice = re.sub(r'^(Choice|Answer|خيارات|اختيار|إجابة)\s*', '', choice, flags=re.IGNORECASE).strip()
                    if cleaned_choice != choice:
                        needs_update = True
                    updated_choices.append(cleaned_choice)
                else:
                    updated_choices.append(None)
            
            if needs_update:
                cursor.execute(
                    "UPDATE questions SET choice_1 = ?, choice_2 = ?, choice_3 = ?, choice_4 = ? WHERE question_id = ?",
                    (*updated_choices, q_id)
                )
                updated_count += 1
        
        conn.commit()
        print(f"Successfully processed {len(questions_to_update)} questions. Updated {updated_count} questions.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_choices_in_db()
