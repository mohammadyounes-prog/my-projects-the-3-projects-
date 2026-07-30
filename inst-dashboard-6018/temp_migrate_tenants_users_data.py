import sqlite3

source_db_path = "D:\\QuestionRetrieval\\new-q-bank\\working-eorkin- afte -q-bank\\questions.db"
target_db_path = "D:\\QuestionRetrieval\\new-q-bank\\questions.db"

def migrate_table(source_conn, target_conn, table_name, column_mapping=None, default_values=None):
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    source_cursor.execute(f"PRAGMA table_info({table_name});")
    source_columns_info = source_cursor.fetchall()
    source_column_names = [col[1] for col in source_columns_info]

    target_cursor.execute(f"PRAGMA table_info({table_name});")
    target_columns_info = target_cursor.fetchall()
    target_column_names = [col[1] for col in target_columns_info]

    # Determine columns to select from source and insert into target
    select_columns = []
    insert_columns = []
    for col in target_column_names:
        if col in source_column_names:
            select_columns.append(col)
            insert_columns.append(col)
        elif default_values and col in default_values:
            # This column will be filled with a default value, not selected from source
            insert_columns.append(col)

    if not insert_columns:
        print(f"Skipping table {table_name}: No columns to insert.")
        return

    select_cols_str = ', '.join(select_columns)
    insert_cols_str = ', '.join(insert_columns)
    placeholders = ', '.join(['?' for _ in insert_columns])

    source_cursor.execute(f"SELECT {select_cols_str} FROM {table_name}")
    rows = source_cursor.fetchall()

    print(f"Migrating data for table: {table_name}")
    for row_data in rows:
        insert_values = []
        source_data_dict = dict(zip(select_columns, row_data))

        for col in insert_columns:
            if col in source_data_dict:
                insert_values.append(source_data_dict[col])
            elif default_values and col in default_values:
                insert_values.append(default_values[col])
            else:
                insert_values.append(None) # Fallback for columns not in source and no default

        try:
            target_cursor.execute(
                f"INSERT OR IGNORE INTO {table_name} ({insert_cols_str}) VALUES ({placeholders})",
                tuple(insert_values)
            )
        except sqlite3.Error as e:
            print(f"Error inserting into {table_name}: {e} - Row: {insert_values}")
    target_conn.commit()
    print(f"Finished migrating data for table: {table_name}")

try:
    source_conn = sqlite3.connect(source_db_path)
    source_conn.row_factory = sqlite3.Row # Enable column access by name
    target_conn = sqlite3.connect(target_db_path)
    target_conn.row_factory = sqlite3.Row # Enable column access by name

    # Migrate tenants table
    migrate_table(source_conn, target_conn, "tenants")

    # Migrate users table with default values for new columns
    user_default_values = {
        "is_admin": 0,
        "full_name": None,
        "mobile_phone": None,
        "audience_type": None,
        "tenant_id": None, # Assuming superadmin might not have a tenant_id, or it will be updated later
        "is_super_admin": 0 # Assuming this is a new column in target
    }
    migrate_table(source_conn, target_conn, "users", default_values=user_default_values)

    print("Tenants and Users migration complete.")

except sqlite3.Error as e:
    print(f"An error occurred during migration: {e}")
finally:
    if source_conn:
        source_conn.close()
    if target_conn:
        target_conn.close()
