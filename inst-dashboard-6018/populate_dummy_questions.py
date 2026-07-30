import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import datetime
from database import insert_question, get_lookup_id_by_name, get_db_connection
from sqlite3 import IntegrityError

# Ensure lookup tables are populated if they are empty
def populate_lookup_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Difficulty Levels
    cursor.execute("CREATE TABLE IF NOT EXISTS difficulty_levels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    for level in ["Easy", "Medium", "Hard"]:
        cursor.execute("INSERT OR IGNORE INTO difficulty_levels (name) VALUES (?)", (level,))

    # Cognitive Levels
    cursor.execute("CREATE TABLE IF NOT EXISTS cognitive_levels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    for level in ["Remembering", "Understanding", "Applying", "Analyzing", "Evaluating", "Creating"]:
        cursor.execute("INSERT OR IGNORE INTO cognitive_levels (name) VALUES (?)", (level,))

    # Learning Outcomes
    cursor.execute("CREATE TABLE IF NOT EXISTS learning_outcomes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    for outcome in ["Identify basic facts", "Explain concepts", "Solve problems", "Analyze situations", "Evaluate theories", "Design solutions"]:
        cursor.execute("INSERT OR IGNORE INTO learning_outcomes (name) VALUES (?)", (outcome,))

    conn.commit()
    conn.close()

# Call this function to ensure lookup tables are ready
populate_lookup_tables()

dummy_questions = [
    {
        "question_text": "What is the capital of France?",
        "choice_1": "Berlin",
        "choice_2": "Madrid",
        "choice_3": "Paris",
        "choice_4": "Rome",
        "correct_option": "Paris",
        "difficulty_level": "Easy",
        "cognitive_level": "Remembering",
        "learning_outcome": "Identify basic facts",
        "author_creator": "System",
        "date_created": str(datetime.date.today()),
        "variables": {"var1": "value1", "var2": "value2"}
    },
    {
        "question_text": "Which planet is known as the Red Planet?",
        "choice_1": "Earth",
        "choice_2": "Mars",
        "choice_3": "Jupiter",
        "choice_4": "Venus",
        "correct_option": "Mars",
        "difficulty_level": "Easy",
        "cognitive_level": "Remembering",
        "learning_outcome": "Identify basic facts",
        "author_creator": "System",
        "date_created": str(datetime.date.today()),
        "variables": {"planet_name": "Mars"}
    },
    {
        "question_text": "Explain the concept of photosynthesis in simple terms.",
        "correct_option": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water.",
        "difficulty_level": "Medium",
        "cognitive_level": "Understanding",
        "learning_outcome": "Explain concepts",
        "author_creator": "System",
        "date_created": str(datetime.date.today()),
        "variables": {}
    },
    {
        "question_text": "What is the primary function of the human heart?",
        "choice_1": "To filter blood",
        "choice_2": "To pump blood throughout the body",
        "choice_3": "To produce hormones",
        "choice_4": "To regulate body temperature",
        "correct_option": "To pump blood throughout the body",
        "difficulty_level": "Easy",
        "cognitive_level": "Remembering",
        "learning_outcome": "Identify basic facts",
        "author_creator": "System",
        "date_created": str(datetime.date.today()),
        "variables": {"organ": "heart"}
    },
    {
        "question_text": "Describe the main steps involved in the water cycle.",
        "correct_option": "The water cycle involves evaporation (water turning into vapor), condensation (vapor forming clouds), precipitation (water falling as rain/snow), and collection (water gathering in bodies of water).",
        "difficulty_level": "Medium",
        "cognitive_level": "Understanding",
        "learning_outcome": "Explain concepts",
        "author_creator": "System",
        "date_created": str(datetime.date.today()),
        "variables": {"cycle": "water"}
    }
]

print("Populating database with dummy questions...")
for q_data in dummy_questions:
    try:
        inserted_id = insert_question(q_data)
        print(f"Successfully inserted question: '{q_data['question_text']}' with ID: {inserted_id}")
    except ValueError as e:
        print(f"Error inserting question '{q_data['question_text']}': {e}")
    except IntegrityError as e:
        print(f"Question '{q_data['question_text']}' already exists or another integrity error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for '{q_data['question_text']}': {e}")

print("Dummy question population complete.")
