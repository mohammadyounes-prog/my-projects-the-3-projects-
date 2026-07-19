import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '../', 'questions.db')

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def add_name_ar_column(table_name: str):
    """Adds a 'name_ar' column to the specified table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if column already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if 'name_ar' not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN name_ar TEXT")
            logging.info(f"Added 'name_ar' column to table '{table_name}'.")
        else:
            logging.info(f"'name_ar' column already exists in table '{table_name}'. Skipping.")
        conn.commit()
    except sqlite3.OperationalError as e:
        logging.error(f"Error adding 'name_ar' column to '{table_name}': {e}")
    finally:
        conn.close()

def dump_table_content(table_name: str):
    """Dumps relevant columns of a table to the log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]

        select_columns = []
        if "id" in column_names: select_columns.append("id")
        if "name" in column_names: select_columns.append("name")
        if "api_name" in column_names: select_columns.append("api_name")
        if "name_ar" in column_names: select_columns.append("name_ar")

        if not select_columns:
            logging.warning(f"No relevant columns (id, name, api_name, name_ar) found in {table_name}.")
            return

        select_clause = ", ".join(select_columns)
        cursor.execute(f"SELECT {select_clause} FROM {table_name}")
        rows = cursor.fetchall()
        logging.info(f"--- Content of '{table_name}' ---")
        for row in rows:
            logging.info(dict(row))
        logging.info(f"--- End of '{table_name}' content ---")
    except sqlite3.OperationalError as e:
        logging.error(f"Error dumping content for '{table_name}': {e}")
    finally:
        conn.close()


def populate_arabic_data():
    """Populates sample Arabic data for the 'name_ar' column in relevant tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Difficulty Levels ---
    table_name = "difficulty_levels"
    add_name_ar_column(table_name) # Ensure column exists first
    try:
        data_to_update = {
            "Easy": "سهل",
            "Medium": "متوسط",
            "Hard": "صعب"
        }
        for english_name, arabic_name in data_to_update.items():
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE name = ?", (arabic_name, english_name))
        conn.commit()
        logging.info(f"Populated 'name_ar' for '{table_name}'.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # --- Cognitive Levels ---
    table_name = "cognitive_levels"
    add_name_ar_column(table_name)
    try:
        data_to_update = {
            "Remembering": "تذكر",
            "Understanding": "فهم",
            "Applying": "تطبيق",
            "Analyzing": "تحليل",
            "Evaluating": "تقييم",
            "Creating": "إنشاء"
        }
        for english_name, arabic_name in data_to_update.items():
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE name = ?", (arabic_name, english_name))
        conn.commit()
        logging.info(f"Populated 'name_ar' for '{table_name}'.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # --- Learning Outcomes ---
    table_name = "learning_outcomes"
    add_name_ar_column(table_name)
    try:
        # This table might have more dynamic data, so we'll add generic if not present
        # Or, ideally, the user would provide specific translations.
        # For now, let's just ensure the column is there.
        # If there's existing data, we can update it.
        # Example: select existing 'name's and map them.
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_outcomes = cursor.fetchall()
        for outcome in existing_outcomes:
            # Placeholder: In a real scenario, you'd translate 'outcome['name']'
            generic_arabic = f"مخرج التعلم {outcome['name']}" # "Learning Outcome {English Name}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, outcome['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")
    
    # --- Question Types ---
    table_name = "question_types"
    add_name_ar_column(table_name)
    try:
        data_to_update = {
            "Multiple Choice": "اختيار من متعدد",
            "True/False": "صح/خطأ",
            "Short Answer": "إجابة قصيرة",
            "Essay": "مقالي",
            "Open-ended": "مفتوح النهاية"
        }
        for english_name, arabic_name in data_to_update.items():
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE name = ?", (arabic_name, english_name))
        conn.commit()
        logging.info(f"Populated 'name_ar' for '{table_name}'.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # --- Property Types (table holding metadata about dynamic properties) ---
    table_name = "property_types"
    add_name_ar_column(table_name) # Ensure column exists first
    try:
        data_to_update = {
            "school_types": "أنواع المدارس",
            "school_subjects": "المواد الدراسية",
            "school_years": "السنوات الدراسية",
            "university_majors": "التخصصات الجامعية",
            "university_courses": "المساقات الجامعية",
            "university_materials": "المواد الجامعية",
            "university_semesters": "الفصول الدراسية",
            "companies": "الشركات",
            "departments": "الأقسام",
            "job_roles": "المسميات الوظيفية",
            "gender": "النوع" # Assuming 'gender' is also a property type
        }
        for english_api_name, arabic_name in data_to_update.items():
            # Use api_name for WHERE clause as it's unique identifier for these properties
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE api_name = ?", (arabic_name, english_api_name))
        conn.commit()
        logging.info(f"Populated 'name_ar' for '{table_name}'.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")


    # --- INDIVIDUAL LOOKUP TABLES FOR DYNAMIC PROPERTIES ---
    # These tables contain the actual selectable values for dynamic dropdowns
    
    # school_types
    table_name = "school_types"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_types = cursor.fetchall()
        for item in existing_types:
            # Example placeholder translations - user should refine
            generic_arabic = f"نوع المدرسة {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # school_subjects
    table_name = "school_subjects"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_subjects = cursor.fetchall()
        for item in existing_subjects:
            generic_arabic = f"موضوع {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")
    
    # school_years
    table_name = "school_years"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_years = cursor.fetchall()
        for item in existing_years:
            generic_arabic = f"سنة {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # university_majors
    table_name = "university_majors"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_majors = cursor.fetchall()
        for item in existing_majors:
            generic_arabic = f"تخصص جامعي {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # university_courses
    table_name = "university_courses"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_courses = cursor.fetchall()
        for item in existing_courses:
            generic_arabic = f"مساق جامعي {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # university_materials
    table_name = "university_materials"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_materials = cursor.fetchall()
        for item in existing_materials:
            generic_arabic = f"مادة جامعية {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # university_semesters
    table_name = "university_semesters"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_semesters = cursor.fetchall()
        for item in existing_semesters:
            generic_arabic = f"فصل دراسي {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # companies
    table_name = "companies"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_companies = cursor.fetchall()
        for item in existing_companies:
            generic_arabic = f"شركة {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # departments
    table_name = "departments"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_departments = cursor.fetchall()
        for item in existing_departments:
            generic_arabic = f"قسم {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # job_roles
    table_name = "job_roles"
    add_name_ar_column(table_name)
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE name_ar IS NULL OR name_ar = ''")
        existing_job_roles = cursor.fetchall()
        for item in existing_job_roles:
            generic_arabic = f"دور وظيفي {item['name']}"
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE id = ?", (generic_arabic, item['id']))
        conn.commit()
        logging.info(f"Populated/updated 'name_ar' for '{table_name}' with generic translations.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    # gender
    table_name = "gender"
    add_name_ar_column(table_name)
    try:
        data_to_update = {
            "Male": "ذكر",
            "Female": "أنثى",
            "Other": "أخرى"
        }
        for english_name, arabic_name in data_to_update.items():
            cursor.execute(f"UPDATE {table_name} SET name_ar = ? WHERE name = ?", (arabic_name, english_name))
        conn.commit()
        logging.info(f"Populated 'name_ar' for '{table_name}'.")
    except Exception as e:
        logging.error(f"Error populating 'name_ar' for '{table_name}': {e}")

    conn.close()

if __name__ == "__main__":
    logging.info("Starting database migration to add 'name_ar' columns and populate with Arabic data...")
    populate_arabic_data()
    dump_table_content("property_types") # Dump property_types content
    logging.info("Database migration completed.")
