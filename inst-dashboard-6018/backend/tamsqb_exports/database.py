import sqlite3
import os
from fastapi.concurrency import run_in_threadpool
import datetime
from typing import List, Optional, Any
import re
import json

DATABASE_FILE = os.path.join(os.path.dirname(__file__), '../', 'questions.db')
print(f"DEBUG: Using database file: {DATABASE_FILE}") # ADDED LOG

async def get_db():
    conn = await run_in_threadpool(sqlite3.connect, DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        await run_in_threadpool(conn.close)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def create_generation_tasks_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            request_parameters TEXT,
            num_questions_requested INTEGER,
            num_questions_generated INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def add_user_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN user_id INTEGER")
        # Optionally, update existing questions with a default user_id if needed
        # For example, if user_id 1 is a default admin or system user
        cursor.execute("UPDATE questions SET user_id = 1 WHERE user_id IS NULL")
        conn.commit()
        print("Added user_id column to questions table and updated existing questions.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("user_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_task_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN task_id INTEGER")
        conn.commit()
        print("Added task_id column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("task_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_audience_type_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN audience_type TEXT")
        conn.commit()
        print("Added audience_type column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("audience_type column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_variables_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN variables TEXT")
        conn.commit()
        print("Added variables column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("variables column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_tenant_id_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN tenant_id INTEGER")
        conn.commit()
        print("Added tenant_id column to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("tenant_id column already exists in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_audit_fields_to_questions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN approved_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN approved_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN rejected_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN rejected_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN edited_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN edited_at TEXT")
        cursor.execute("ALTER TABLE questions ADD COLUMN deleted_by INTEGER")
        cursor.execute("ALTER TABLE questions ADD COLUMN deleted_at TEXT")
        conn.commit()
        print("Added audit fields to questions table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Audit fields already exist in questions table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_email_to_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        print("DEBUG: Successfully added email column to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("DEBUG: email column already exists in users table. Skipping migration.")
        else:
            print(f"ERROR: Failed to add email column to users table: {e}")
            raise e
    finally:
        conn.close()

def create_generation_models_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS generation_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_api_name TEXT NOT NULL UNIQUE,
            generation_method TEXT NOT NULL,
            tenant_id INTEGER,
            is_default BOOLEAN NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            api_key TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )"""
    )
    conn.commit()
    conn.close()

# Ensure tables are created and migrations run when the module is imported
create_generation_tasks_table()
add_user_id_to_questions_table()
add_task_id_to_questions_table()
add_audience_type_to_questions_table()
add_variables_to_questions_table()
add_tenant_id_to_questions_table()
create_generation_models_table()
add_email_to_users_table() # This will now be called after generation_tasks is assumed to exist
add_audit_fields_to_questions_table()

def create_indexes():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create helpful indexes if they don't already exist
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_user ON questions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_task ON questions(task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user ON generation_tasks(user_id)")
    conn.commit()
    conn.close()

create_indexes()

def create_user_specific_audience_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    for audience_type in ["school", "university", "company"]:
        table_name = f"user_{audience_type}_preferences"
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    conn.commit()
    conn.close()

def create_uploaded_files_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tenant_id INTEGER,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            upload_timestamp TEXT NOT NULL,
            extracted_content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
    """)
    conn.commit()
    conn.close()

def add_task_id_to_uploaded_files_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE uploaded_files ADD COLUMN task_id INTEGER")
        conn.commit()
        print("Added task_id column to uploaded_files table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("task_id column already exists in uploaded_files table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

def add_uploaded_file_id_to_generation_tasks_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE generation_tasks ADD COLUMN uploaded_file_id INTEGER")
        conn.commit()
        print("Added uploaded_file_id column to generation_tasks table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("uploaded_file_id column already exists in generation_tasks table. Skipping migration.")
        else:
            raise e
    finally:
        conn.close()

create_user_specific_audience_tables()
create_uploaded_files_table()
add_task_id_to_uploaded_files_table() # Call the new migration function
add_uploaded_file_id_to_generation_tasks_table() # Call the new migration function


def get_user(username: str, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id:
        cursor.execute("SELECT *, email FROM users WHERE username = ? AND tenant_id = ?", (username, tenant_id))
    else:
        cursor.execute("SELECT *, email FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id:
        cursor.execute("SELECT *, email FROM users WHERE id = ? AND tenant_id = ?", (user_id, tenant_id))
    else:
        cursor.execute("SELECT *, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username: str, hashed_password: str, is_admin: int = 0, full_name: Optional[str] = None, tenant_id: Optional[int] = None, mobile_phone: Optional[str] = None, email: Optional[str] = None, audience_type: Optional[str] = None, role: Optional[str] = None, institution: Optional[str] = None, department: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, is_admin, full_name, tenant_id, mobile_phone, email, audience_type, role, institution, department) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, hashed_password, is_admin, full_name, tenant_id, mobile_phone, email, audience_type, role, institution, department))
    conn.commit()
    conn.close()

def update_user_password(user_id: int, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

def delete_multiple_tenants(tenant_ids: List[int]):
    if not tenant_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in tenant_ids])
    cursor.execute(f"DELETE FROM tenants WHERE id IN ({placeholders})", tuple(tenant_ids))
    conn.commit()
    conn.close()

def delete_tenant(tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
    conn.commit()
    conn.close()

def update_tenant(tenant_id: int, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tenants SET name = ? WHERE id = ?", (name, tenant_id))
    conn.commit()
    conn.close()

def create_tenant(name: str, parent_id: Optional[int] = None, created_by: Optional[int] = None, conn: Optional[sqlite3.Connection] = None, cursor: Optional[sqlite3.Cursor] = None) -> int:
    _conn = conn if conn else get_db_connection()
    _cursor = cursor if cursor else _conn.cursor()
    
    _cursor.execute("INSERT INTO tenants (name, parent_id, created_by) VALUES (?, ?, ?)", (name, parent_id, created_by))
    
    if not conn:
        _conn.commit()
        _conn.close()
    
    return _cursor.lastrowid

def get_all_tenants(skip: int = 0, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total count first
    cursor.execute("SELECT COUNT(*) FROM tenants")
    total_tenants = cursor.fetchone()[0]

    # Get paginated tenants
    cursor.execute("""
        SELECT t.id, t.name, t.created_at, u.username as created_by_username, t.created_by as created_by_id, c.name as country, u.mobile_phone as admin_mobile_phone
        FROM tenants t
        LEFT JOIN users u ON t.created_by = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        ORDER BY t.created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, skip))
    tenants = cursor.fetchall()
    conn.close()
    return total_tenants, [dict(tenant) for tenant in tenants]

def get_tenant_by_id(tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.name, t.created_at, c.name as country
        FROM tenants t
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        WHERE t.id = ?
    """, (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    print(f"DEBUG: get_tenant_by_id returning: {tenant}")
    return dict(tenant) if tenant else None

def get_all_users(tenant_ids: Optional[List[int]] = None, skip: int = 0, limit: int = 10, country: Optional[str] = None, product_id: Optional[int] = None, username: Optional[str] = None, phone: Optional[str] = None, sort_by: Optional[str] = None):
    print(f"DEBUG: get_all_users called with tenant_ids={tenant_ids}, skip={skip}, limit={limit}, country={country}, product_id={product_id}, username={username}, phone={phone}, sort_by={sort_by}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query for users
    base_query = """
        SELECT u.id, u.username, u.is_admin, u.full_name, u.tenant_id, t.name as agent_name, GROUP_CONCAT(c.name) as country_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        LEFT JOIN tenant_countries tc ON u.tenant_id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
    """
    
    where_clauses = []
    params = []

    if tenant_ids is not None and len(tenant_ids) > 0:
        placeholders = ','.join('?' for _ in tenant_ids)
        where_clauses.append(f"u.tenant_id IN ({placeholders})")
        params.extend(tenant_ids)

    if username:
        where_clauses.append("u.username LIKE ?")
        params.append(f"%{username}%")

    if phone:
        where_clauses.append("u.mobile_phone LIKE ?")
        params.append(f"%{phone}%")

    if product_id is not None:
        # Join with billing_events to filter by product_id
        base_query += " LEFT JOIN billing_events be ON u.id = be.user_id "
        where_clauses.append("be.product_id = ?")
        params.append(product_id)

    # Construct the WHERE clause
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " GROUP BY u.id"

    having_clauses = []
    if country:
        having_clauses.append("country_name LIKE ?")
        params.append(f"%{country}%")

    if having_clauses:
        base_query += " HAVING " + " AND ".join(having_clauses)

    # Determine sorting order
    order_by_clause = " ORDER BY u.username ASC" # Default sort
    if sort_by == 'fifo':
        order_by_clause = " ORDER BY u.id ASC" # FIFO sorting
    elif sort_by == 'lifo':
        order_by_clause = " ORDER BY u.id DESC" # LIFO sorting
    elif sort_by == 'username':
        order_by_clause = " ORDER BY u.username ASC"

    # Get total count first
    # The count query needs to be adjusted to handle the GROUP BY logic correctly.
    # A subquery is a robust way to do this.
    count_query = f"SELECT COUNT(*) FROM ({base_query})"
    
    print(f"DEBUG: get_all_users count_query: {count_query}, count_params: {params}")
    cursor.execute(count_query, params)
    total_users = cursor.fetchone()[0]

    # Get paginated users
    final_query = base_query + order_by_clause + " LIMIT ? OFFSET ?"
    final_params = params + [limit, skip]

    print(f"DEBUG: get_all_users final_query: {final_query}, final_params: {final_params}")
    cursor.execute(final_query, final_params)
    users = cursor.fetchall()
    print(f"DEBUG: get_all_users fetched users: {users}")
    conn.close()
    return total_users, [dict(user) for user in users]

def update_user(user_id: int, username: Optional[str] = None, is_admin: Optional[int] = None, full_name: Optional[str] = None, mobile_phone: Optional[str] = None, email: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(is_admin)
    if full_name is not None:
        updates.append("full_name = ?")
        params.append(full_name)
    if mobile_phone is not None:
        updates.append("mobile_phone = ?")
        params.append(mobile_phone)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    
    if updates:
        sql_query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)
        cursor.execute(sql_query, tuple(params))
        conn.commit()
    conn.close()

def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Set created_by to NULL in tenants table
        cursor.execute("UPDATE tenants SET created_by = NULL WHERE created_by = ?", (user_id,))

        # Delete from generation_tasks
        cursor.execute("DELETE FROM generation_tasks WHERE user_id = ?", (user_id,))

        # Delete from user preferences tables
        for audience_type in ["school", "university", "company"]:
            table_name = f"user_{audience_type}_preferences"
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user_id,))
            except sqlite3.OperationalError as e:
                # This will happen if the table doesn't exist, which is fine.
                if "no such table" in str(e):
                    print(f"Table {table_name} does not exist, skipping.")
                else:
                    raise e
        
        # Finally, delete the user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_multiple_users(user_ids: List[int], tenant_id: Optional[int] = None):
    if not user_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in user_ids])
    if tenant_id is None:
        cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", tuple(user_ids))
    else:
        cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders}) AND tenant_id = ?", tuple(user_ids + [tenant_id]))
    conn.commit()
    conn.close()

def add_lookup_data(table_name: str, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (name) VALUES (?)", (name,))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def update_lookup_data(table_name: str, item_id: int, new_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET name = ? WHERE id = ?", (new_name, item_id))
    conn.commit()
    conn.close()

def delete_lookup_data(table_name: str, item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def ensure_models_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            method TEXT NOT NULL CHECK (method IN ('ai','internet','both')),
            provider TEXT NOT NULL CHECK (provider IN ('google','openai','custom')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def get_models(method: str | None = None) -> list[dict]:
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if method:
        cur.execute("SELECT * FROM models WHERE method = ? ORDER BY display_name", (method,))
    else:
        cur.execute("SELECT * FROM models ORDER BY display_name")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_models() -> list[dict]:
    return get_models(None)

def get_model_by_name(name: str) -> dict | None:
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM models WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def create_model(name: str, display_name: str, method: str, provider: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO models (name, display_name, method, provider) VALUES (?,?,?,?)",
        (name, display_name, method, provider),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def update_model(model_id: int, **fields):
    if not fields:
        return
    allowed = {"name", "display_name", "method", "provider"}
    sets, values = [], []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k} = ?")
            values.append(v)
    if not sets:
        return
    values.append(model_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE models SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_model(model_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM models WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()

def insert_generation_task(user_id: int, request_parameters: str, num_questions_requested: int, num_questions_generated: int, status: str = 'completed', tenant_id: int | None = None, uploaded_file_id: Optional[int] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    print(f"DEBUG: Inserting generation task for user_id: {user_id}, uploaded_file_id: {uploaded_file_id}")
    # Try to insert tenant_id and uploaded_file_id if columns exist; fallback to insert without them
    try:
        cursor.execute(
            """INSERT INTO generation_tasks (
                user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id)
        )
    except sqlite3.OperationalError as e:
        if "no such column: tenant_id" in str(e):
            print(f"WARN: tenant_id column missing. Inserting without tenant_id. Error: {e}")
            try:
                cursor.execute(
                    """INSERT INTO generation_tasks (
                        user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status, uploaded_file_id)
                )
            except sqlite3.OperationalError as e_inner:
                if "no such column: uploaded_file_id" in str(e_inner):
                    print(f"WARN: uploaded_file_id column missing. Inserting without uploaded_file_id. Error: {e_inner}")
                    cursor.execute(
                        """INSERT INTO generation_tasks (
                            user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status
                        ) VALUES (?, ?, ?, ?, ?, ?)""",
                        (user_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status)
                    )
                else:
                    raise e_inner
        elif "no such column: uploaded_file_id" in str(e):
            print(f"WARN: uploaded_file_id column missing. Inserting without uploaded_file_id. Error: {e}")
            cursor.execute(
                """INSERT INTO generation_tasks (
                    user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, tenant_id, timestamp, request_parameters, num_questions_requested, num_questions_generated, status)
            )
        else:
            raise e
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_search_suggestions(term: str, limit: int = 10) -> list[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    suggestions = set() # Use a set to store unique suggestions

    # Search in question_text
    cursor.execute(
        "SELECT question_text FROM questions WHERE question_text LIKE ? LIMIT ?",
        (f"%{term}%", limit)
    )
    for row in cursor.fetchall():
        suggestions.add(row['question_text'])

    # Search in choices
    for i in range(1, 5): # choice_1 to choice_4
        cursor.execute(
            f"SELECT choice_{i} FROM questions WHERE choice_{i} LIKE ? AND choice_{i} IS NOT NULL LIMIT ?",
            (f"%{term}%", limit)
        )
        for row in cursor.fetchall():
            suggestions.add(row[f'choice_{i}'])
    
    # Search in correct_option
    cursor.execute(
        "SELECT correct_option FROM questions WHERE correct_option LIKE ? AND correct_option IS NOT NULL LIMIT ?",
        (f"%{term}%", limit)
    )
    for row in cursor.fetchall():
        suggestions.add(row['correct_option'])

    conn.close()
    return sorted(list(suggestions))[:limit]

def get_total_questions_count(query: Optional[str] = None, status: Optional[str] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None,
                              date_from: Optional[str] = None, date_to: Optional[str] = None,
                              approved_by: Optional[int] = None, rejected_by: Optional[int] = None,
                              edited_by: Optional[int] = None, deleted_by: Optional[int] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT COUNT(question_id) FROM questions q"
    params = []

    where_clauses = []
    if query:
        where_clauses.append("""(
            q.question_text LIKE ? OR
            q.choice_1 LIKE ? OR
            q.choice_2 LIKE ? OR
            q.choice_3 LIKE ? OR
            q.choice_4 LIKE ? OR
            q.correct_option LIKE ?
        )""")
        for _ in range(6):
            params.append(f"%{query}%")

    if status:
        where_clauses.append("q.status = ?")
        params.append(status)

    if user_id is not None:
        where_clauses.append("q.user_id = ?")
        params.append(user_id)

    if tenant_id is not None:
        where_clauses.append("q.tenant_id = ?")
        params.append(tenant_id)

    if date_from and date_to:
        where_clauses.append("date(q.date_created) BETWEEN date(?) AND date(?)")
        params.extend([date_from, date_to])
    elif date_from:
        where_clauses.append("date(q.date_created) >= date(?)")
        params.append(date_from)
    elif date_to:
        where_clauses.append("date(q.date_created) <= date(?)")
        params.append(date_to)

    if approved_by is not None:
        where_clauses.append("q.approved_by = ?")
        params.append(approved_by)
    if rejected_by is not None:
        where_clauses.append("q.rejected_by = ?")
        params.append(rejected_by)
    if edited_by is not None:
        where_clauses.append("q.edited_by = ?")
        params.append(edited_by)
    if deleted_by is not None:
        where_clauses.append("q.deleted_by = ?")
        params.append(deleted_by)

    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)

    print(f"DEBUG: get_total_questions_count SQL Query: {sql_query}")
    print(f"DEBUG: get_total_questions_count Parameters: {params}")
    cursor.execute(sql_query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_questions(query: Optional[str] = None, status: Optional[str] = None, task_id: Optional[int] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None, skip: int = 0, limit: int = 10,
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  approved_by: Optional[int] = None, rejected_by: Optional[int] = None,
                  edited_by: Optional[int] = None, deleted_by: Optional[int] = None,
                  include_correct_answer: bool = True): # NEW PARAMETER - Changed default to True
    import time
    t0 = time.perf_counter()
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = f"""SELECT 
        q.question_id, q.author_creator, q.date_created, q.question_text,
        q.choice_1, q.choice_2, q.choice_3, q.choice_4, 
        CASE WHEN {1 if include_correct_answer else 0} THEN q.correct_option ELSE NULL END as correct_option,
        dl.name as difficulty_level, cl.name as cognitive_level, lo.name as learning_outcome,
        qt.name as question_type,
        st.name as school_type, ss.name as subject, sy.name as year,
        um.name as major, uc.name as course, umt.name as material, us.name as semester,
        comp.name as company, dep.name as department, jr.name as job_role,
        q.mark, q.time_seconds, q.discriminating_factor, q.status, q.audience_type, q.variables, q.solution
        FROM questions q
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN school_types st ON q.school_type_id = st.id
        LEFT JOIN school_subjects ss ON q.subject_id = ss.id
        LEFT JOIN school_years sy ON q.year_id = sy.id
        LEFT JOIN university_majors um ON q.major_id = um.id
        LEFT JOIN university_courses uc ON q.course_id = uc.id
        LEFT JOIN university_materials umt ON q.material_id = umt.id
        LEFT JOIN university_semesters us ON q.semester_id = us.id
        LEFT JOIN companies comp ON q.company_id = comp.id
        LEFT JOIN departments dep ON q.department_id = dep.id
        LEFT JOIN job_roles jr ON q.job_role_id = jr.id
    """
    params = []

    where_clauses = []
    if query:
        where_clauses.append("""(
            q.question_text LIKE ? OR
            q.choice_1 LIKE ? OR
            q.choice_2 LIKE ? OR
            q.choice_3 LIKE ? OR
            q.choice_4 LIKE ? OR
            q.correct_option LIKE ?
        )""")
        # Add the query parameter for each LIKE clause
        for _ in range(6): # 6 fields to search
            params.append(f"%{query}%")

    if status:
        where_clauses.append("q.status = ?")
        params.append(status)

    if user_id is not None:
        where_clauses.append("q.user_id = ?")
        params.append(user_id)

    if tenant_id is not None:
        where_clauses.append("q.tenant_id = ?")
        params.append(tenant_id)

    if date_from and date_to:
        where_clauses.append("date(q.date_created) BETWEEN date(?) AND date(?)")
        params.extend([date_from, date_to])
    elif date_from:
        where_clauses.append("date(q.date_created) >= date(?)")
        params.append(date_from)
    elif date_to:
        where_clauses.append("date(q.date_created) <= date(?)")
        params.append(date_to)

    if approved_by is not None:
        where_clauses.append("q.approved_by = ?")
        params.append(approved_by)
    if rejected_by is not None:
        where_clauses.append("q.rejected_by = ?")
        params.append(rejected_by)
    if edited_by is not None:
        where_clauses.append("q.edited_by = ?")
        params.append(edited_by)
    if deleted_by is not None:
        where_clauses.append("q.deleted_by = ?")
        params.append(deleted_by)

    if where_clauses:
        sql_query += " WHERE " + " AND ".join(where_clauses)

    sql_query += " ORDER BY q.question_id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    print(f"DEBUG: get_questions SQL Query: {sql_query}")
    print(f"DEBUG: get_questions Parameters: {params}")
    cursor.execute(sql_query, params)
    questions = cursor.fetchall()
    t1 = time.perf_counter()
    print(f"TIMING: get_questions took {int((t1 - t0)*1000)} ms (limit={limit}, skip={skip})")
    print(f"DEBUG: get_questions - Applied filters: user_id={user_id}, tenant_id={tenant_id}")
    print(f"DEBUG: get_questions - Raw questions fetched from DB: {questions}")
    conn.close()
    
    questions_list = []
    for q in questions:
        question_dict = dict(q)
        if question_dict.get('variables'):
            question_dict['variables'] = json.loads(question_dict['variables'])
        questions_list.append(question_dict)

    return questions_list

def get_lookup_data(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name FROM {table_name}")
    data = [{row['id']: row['name']} for row in cursor.fetchall()]
    conn.close()
    return data

def get_lookup_data_list(table_name: str, lang: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    column_name = "name"
    if lang == "ar":
        # Check if 'name_ar' column exists in the table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if "name_ar" in columns:
            column_name = "name_ar"
    
    cursor.execute(f"SELECT id, {column_name} as name FROM {table_name}")
    data = [{ "id": row['id'], "name": row['name'] } for row in cursor.fetchall()]
    conn.close()
    return data

def get_all_learning_outcomes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if 'name_ar' column exists
    cursor.execute("PRAGMA table_info(learning_outcomes)")
    columns = [col[1] for col in cursor.fetchall()]
    has_name_ar = "name_ar" in columns

    if has_name_ar:
        cursor.execute("SELECT name, name_ar FROM learning_outcomes")
    else:
        cursor.execute("SELECT name, name as name_ar FROM learning_outcomes")
        
    outcomes = [{'name': row['name'], 'name_ar': row['name_ar']} for row in cursor.fetchall()]
    conn.close()
    return outcomes

def get_lookup_id_by_name(table_name: str, name: str) -> Optional[int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table_name} WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def get_generation_tasks_by_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM generation_tasks WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    
    tasks_with_file_info = []
    for task_row in tasks:
        task = dict(task_row)
        task['uploaded_file_name'] = "No uploaded files within this task." # Default message
        task['generated_question_ids'] = [] # Initialize new field

        # Fetch generated question IDs for this task
        question_conn = get_db_connection()
        question_cursor = question_conn.cursor()
        query_sql = "SELECT question_id FROM questions WHERE task_id = ?"
        print(f"DEBUG: get_generation_tasks_by_user - Executing query: '{query_sql}' with task_id: {task['task_id']}")
        question_cursor.execute(query_sql, (task['task_id'],))
        generated_question_ids = [int(row['question_id']) for row in question_cursor.fetchall()]
        question_conn.close()
        task['generated_question_ids'] = generated_question_ids
        print(f"DEBUG: get_generation_tasks_by_user - Task {task['task_id']} has generated questions: {generated_question_ids}")
        print(f"DEBUG: get_generation_tasks_by_user - Raw query result for task {task['task_id']}: {generated_question_ids}")

        print(f"DEBUG: get_generation_tasks_by_user - Processing task_id: {task['task_id']}")
        print(f"DEBUG: get_generation_tasks_by_user - Raw request_parameters: {task['request_parameters']}")

        if task['request_parameters']:
            try:
                request_params = json.loads(task['request_parameters'])
                print(f"DEBUG: get_generation_tasks_by_user - Parsed request_params: {request_params}")
                uploaded_file_id = request_params.get('uploaded_file_id')
                print(f"DEBUG: get_generation_tasks_by_user - Extracted uploaded_file_id: {uploaded_file_id}")
                
                if uploaded_file_id:
                    file_conn = get_db_connection()
                    file_cursor = file_conn.cursor()
                    file_cursor.execute("SELECT file_name FROM uploaded_files WHERE id = ?", (uploaded_file_id,))
                    file_result = file_cursor.fetchone()
                    file_conn.close()

                    if file_result:
                        task['uploaded_file_name'] = file_result['file_name']
                        print(f"DEBUG: get_generation_tasks_by_user - Fetched file_name: {task['uploaded_file_name']}")
                    else:
                        task['uploaded_file_name'] = f"Uploaded file (ID: {uploaded_file_id}) not found."
                        print(f"DEBUG: get_generation_tasks_by_user - File not found for ID: {uploaded_file_id}")
            except json.JSONDecodeError:
                print(f"WARNING: Could not decode request_parameters for task_id {task['task_id']}")
            except Exception as e:
                print(f"ERROR: Error processing uploaded_file_id for task_id {task['task_id']}: {e}")
        tasks_with_file_info.append(task)
    return tasks_with_file_info


def insert_question(question_data: dict, task_id: Optional[int] = None, user_id: Optional[int] = None, tenant_id: Optional[int] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"DEBUG: insert_question called with: question_data={question_data.get('question_text')[:50]}..., task_id={task_id}, user_id={user_id}, tenant_id={tenant_id}")
    print(f"DEBUG: insert_question - Received task_id for insertion: {task_id}")

    # Normalize incoming data to a plain dict to avoid attribute errors
    try:
        import sqlite3 as _sqlite3
        if isinstance(question_data, _sqlite3.Row):
            question_data = {k: question_data[k] for k in question_data.keys()}
    except Exception:
        pass
    if not isinstance(question_data, dict):
        try:
            question_data = dict(question_data)
        except Exception:
            # Fallback: reflect common attributes
            question_data = {k: getattr(question_data, k) for k in dir(question_data) if not k.startswith('_')}

    # Safe getter that does not rely on dict.get semantics for non-dict inputs
    def g(key: str, default=None):
        try:
            return question_data[key] if key in question_data else default
        except Exception:
            return default

    # Build a clean, flat dict with only fields we actually use downstream.
    clean = {
        'author_creator': g('author_creator', 'System'),
        'date_created': g('date_created', datetime.datetime.now().isoformat()),
        'question_text': g('question_text', ''),
        'choice_1': g('choice_1'),
        'choice_2': g('choice_2'),
        'choice_3': g('choice_3'),
        'choice_4': g('choice_4'),
        'correct_option': g('correct_option'),
        'difficulty_level': g('difficulty_level'),
        'cognitive_level': g('cognitive_level'),
        'learning_outcome': g('learning_outcome'),
        'question_type': g('question_type'),
        'mark': g('mark', 0),
        'time_seconds': g('time_seconds', 0),
        'discriminating_factor': g('discriminating_factor'),
        'status': g('status', 'pending'),
        'school_type': g('school_type'),
        'subject': g('subject'),
        'year': g('year'),
        'major': g('major'),
        'course': g('course'),
        'material': g('material'),
        'semester': g('semester'),
        'company': g('company'),
        'department': g('department'),
        'job_role': g('job_role'),
        'audience_type': g('audience_type'),
        'variables': g('variables'),
        'solution': g('solution'),
    }

    # Coerce types and enforce NOT NULL defaults for constrained fields
    try:
        clean['mark'] = int(clean['mark']) if clean['mark'] is not None else 0
    except Exception:
        clean['mark'] = 0
    try:
        clean['time_seconds'] = int(clean['time_seconds']) if clean['time_seconds'] is not None else 0
    except Exception:
        clean['time_seconds'] = 0
    if isinstance(clean['date_created'], datetime.date):
        clean['date_created'] = str(clean['date_created'])
    if clean['date_created'] is None:
        clean['date_created'] = datetime.datetime.now().isoformat()
    if clean['status'] is None:
        clean['status'] = 'pending'

    # Get IDs for lookup tables using safe accessor
    difficulty_id = get_lookup_id_by_name('difficulty_levels', clean['difficulty_level'])
    cognitive_id = get_lookup_id_by_name('cognitive_levels', clean['cognitive_level'])
    learning_outcome_id = get_lookup_id_by_name('learning_outcomes', clean['learning_outcome'])
    question_type_id = get_lookup_id_by_name('question_types', clean['question_type'])

    school_type_id = get_lookup_id_by_name('school_types', clean['school_type'])
    subject_id = get_lookup_id_by_name('school_subjects', clean['subject'])
    year_id = get_lookup_id_by_name('school_years', clean['year'])
    major_id = get_lookup_id_by_name('university_majors', clean['major'])
    course_id = get_lookup_id_by_name('university_courses', clean['course']) # Assuming university_courses table exists
    material_id = get_lookup_id_by_name('university_materials', clean['material']) # Assuming university_materials table exists
    semester_id = get_lookup_id_by_name('university_semesters', clean['semester']) # Assuming university_semesters table exists
    company_id = get_lookup_id_by_name('companies', clean['company'])
    department_id = get_lookup_id_by_name('departments', clean['department'])
    job_role_id = get_lookup_id_by_name('job_roles', clean['job_role'])

    # If a lookup value is not found, set its ID to None (NULL in DB) instead of raising an error
    # This assumes these fields are nullable in the questions table schema.
    # The frontend should ensure required fields are selected.

    columns = [
        'author_creator', 'date_created', 'question_text', 
        'choice_1', 'choice_2', 'choice_3', 'choice_4', 'correct_option',
        'difficulty_level_id', 'cognitive_level_id', 'learning_outcome_id', 'question_type_id',
        'mark', 'time_seconds', 'discriminating_factor', 'status',
        'school_type_id', 'subject_id', 'year_id', 'major_id', 'course_id', 'material_id', 'semester_id',
        'company_id', 'department_id', 'job_role_id',
        'audience_type', 'solution'
    ]
    values = [
        clean['author_creator'],
        clean['date_created'],
        clean['question_text'],
        clean['choice_1'],
        clean['choice_2'],
        clean['choice_3'],
        clean['choice_4'],
        clean['correct_option'],
        difficulty_id,
        cognitive_id,
        learning_outcome_id,
        question_type_id,
        clean['mark'],
        clean['time_seconds'],
        clean['discriminating_factor'],
        clean['status'],
        school_type_id,
        subject_id,
        year_id,
        major_id,
        course_id,
        material_id,
        semester_id,
        company_id,
        department_id,
        job_role_id,
        clean['audience_type'],
        clean['solution']
    ]

    if task_id is not None:
        columns.append('task_id')
        values.append(task_id)

    if user_id is not None:
        columns.append('user_id')
        values.append(user_id)

    if tenant_id is not None:
        columns.append('tenant_id')
        values.append(tenant_id)

    if clean['variables'] is not None:
        columns.append('variables')
        try:
            values.append(json.dumps(clean['variables']))
        except Exception:
            values.append(None)

    placeholders = ', '.join(['?' for _ in values])
    sql_query = f"INSERT INTO questions ({', '.join(columns)}) VALUES ({placeholders})"
    print(f"DEBUG: insert_question SQL Query: {sql_query}")
    print(f"DEBUG: insert_question Parameters: {tuple(values)}")

    cursor.execute(sql_query, tuple(values))
    conn.commit()
    question_id = cursor.lastrowid
    print(f"DEBUG: Question inserted with ID: {question_id}")
    conn.close()
    return question_id

def get_audience_fields(audience_type: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT field_name, is_enabled FROM audience_field_config WHERE audience_type = ?", (audience_type,))
    fields = {row['field_name']: bool(row['is_enabled']) for row in cursor.fetchall()}
    conn.close()
    return fields

def get_property_types_by_audience(audience_type: str, lang: Optional[str] = None): # Added lang parameter
    conn = get_db_connection()
    cursor = conn.cursor()
    
    name_column = "name"
    if lang == "ar":
        cursor.execute("PRAGMA table_info(property_types)")
        columns = [col[1] for col in cursor.fetchall()]
        if "name_ar" in columns:
            name_column = "name_ar"
            
    cursor.execute(f"SELECT id, {name_column} as name, api_name, audience_type FROM property_types WHERE audience_type = ?", (audience_type,))
    property_types = cursor.fetchall()
    conn.close()
    print(f"DEBUG: get_property_types_by_audience returning: {property_types}")
    return [dict(pt) for pt in property_types]

def create_property_type(name: str, api_name: str, audience_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO property_types (name, api_name, audience_type) VALUES (?, ?, ?)",
        (name, api_name, audience_type)
    )
    conn.commit()
    new_id = cursor.lastrowid
    # Dynamically create the table for this new property type
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {api_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()
    return new_id

def get_property_type_by_api_name(api_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM property_types WHERE api_name = ?", (api_name,))
    property_type = cursor.fetchone()
    conn.close()
    return dict(property_type) if property_type else None

def delete_property_type(api_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use a transaction to ensure both operations succeed or fail together
    try:
        cursor.execute("BEGIN TRANSACTION")
        # Delete from the property_types table
        cursor.execute("DELETE FROM property_types WHERE api_name = ?", (api_name,))
        # Drop the associated lookup table
        cursor.execute(f"DROP TABLE IF EXISTS {api_name}")
        cursor.execute("COMMIT")
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    finally:
        conn.close()

def update_audience_fields(audience_type: str, fields: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    for field_name, is_enabled in fields.items():
        # Use INSERT OR REPLACE to handle both new and existing fields
        cursor.execute("""
            INSERT INTO audience_field_config (audience_type, field_name, is_enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(audience_type, field_name) DO UPDATE SET is_enabled = excluded.is_enabled;
        """, (audience_type, field_name, is_enabled))
    conn.commit()
    conn.close()

import json

def update_question(question_id: int, question_data: dict, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []

    for key, value in question_data.items():
        # Ensure we don't try to update the primary key
        if key == 'question_id':
            continue

        if key == 'variables':
            update_fields.append('variables = ?')
            update_values.append(json.dumps(value))
            continue
        # Handle lookup fields and status field
        if key in ['difficulty_level', 'cognitive_level', 'learning_outcome', 'question_type',
                   'school_type', 'subject', 'year', 'major', 'course', 'material', 'semester',
                   'company', 'department', 'job_role']:
            lookup_table = f"{key}s"
            # Special handling for 'year' to map to 'school_years'
            if key == 'year':
                lookup_table = 'school_years'
            # Special handling for 'question_type' to map to 'question_types'
            if key == 'question_type':
                lookup_table = 'question_types'

            lookup_id = None
            if value is not None and value != '': # Only try to get ID if value is not None or empty
                lookup_id = get_lookup_id_by_name(lookup_table, value)
            
            if lookup_id is not None:
                update_fields.append(f"{key}_id = ?")
                update_values.append(lookup_id)
            elif value is None or value == '':
                # If the value is None or empty, and the column is NOT NULL,
                # we should skip updating this field to avoid IntegrityError.
                # If the column is nullable, setting to None is fine.
                # For now, let's skip to prevent the error.
                pass
            else:
                raise ValueError(f"Invalid value for {key}: {value}")
        elif key == 'status':
            update_fields.append(f"status = ?")
            update_values.append(value)
        else:
            update_fields.append(f"{key} = ?")
            update_values.append(value)

    if not update_fields:
        print(f"DEBUG: update_question: No fields to update for question_id {question_id}")
        return

    # If actor provided, stamp edit metadata
    if actor_user_id is not None:
        update_fields.append('edited_by = ?')
        update_values.append(actor_user_id)
        update_fields.append('edited_at = ?')
        update_values.append(datetime.datetime.utcnow().isoformat())

    sql_query = f"UPDATE questions SET {', '.join(update_fields)} WHERE question_id = ?"
    update_values.append(question_id)

    print(f"DEBUG: update_question SQL Query: {sql_query}")
    print(f"DEBUG: update_question Parameters: {update_values}")
    cursor.execute(sql_query, tuple(update_values))
    conn.commit()
    print(f"DEBUG: update_question: Commit successful for question_id {question_id}")
    # Log action if context available
    if actor_user_id is not None and tenant_id is not None:
        try:
            log_question_action_raw(question_id, tenant_id, actor_user_id, 'edited', {"fields": list(question_data.keys())})
        except Exception as e:
            print("WARN: failed to log edited action:", e)
    conn.close()

def get_question_by_id(question_id: int, include_correct_answer: bool = False): # NEW PARAMETER
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = f"""SELECT 
        q.question_id, q.author_creator, q.date_created, q.question_text,
        q.choice_1, q.choice_2, q.choice_3, q.choice_4, 
        CASE WHEN {1 if include_correct_answer else 0} THEN q.correct_option ELSE NULL END as correct_option,
        dl.name as difficulty_level, cl.name as cognitive_level, lo.name as learning_outcome,
        qt.name as question_type,
        st.name as school_type, ss.name as subject, sy.name as year,
        um.name as major, uc.name as course, umt.name as material, us.name as semester,
        comp.name as company, dep.name as department, jr.name as job_role,
        q.mark, q.time_seconds, q.discriminating_factor, q.status, q.audience_type, q.variables, q.solution
        FROM questions q
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN school_types st ON q.school_type_id = st.id
        LEFT JOIN school_subjects ss ON q.subject_id = ss.id
        LEFT JOIN school_years sy ON q.year_id = sy.id
        LEFT JOIN university_majors um ON q.major_id = um.id
        LEFT JOIN university_courses uc ON q.course_id = uc.id
        LEFT JOIN university_materials umt ON q.material_id = umt.id
        LEFT JOIN university_semesters us ON q.semester_id = us.id
        LEFT JOIN companies comp ON q.company_id = comp.id
        LEFT JOIN departments dep ON q.department_id = dep.id
        LEFT JOIN job_roles jr ON q.job_role_id = jr.id
        WHERE q.question_id = ?
    """
    print(f"DEBUG: get_question_by_id SQL Query: {sql_query}")
    print(f"DEBUG: get_question_by_id Parameter: {question_id}")
    cursor.execute(sql_query, (question_id,))
    question = cursor.fetchone()
    print(f"DEBUG: get_question_by_id Result: {question}")
    conn.close()
    if question:
        question_dict = dict(question)
        if question_dict.get('variables'):
            question_dict['variables'] = json.loads(question_dict['variables'])
        return question_dict
    return None

def delete_question(question_id: int, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"DEBUG: Attempting to delete question with ID: {question_id}")
    try:
        if actor_user_id is not None and tenant_id is not None:
            try:
                cursor.execute("UPDATE questions SET deleted_by = ?, deleted_at = ? WHERE question_id = ?", (actor_user_id, datetime.datetime.utcnow().isoformat(), question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'deleted', None)
            except Exception as e:
                print("WARN: failed to stamp delete metadata:", e)
        cursor.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))
        conn.commit()
        print(f"DEBUG: Successfully deleted question with ID: {question_id}")
    except Exception as e:
        print(f"ERROR: Failed to delete question with ID {question_id}: {e}")
        conn.rollback() # Rollback in case of error
    finally:
        conn.close()

def delete_multiple_questions(question_ids: List[int], tenant_id: Optional[int] = None):
    if not question_ids:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['?' for _ in question_ids])
    try:
        if tenant_id is None:
            cursor.execute(f"DELETE FROM questions WHERE question_id IN ({placeholders})", tuple(question_ids))
        else:
            cursor.execute(f"DELETE FROM questions WHERE question_id IN ({placeholders}) AND tenant_id = ?", tuple(question_ids + [tenant_id]))
        conn.commit()
        print(f"DEBUG: Successfully deleted questions with IDs: {question_ids}")
    except Exception as e:
        print(f"ERROR: Failed to delete questions with IDs {question_ids}: {e}")
        conn.rollback()
    finally:
        conn.close()


def update_question_status(question_id: int, status: str, actor_user_id: Optional[int] = None, tenant_id: Optional[int] = None):
    import time
    t0 = time.perf_counter()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE questions SET status = ? WHERE question_id = ?", (status, question_id))
    if actor_user_id is not None and tenant_id is not None:
        try:
            now = datetime.datetime.utcnow().isoformat()
            if status.lower() == 'approved':
                cursor.execute("UPDATE questions SET approved_by = ?, approved_at = ? WHERE question_id = ?", (actor_user_id, now, question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'approved', None)
            elif status.lower() == 'rejected':
                cursor.execute("UPDATE questions SET rejected_by = ?, rejected_at = ? WHERE question_id = ?", (actor_user_id, now, question_id))
                log_question_action_raw(question_id, tenant_id, actor_user_id, 'rejected', None)
        except Exception as e:
            print("WARN: failed to stamp status metadata:", e)
    conn.commit()
    t1 = time.perf_counter()
    print(f"TIMING: update_question_status took {int((t1 - t0)*1000)} ms (status={status})")
    conn.close()

def log_question_action_raw(question_id: int, tenant_id: int, actor_user_id: int, action: str, details: Optional[Any]):
    conn = get_db_connection()
    cur = conn.cursor()
    details_str = None
    if details is not None:
        details_str = json.dumps(details) if not isinstance(details, str) else details
    try:
        cur.execute(
            "INSERT INTO question_actions (question_id, tenant_id, action, actor_user_id, details) VALUES (?,?,?,?,?)",
            (question_id, tenant_id, action, actor_user_id, details_str)
        )
        conn.commit()
    except Exception as e:
        print("WARN: failed to log question action:", e)
    finally:
        conn.close()

def get_question_history(question_id: int, tenant_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT action, actor_user_id, details, created_at FROM question_actions WHERE question_id = ? AND tenant_id = ? ORDER BY created_at ASC", (question_id, tenant_id))
    rows = cur.fetchall()
    conn.close()
    # return as list of dicts
    result = []
    for r in rows:
        details = r[2]
        try:
            details = json.loads(details) if details else None
        except Exception:
            pass
        result.append({"action": r[0], "actor_user_id": r[1], "details": details, "created_at": r[3]})
    return result

def update_generation_task_status(task_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE generation_tasks SET status = ? WHERE task_id = ?", (status, task_id))
    conn.commit()
    conn.close()

def update_generation_task_generated_count(task_id: int, count: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE generation_tasks SET num_questions_generated = ? WHERE task_id = ?", (count, task_id))
    conn.commit()
    conn.close()

def create_generation_model(model_name: str, model_api_name: str, generation_method: str, tenant_id: int, is_default: bool, is_active: bool, api_key: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO generation_models (model_name, model_api_name, generation_method, tenant_id, is_default, is_active, api_key)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (model_name, model_api_name, generation_method, tenant_id, is_default, is_active, api_key)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_generation_model_by_id(model_id: int, tenant_id: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute("SELECT * FROM generation_models WHERE id = ?", (model_id,))
    else:
        cursor.execute("SELECT * FROM generation_models WHERE id = ? AND tenant_id = ?", (model_id, tenant_id))
    model = cursor.fetchone()
    conn.close()
    return model

def get_generation_model_by_api_name(model_api_name: str, tenant_id: int | None):
    print(f"DEBUG: get_generation_model_by_api_name called with model_api_name={model_api_name}, tenant_id={tenant_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute(
            "SELECT * FROM generation_models WHERE model_api_name = ? AND is_active = 1 ORDER BY is_default DESC LIMIT 1",
            (model_api_name,)
        )
    else:
        cursor.execute(
            "SELECT * FROM generation_models WHERE model_api_name = ? AND (tenant_id = ? OR tenant_id IS NULL) AND is_active = 1 ORDER BY CASE WHEN tenant_id = ? THEN 0 ELSE 1 END, is_default DESC LIMIT 1",
            (model_api_name, tenant_id, tenant_id)
        )
    model = cursor.fetchone()
    conn.close()
    print(f"DEBUG: get_generation_model_by_api_name returning model: {model}")
    return model

def get_generation_models_by_method(generation_method: str, tenant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM generation_models WHERE generation_method = ? AND tenant_id = ? AND is_active = 1",
        (generation_method, tenant_id)
    )
    models = cursor.fetchall()
    conn.close()
    return [dict(model) for model in models]

def get_all_generation_models(tenant_id: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = ""
    params = ()
    if tenant_id is None:
        sql_query = (
            "SELECT * FROM generation_models WHERE is_active = 1 ORDER BY is_default DESC, model_name ASC"
        )
    else:
        sql_query = (
            "SELECT * FROM generation_models WHERE (tenant_id = ? OR tenant_id IS NULL) AND is_active = 1 ORDER BY CASE WHEN tenant_id = ? THEN 0 ELSE 1 END, is_default DESC, model_name ASC"
        )
        params = (tenant_id, tenant_id)
    print(f"DEBUG: get_all_generation_models SQL Query: {sql_query}")
    print(f"DEBUG: get_all_generation_models Parameters: {params}")
    cursor.execute(sql_query, params)
    models = cursor.fetchall()
    conn.close()
    print(f"DEBUG: get_all_generation_models fetched models: {models}")
    
    # Deduplicate models by model_name, giving priority to the first one found (which will be the tenant-specific one if it exists)
    unique_models = {}
    for model in models:
        model_dict = dict(model)
        if model_dict['model_name'] not in unique_models:
            unique_models[model_dict['model_name']] = model_dict
            
    return list(unique_models.values())

def update_generation_model(model_id: int, tenant_id: int, model_name: str, model_api_name: str, generation_method: str, is_default: bool, is_active: bool, api_key: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE generation_models
           SET model_name = ?, model_api_name = ?, generation_method = ?, is_default = ?, is_active = ?, api_key = ?
           WHERE id = ? AND tenant_id = ?""",
        (model_name, model_api_name, generation_method, is_default, is_active, api_key, model_id, tenant_id)
    )
    conn.commit()
    conn.close()

def delete_generation_model(model_id: int, tenant_id: Optional[int] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if tenant_id is None:
        cursor.execute("DELETE FROM generation_models WHERE id = ?", (model_id,))
    else:
        cursor.execute("DELETE FROM generation_models WHERE id = ? AND tenant_id = ?", (model_id, tenant_id))
    conn.commit()
    conn.close()

def get_all_billing_products(tenant_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT * FROM billing_products WHERE 1=1"
    params = []

    if is_active is not None:
        sql_query += " AND is_active = ?"
        params.append(1 if is_active else 0)
    
    if tenant_id is not None:
        sql_query += " AND (tenant_id IS NULL OR tenant_id = ?)"
        params.append(tenant_id)
    else:
        # If no tenant_id is provided, only return global products (tenant_id IS NULL)
        sql_query += " AND tenant_id IS NULL"

    cursor.execute(sql_query, params)
    products = cursor.fetchall()
    
    product_list = []
    for product in products:
        product_dict = dict(product)
        
        # Calculate sold_count
        cursor.execute("SELECT COUNT(*) FROM billing_events WHERE product_id = ?", (product_dict['id'],))
        sold_count = cursor.fetchone()[0]
        product_dict['sold_count'] = sold_count
        
        product_list.append(product_dict)

    conn.close()
    return product_list

def get_all_billing_events(
    tenant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    country: Optional[str] = None,
    agent_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT
            be.id,
            bp.name AS product_name,
            t.name AS agent_name,
            c.name AS country,
            u.username,
            be.created_at,
            be.total_price_cents,
            be.currency
        FROM billing_events be
        LEFT JOIN billing_products bp ON be.product_id = bp.id
        LEFT JOIN tenants t ON be.tenant_id = t.id
        LEFT JOIN users u ON be.user_id = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
    """

    where_clauses = ["be.event_type = 'credit'"]
    params = []

    if tenant_id is not None:
        where_clauses.append("be.tenant_id = ?")
        params.append(tenant_id)

    if country:
        where_clauses.append("c.name = ?")
        params.append(country)

    if agent_id is not None:
        where_clauses.append("t.id = ?")
        params.append(agent_id)

    if start_date:
        where_clauses.append("date(be.created_at) >= date(?)")
        params.append(start_date)

    if end_date:
        where_clauses.append("date(be.created_at) <= date(?)")
        params.append(end_date)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Get total count first
    count_query = f"SELECT COUNT(DISTINCT be.id) FROM billing_events be LEFT JOIN billing_products bp ON be.product_id = bp.id LEFT JOIN tenants t ON be.tenant_id = t.id LEFT JOIN users u ON be.user_id = u.id LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id LEFT JOIN countries c ON tc.country_id = c.country_id"
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)

    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]

    # Get paginated billing events
    final_query = base_query + " ORDER BY be.created_at DESC LIMIT ? OFFSET ?"
    final_params = params + [limit, skip]

    cursor.execute(final_query, final_params)
    billing_events = cursor.fetchall()
    print(f"DEBUG: get_all_billing_events returning total_count={total_count}, billing_events_count={len(billing_events)}")
    conn.close()
    return total_count, [dict(event) for event in billing_events]

def get_tenant_hierarchy(tenant_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        WITH RECURSIVE tenant_hierarchy (id) AS (
            SELECT id FROM tenants WHERE id = ?
            UNION ALL
            SELECT t.id
            FROM tenants t
            JOIN tenant_hierarchy th ON t.parent_id = th.id
        )
        SELECT t.id, t.name, t.created_at, u.username as created_by_username, t.created_by as created_by_id, c.name as country, u.mobile_phone as admin_mobile_phone
        FROM tenants t
        LEFT JOIN users u ON t.created_by = u.id
        LEFT JOIN tenant_countries tc ON t.id = tc.tenant_id
        LEFT JOIN countries c ON tc.country_id = c.country_id
        WHERE t.id IN (SELECT id FROM tenant_hierarchy)
        ORDER BY t.name;
    """
    cursor.execute(sql, (tenant_id,))
    tenants_rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in tenants_rows]

# Example usage (for testing purposes)
if __name__ == "__main__":
    print("Difficulty Levels:", get_lookup_data_list('difficulty_levels'))
    print("Cognitive Levels:", get_lookup_data_list('cognitive_levels'))
    print("Learning Outcomes:", get_lookup_data_list('learning_outcomes'))

    # Example of inserting a question
    try:
        new_question_data = {
            "question_text": "What is the capital of Canada?",
            "choice_1": "Toronto",
            "choice_2": "Ottawa",
            "choice_3": "Vancouver",
            "choice_4": "Montreal",
            "correct_option": "Ottawa",
            "difficulty_level": "Easy",
            "cognitive_level": "Remembering",
            "learning_outcome": "Identify basic facts",
            "author_creator": "Test User",
            "mark": 1,
            "time_seconds": 30,
            "discriminating_factor": 0.5
        }
        inserted_id = insert_question(new_question_data)
        print(f"Inserted new question with ID: {inserted_id}")
    except ValueError as e:
        print(f"Error inserting question: {e}")
    except sqlite3.Error as e:
        print(f"Database error during insert: {e}")

def get_user_specific_audience_items(user_id: int, audience_type: str, field_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"user_{field_name}s"
    print(f"DEBUG: get_user_specific_audience_items - Attempting to query table: {table_name} for user_id: {user_id}")
    # Basic validation to prevent SQL injection for table_name
    if not table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        print(f"ERROR: get_user_specific_audience_items - Invalid field_name: {field_name}")
        raise ValueError("Invalid field_name")
    try:
        cursor.execute(f"SELECT id, name FROM {table_name} WHERE user_id = ?", (user_id,))
        items = cursor.fetchall()
        print(f"DEBUG: get_user_specific_audience_items - Successfully queried {table_name}. Items found: {len(items)}")
        conn.close()
        return [dict(item) for item in items]
    except sqlite3.OperationalError as e:
        print(f"ERROR: get_user_specific_audience_items - sqlite3.OperationalError: {e} for table: {table_name}")
        raise e
    except Exception as e:
        print(f"ERROR: get_user_specific_audience_items - An unexpected error occurred: {e} for table: {table_name}")
        raise e

def add_user_specific_audience_item(user_id: int, audience_type: str, field_name: str, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"user_{field_name}s"
    # Basic validation to prevent SQL injection for table_name
    if not table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        raise ValueError("Invalid field_name")
    cursor.execute(f"INSERT INTO {table_name} (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def delete_user_specific_audience_item(user_id: int, audience_type: str, field_name: str, item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"user_{field_name}s"
    # Basic validation to prevent SQL injection for table_name
    if not table_name.startswith("user_") or not re.match(r'^[a-zA-Z0-9_]+$', field_name):
        raise ValueError("Invalid field_name")
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

def get_unbanked_questions_for_user(user_id: int, tenant_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = """
        SELECT 
            q.question_id, q.author_creator, q.date_created, q.question_text,
            q.choice_1, q.choice_2, q.choice_3, q.choice_4, q.correct_option,
            dl.name as difficulty_level, cl.name as cognitive_level, lo.name as learning_outcome,
            qt.name as question_type,
            st.name as school_type, ss.name as subject, sy.name as year,
            um.name as major, uc.name as course, umt.name as material, us.name as semester,
            comp.name as company, dep.name as department, jr.name as job_role,
            q.mark, q.time_seconds, q.discriminating_factor, q.status, q.audience_type, q.variables, q.solution
        FROM questions q
        LEFT JOIN difficulty_levels dl ON q.difficulty_level_id = dl.id
        LEFT JOIN cognitive_levels cl ON q.cognitive_level_id = cl.id
        LEFT JOIN learning_outcomes lo ON q.learning_outcome_id = lo.id
        LEFT JOIN question_types qt ON q.question_type_id = qt.id
        LEFT JOIN school_types st ON q.school_type_id = st.id
        LEFT JOIN school_subjects ss ON q.subject_id = ss.id
        LEFT JOIN school_years sy ON q.year_id = sy.id
        LEFT JOIN university_majors um ON q.major_id = um.id
        LEFT JOIN university_courses uc ON q.course_id = uc.id
        LEFT JOIN university_materials umt ON q.material_id = umt.id
        LEFT JOIN university_semesters us ON q.semester_id = us.id
        LEFT JOIN companies comp ON q.company_id = comp.id
        LEFT JOIN departments dep ON q.department_id = dep.id
        LEFT JOIN job_roles jr ON q.job_role_id = jr.id
        WHERE q.user_id = ? AND q.tenant_id = ? AND q.tamsqb_bank_added = 0
    """
    cursor.execute(sql_query, (user_id, tenant_id))
    questions = cursor.fetchall()
    conn.close()
    
    questions_list = []
    for q in questions:
        question_dict = dict(q)
        if question_dict.get('variables'):
            question_dict['variables'] = json.loads(question_dict['variables'])
        questions_list.append(question_dict)
    return questions_list

def update_question_tamsqb_bank_added_status(question_id: int, status: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE questions SET tamsqb_bank_added = ? WHERE question_id = ?", (status, question_id))
    conn.commit()
    conn.close()

def insert_uploaded_file(user_id: int, tenant_id: int, file_name: str, file_path: str, file_type: str, extracted_content: Optional[str], task_id: Optional[int] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    upload_timestamp = datetime.datetime.now().isoformat()
    print(f"DEBUG: insert_uploaded_file - Inserting file_name: {file_name}, extracted_content length: {len(extracted_content) if extracted_content else 0}")
    cursor.execute(
        """INSERT INTO uploaded_files (user_id, tenant_id, file_name, file_path, file_type, upload_timestamp, extracted_content, task_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, tenant_id, file_name, file_path, file_type, upload_timestamp, extracted_content, task_id)
    )
    conn.commit()
    file_id = cursor.lastrowid
    print(f"DEBUG: insert_uploaded_file - File inserted with ID: {file_id}")
    conn.close()
    return file_id

def get_uploaded_file_content(file_id: int) -> Optional[str]:
    print(f"DEBUG: get_uploaded_file_content - Retrieving content for file_id: {file_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT extracted_content FROM uploaded_files WHERE id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result['extracted_content']:
        print(f"DEBUG: get_uploaded_file_content - Retrieved content length: {len(result['extracted_content'])}")
    else:
        print(f"DEBUG: get_uploaded_file_content - No content or empty content found for file_id: {file_id}")
    return result['extracted_content'] if result else None

def update_uploaded_file_task_id(file_id: int, task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE uploaded_files SET task_id = ? WHERE id = ?", (task_id, file_id))
    conn.commit()
    conn.close()


