import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.database import insert_question, get_lookup_data_list

def populate_dummy_questions():
    print("Populating database with 100 dummy questions...")

    # Get valid lookup values
    try:
        difficulty_levels = get_lookup_data_list('difficulty_levels')
        cognitive_levels = get_lookup_data_list('cognitive_levels')
        learning_outcomes = get_lookup_data_list('learning_outcomes')

        if not all([difficulty_levels, cognitive_levels, learning_outcomes]):
            print("Error: Could not retrieve lookup data. Make sure the database is set up correctly.")
            return

    except Exception as e:
        print(f"Error fetching lookup data: {e}")
        return

    for i in range(100):
        question_data = {
            "question_text": f"This is dummy question number {i+1}. What is {i+1} + {i+1}?",
            "choice_1": f"{2*(i+1)}",
            "choice_2": f"{2*(i+1) + 1}",
            "choice_3": f"{2*(i+1) - 1}",
            "choice_4": "None of the above",
            "correct_option": f"{2*(i+1)}",
            "difficulty_level": difficulty_levels[i % len(difficulty_levels)],
            "cognitive_level": cognitive_levels[i % len(cognitive_levels)],
            "learning_outcome": learning_outcomes[i % len(learning_outcomes)],
            "author_creator": "Dummy Data Script",
            "mark": 1,
            "time_seconds": 60,
            "discriminating_factor": 0.5,
            "status": "pending"
        }
        try:
            insert_question(question_data)
            print(f"Inserted dummy question {i+1}/100")
        except Exception as e:
            print(f"Error inserting dummy question {i+1}: {e}")

    print("Finished populating dummy questions.")

if __name__ == "__main__":
    populate_dummy_questions()
