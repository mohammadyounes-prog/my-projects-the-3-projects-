import sqlite3
import os
import datetime
from typing import Optional

# Assuming database.py is in the same directory
from database import get_db_connection, insert_question, get_lookup_id_by_name

def delete_all_questions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions")
    conn.commit()
    conn.close()
    print("All questions deleted from the database.")

def insert_dummy_questions(num_questions: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get IDs for common lookup values
    difficulty_id = get_lookup_id_by_name('difficulty_levels', 'Easy')
    cognitive_id = get_lookup_id_by_name('cognitive_levels', 'Remembering')
    learning_outcome_id = get_lookup_id_by_name('learning_outcomes', 'Identify basic facts')
    question_type_id = get_lookup_id_by_name('question_types', 'multiple_choice')
    school_type_id = get_lookup_id_by_name('school_types', 'Public')
    subject_id = get_lookup_id_by_name('school_subjects', 'Mathematics')
    year_id = get_lookup_id_by_name('school_years', 'Grade 1')

    for i in range(1, num_questions + 1):
        question_data = {
            "question_text": f"This is dummy question {i}. What is {i} + {i}?",
            "choice_1": str(i*2),
            "choice_2": str(i*2 + 1),
            "choice_3": str(i*2 - 1),
            "choice_4": "None of the above",
            "correct_option": str(i*2),
            "difficulty_level": "Easy",
            "cognitive_level": "Remembering",
            "learning_outcome": "Identify basic facts",
            "question_type": "multiple_choice",
            "school_type": "Public",
            "subject": "Mathematics",
            "year": "Grade 1",
            "author_creator": "Reset Script",
            "date_created": str(datetime.date.today()),
            "status": "pending",
            "mark": 1,
            "time_seconds": 60,
            "discriminating_factor": 0.5,
            "audience_type": "school" # Assuming 'school' for dummy questions
        }
        # insert_question expects user_id and task_id, providing defaults for script
        insert_question(question_data, user_id=1, task_id=1) # Assuming user_id 1 and task_id 1 exist or are handled
        print(f"Inserted dummy question {i}.")
    conn.close()
    print(f"{num_questions} dummy questions inserted.")

if __name__ == "__main__":
    delete_all_questions()
    insert_dummy_questions(20)
    print("Database reset complete: All questions deleted, 20 new dummy questions inserted.")
