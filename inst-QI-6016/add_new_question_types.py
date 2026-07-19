import sqlite3
import logging

def add_new_question_types():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    
    new_types = [
        ('Yes/No', 'نعم/لا', 'yes_no'),
        ('Multiple Answer', 'إجابات متعددة', 'multiple_answer'),
        ('Accept/Reject', 'قبول/رفض', 'accept_reject'),
        ('Text (Fill in the blank)', 'نص (إكمال الفراغ)', 'text')
    ]
    
    for name, name_ar, api_name in new_types:
        try:
            cursor.execute("""
                INSERT INTO question_types (name, name_ar, api_name, audience_type, created_by)
                VALUES (?, ?, ?, 'general', 38)
            """, (name, name_ar, api_name))
            print(f"Added question type: {name}")
        except sqlite3.IntegrityError:
            print(f"Question type already exists: {name}")
            # Try to update it instead to ensure api_name is correct
            cursor.execute("""
                UPDATE question_types 
                SET name_ar = ?, api_name = ? 
                WHERE name = ?
            """, (name_ar, api_name, name))
            print(f"Updated question type: {name}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_new_question_types()
