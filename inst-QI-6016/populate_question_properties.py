import sqlite3
import os

# --- Configuration ---
DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'questions.db')

# Define the property types that should be associated with the 'question' audience.
# Format: (Display Name, API Name, Audience Type)
QUESTION_PROPERTIES = [
    ('Question Type', 'question_types', 'question'),
    ('Difficulty Level', 'difficulty_levels', 'question'),
    ('Learning Outcome', 'learning_outcomes', 'question'),
    ('Cognitive Level', 'cognitive_levels', 'question')
]

def populate_question_properties():
    """
    Connects to the database and inserts the necessary property types
    for the 'question' audience if they do not already exist.
    """
    print(f"Connecting to database: {DATABASE_FILE}")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print("Checking and inserting 'question' audience properties into 'property_types' table...")

        for name, api_name, audience_type in QUESTION_PROPERTIES:
            # Check if the property already exists for the given audience
            cursor.execute(
                "SELECT 1 FROM property_types WHERE api_name = ? AND audience_type = ?",
                (api_name, audience_type)
            )
            if cursor.fetchone():
                print(f"- Property '{name}' ('{api_name}') already exists for audience '{audience_type}'. Skipping.")
            else:
                # If it doesn't exist, insert it
                print(f"+ Inserting property '{name}' ('{api_name}') for audience '{audience_type}'...")
                cursor.execute(
                    "INSERT INTO property_types (name, api_name, audience_type) VALUES (?, ?, ?)",
                    (name, api_name, audience_type)
                )
                print(f"  -> Successfully inserted.")

        conn.commit()
        print("\nDatabase population complete.")

    except sqlite3.Error as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure the 'property_types' table exists and the database file is accessible.")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    populate_question_properties()
