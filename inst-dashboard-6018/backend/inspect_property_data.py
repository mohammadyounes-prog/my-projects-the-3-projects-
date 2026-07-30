import sqlite3
import os
from pathlib import Path

# Determine the absolute path to the database file
DATABASE_FILE = os.path.join(os.path.dirname(__file__), '../', 'questions.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def inspect_question_properties():
    print(f"--- Inspecting 'question' audience properties from '{DATABASE_FILE}' ---")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Get property types for audience_type = 'question'
        cursor.execute("SELECT id, name, api_name FROM property_types WHERE audience_type = 'question'")
        property_types = cursor.fetchall()

        if not property_types:
            print("No property types found for audience_type 'question'.")
            return

        print("\nFound Property Types for 'question' audience:")
        print("ID | Name                  | API Name")
        print("---|-----------------------|-----------")
        for pt in property_types:
            print(f"{pt['id']:<2} | {pt['name']:<21} | {pt['api_name']}")
        
        print("\n--- Inspecting values for each property type ---")
        for pt in property_types:
            api_name = pt['api_name']
            print(f"\nProperty Type: '{pt['name']}' (API Name: '{api_name}')")
            
            try:
                # 2. Get values for each property type (from its corresponding lookup table)
                cursor.execute(f"SELECT id, name FROM {api_name}")
                values = cursor.fetchall()

                if not values:
                    print(f"  No values found in table '{api_name}'.")
                else:
                    print(f"  Values in table '{api_name}':")
                    print("  ID | Name")
                    print("  ---|-----------")
                    for val in values:
                        print(f"  {val['id']:<2} | {val['name']}")
            except sqlite3.OperationalError as e:
                print(f"  Error: Table '{api_name}' does not exist. ({e})")
            except Exception as e:
                print(f"  An unexpected error occurred while querying table '{api_name}': {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_question_properties()
