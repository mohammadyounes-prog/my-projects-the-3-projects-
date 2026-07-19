import sqlite3
import json

source_db_path = "D:\\QuestionRetrieval\\new-q-bank\\working-eorkin- afte -q-bank\\questions.db"
target_db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

def get_lookup_id_by_name(conn, table_name, name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table_name} WHERE name = ?", (name,))
    result = cursor.fetchone()
    return result[0] if result else None

try:
    source_conn = sqlite3.connect(source_db_path)
    source_conn.row_factory = sqlite3.Row # Enable column access by name
    target_conn = sqlite3.connect(target_db_path)
    target_conn.row_factory = sqlite3.Row # Enable column access by name

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Get source questions table info
    source_cursor.execute("PRAGMA table_info(questions);")
    source_columns_info = source_cursor.fetchall()
    source_column_names = [col[1] for col in source_columns_info]

    # Get target questions table info
    target_cursor.execute("PRAGMA table_info(questions);");
    target_columns_info = target_cursor.fetchall()
    target_column_names = [col[1] for col in target_columns_info]

    # Columns that exist in both and we want to directly copy
    direct_copy_columns = [
        'question_id', 'author_creator', 'date_created', 'question_text',
        'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_option',
        'mark', 'time_seconds', 'discriminating_factor', 'variables'
    ]

    # Columns that need lookup conversion
    lookup_columns = {
        'difficulty_level_id': 'difficulty_levels',
        'cognitive_level_id': 'cognitive_levels',
        'learning_outcome_id': 'learning_outcomes',
        'question_type_id': 'question_types',
        'school_type_id': 'school_types',
        'subject_id': 'school_subjects',
        'year_id': 'school_years',
        'major_id': 'university_majors',
        'course_id': 'university_courses',
        'material_id': 'university_materials',
        'semester_id': 'university_semesters',
        'company_id': 'companies',
        'department_id': 'departments',
        'job_role_id': 'job_roles'
    }

    # Default values for columns that might be new in target or missing in source
    default_values = {
        'status': 'pending',
        'user_id': None, # Assuming user_id will be handled separately or can be null
        'task_id': None,
        'audience_type': 'general',
        'tenant_id': None, # Assuming tenant_id will be handled separately or can be null
        'approved_by': None,
        'approved_at': None,
        'rejected_by': None,
        'rejected_at': None,
        'edited_by': None,
        'edited_at': None,
        'deleted_by': None,
        'deleted_at': None,
    }

    # Build the SELECT query for the source database
    source_select_cols = []
    for col in direct_copy_columns:
        if col in source_column_names:
            source_select_cols.append(col)
    for col_id, table_name in lookup_columns.items():
        # If the source has the ID column, select it directly
        if col_id in source_column_names:
            source_select_cols.append(col_id)
        # If the source has the name column (e.g., 'difficulty_level' instead of 'difficulty_level_id'), select it
        elif col_id.replace('_id', '') in source_column_names:
            source_select_cols.append(col_id.replace('_id', ''))

    source_select_cols_str = ', '.join(source_select_cols)
    source_cursor.execute(f"SELECT {source_select_cols_str} FROM questions")
    source_questions = source_cursor.fetchall()

    print(f"Migrating data for table: questions")
    for source_row in source_questions:
        insert_columns = []
        insert_values = []
        source_data = dict(source_row)

        for col in target_column_names:
            if col in direct_copy_columns and col in source_data:
                insert_columns.append(col)
                insert_values.append(source_data[col])
            elif col in lookup_columns:
                # Try to get ID from source if it exists
                lookup_id_from_source = None
                if col in source_data: # Source has the ID column
                    lookup_id_from_source = source_data[col]
                elif col.replace('_id', '') in source_data: # Source has the name column
                    lookup_name = source_data[col.replace('_id', '')]
                    if lookup_name:
                        lookup_id_from_source = get_lookup_id_by_name(target_conn, lookup_columns[col], lookup_name)
                
                insert_columns.append(col)
                insert_values.append(lookup_id_from_source)
            elif col in default_values:
                insert_columns.append(col)
                insert_values.append(default_values[col])
            # else: column exists in target but not in source and no default, will be None

        # Ensure 'variables' column is handled as JSON string
        if 'variables' in insert_columns and 'variables' in source_data and source_data['variables'] is not None:
            try:
                idx = insert_columns.index('variables')
                # Check if it's already a JSON string, if not, dump it
                if not isinstance(insert_values[idx], str):
                    insert_values[idx] = json.dumps(insert_values[idx])
            except (ValueError, TypeError):
                # If it's not valid JSON, set to None or handle error
                insert_values[idx] = None

        insert_cols_str = ', '.join(insert_columns)
        placeholders = ', '.join(['?' for _ in insert_values])

        try:
            target_cursor.execute(
                f"INSERT OR IGNORE INTO questions ({insert_cols_str}) VALUES ({placeholders})",
                tuple(insert_values)
            )
        except sqlite3.Error as e:
            print(f"Error inserting question: {e} - Row: {insert_values}")
    target_conn.commit()
    print(f"Finished migrating data for table: questions")

    print("Questions table migration complete.")

except sqlite3.Error as e:
    print(f"An error occurred during questions migration: {e}")
finally:
    if source_conn:
        source_conn.close()
    if target_conn:
        target_conn.close()
