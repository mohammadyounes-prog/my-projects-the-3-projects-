import sqlite3

def get_db_connection():
    conn = sqlite3.connect('questions.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_property_types_by_audience(audience_type: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, api_name, audience_type FROM property_types WHERE audience_type = ?", (audience_type,))
    property_types = cursor.fetchall()
    conn.close()
    return [dict(pt) for pt in property_types]

if __name__ == "__main__":
    print("General Property Types:")
    general_props = get_property_types_by_audience('general')
    for prop in general_props:
        print(prop)

    print("\nQuestion Property Types:")
    question_props = get_property_types_by_audience('question')
    for prop in question_props:
        print(prop)
