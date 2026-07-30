#!/usr/bin/env python3
"""
Idempotent local demo seed for QuestAI (inst-QI-6016).

- Ensures questions.db exists (via setup_database.py when missing/incomplete)
- Ensures tenants / users / generation_models / generation_tasks / balances tables
- Seeds demo tenant + teacher user + dummy generation model

Usage (from inst-QI-6016, with venv activated):
  python scripts/seed_local_demo.py
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

QI_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = QI_ROOT / "questions.db"
DB_PATH = Path(os.getenv("DB_PATH", str(DEFAULT_DB)))

DEMO_TENANT_NAME = "Local Demo"
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo123"
DEMO_FULL_NAME = "Demo Teacher"
DUMMY_MODEL_API_NAME = "dummy"
DUMMY_MODEL_DISPLAY = "Dummy Generator"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, typedef: str) -> None:
    if column not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {typedef}")
        print(f"  + column {table}.{column}")


def _exec_script(conn: sqlite3.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)
    print(f"  executed {path.name}")


def ensure_base_from_setup_database() -> None:
    """Create questions.db + core lookup/questions schema if needed."""
    create_script = QI_ROOT / "create_question_db.sql"
    populate_script = QI_ROOT / "populate_lookup_tables.sql"

    need_create = not DB_PATH.exists()
    if not need_create:
        conn = _connect()
        try:
            need_create = not _table_exists(conn, "questions")
        finally:
            conn.close()

    if need_create:
        print(f"Creating base schema at {DB_PATH} …")
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = _connect()
        try:
            # Use IF NOT EXISTS-friendly path: wrap raw CREATE by executing once on empty DB
            _exec_script(conn, create_script)
            # Lookups may re-run: prefer INSERT OR IGNORE
            populate_sql = populate_script.read_text(encoding="utf-8")
            populate_sql = populate_sql.replace("INSERT INTO ", "INSERT OR IGNORE INTO ")
            conn.executescript(populate_sql)
            conn.commit()
            print(f"  populated lookups from {populate_script.name}")
        finally:
            conn.close()
    else:
        print(f"Base DB already present: {DB_PATH}")
        # Top up lookups idempotently
        conn = _connect()
        try:
            if _table_exists(conn, "difficulty_levels"):
                populate_sql = populate_script.read_text(encoding="utf-8")
                populate_sql = populate_sql.replace("INSERT INTO ", "INSERT OR IGNORE INTO ")
                conn.executescript(populate_sql)
                conn.commit()
        finally:
            conn.close()


def ensure_app_tables(conn: sqlite3.Connection) -> None:
    print("Ensuring app tables …")
    missing_sql = QI_ROOT / "create_all_missing_tables.sql"
    if missing_sql.exists():
        try:
            _exec_script(conn, missing_sql)
        except sqlite3.Error as e:
            # Partial apply is OK on older DBs; continue with explicit ensures
            print(f"  note: create_all_missing_tables.sql: {e}")

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_super_admin INTEGER DEFAULT 0,
            tenant_id INTEGER,
            email TEXT,
            audience_type TEXT,
            full_name TEXT,
            mobile_phone TEXT,
            role TEXT,
            institution TEXT,
            department TEXT,
            country TEXT,
            schooldemo12_user_id INTEGER,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS generation_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_api_name TEXT NOT NULL UNIQUE,
            generation_method TEXT NOT NULL,
            tenant_id INTEGER,
            is_default BOOLEAN NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            api_key TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        );

        CREATE TABLE IF NOT EXISTS generation_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            request_parameters TEXT,
            num_questions_requested INTEGER,
            num_questions_generated INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            tenant_id INTEGER,
            uploaded_file_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS billing_user_question_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            audience_type TEXT NOT NULL,
            balance INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE (user_id, audience_type)
        );
        """
    )

    if _table_exists(conn, "users"):
        for col, typedef in (
            ("is_admin", "INTEGER DEFAULT 0"),
            ("is_super_admin", "INTEGER DEFAULT 0"),
            ("tenant_id", "INTEGER"),
            ("email", "TEXT"),
            ("audience_type", "TEXT"),
            ("full_name", "TEXT"),
            ("mobile_phone", "TEXT"),
            ("role", "TEXT"),
            ("institution", "TEXT"),
            ("department", "TEXT"),
            ("country", "TEXT"),
            ("schooldemo12_user_id", "INTEGER"),
        ):
            _ensure_column(conn, "users", col, typedef)

    if _table_exists(conn, "generation_models"):
        _ensure_column(conn, "generation_models", "api_key", "TEXT")

    if _table_exists(conn, "tenants"):
        _ensure_column(conn, "tenants", "created_by", "INTEGER")

    conn.commit()


def _hash_password(password: str) -> str:
    try:
        import bcrypt
    except ImportError as e:
        raise SystemExit(
            "bcrypt is required. Activate the venv and: pip install -r backend/requirements.txt"
        ) from e
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_tenant(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM tenants WHERE name = ?", (DEMO_TENANT_NAME,)).fetchone()
    if row:
        print(f"Tenant '{DEMO_TENANT_NAME}' already exists (id={row['id']}).")
        return int(row["id"])
    cur = conn.execute("INSERT INTO tenants (name) VALUES (?)", (DEMO_TENANT_NAME,))
    tenant_id = int(cur.lastrowid)
    print(f"Created tenant '{DEMO_TENANT_NAME}' (id={tenant_id}).")
    return tenant_id


def seed_demo_user(conn: sqlite3.Connection, tenant_id: int) -> int:
    row = conn.execute("SELECT id FROM users WHERE username = ?", (DEMO_USERNAME,)).fetchone()
    hashed = _hash_password(DEMO_PASSWORD)
    if row:
        conn.execute(
            """
            UPDATE users
            SET password = ?, is_admin = 1, tenant_id = ?, full_name = ?,
                audience_type = COALESCE(audience_type, 'school'),
                role = COALESCE(role, 'teacher'),
                email = COALESCE(email, 'demo@localhost')
            WHERE id = ?
            """,
            (hashed, tenant_id, DEMO_FULL_NAME, row["id"]),
        )
        print(f"Updated demo user '{DEMO_USERNAME}' (id={row['id']}).")
        return int(row["id"])

    cur = conn.execute(
        """
        INSERT INTO users (
            username, password, is_admin, is_super_admin, full_name,
            tenant_id, email, audience_type, role
        ) VALUES (?, ?, 1, 0, ?, ?, ?, 'school', 'teacher')
        """,
        (DEMO_USERNAME, hashed, DEMO_FULL_NAME, tenant_id, "demo@localhost"),
    )
    user_id = int(cur.lastrowid)
    print(f"Created demo user '{DEMO_USERNAME}' (id={user_id}).")
    return user_id


def seed_dummy_model(conn: sqlite3.Connection, tenant_id: int) -> None:
    row = conn.execute(
        "SELECT id FROM generation_models WHERE model_api_name = ?",
        (DUMMY_MODEL_API_NAME,),
    ).fetchone()
    if row:
        conn.execute(
            """
            UPDATE generation_models
            SET model_name = ?, generation_method = 'ai', tenant_id = ?,
                is_default = 1, is_active = 1, api_key = 'dummy_key'
            WHERE id = ?
            """,
            (DUMMY_MODEL_DISPLAY, tenant_id, row["id"]),
        )
        print(f"Updated dummy model '{DUMMY_MODEL_API_NAME}' (id={row['id']}).")
        return

    conn.execute(
        """
        INSERT INTO generation_models (
            model_name, model_api_name, generation_method,
            tenant_id, is_default, is_active, api_key
        ) VALUES (?, ?, 'ai', ?, 1, 1, 'dummy_key')
        """,
        (DUMMY_MODEL_DISPLAY, DUMMY_MODEL_API_NAME, tenant_id),
    )
    print(f"Created dummy model '{DUMMY_MODEL_API_NAME}'.")


def seed_balances(conn: sqlite3.Connection, user_id: int) -> None:
    """Optional credits for non-dummy models; dummy generate skips balance checks."""
    for audience in ("school", "university", "company"):
        conn.execute(
            """
            INSERT OR IGNORE INTO billing_user_question_balances (user_id, audience_type, balance)
            VALUES (?, ?, 1000)
            """,
            (user_id, audience),
        )
        conn.execute(
            """
            UPDATE billing_user_question_balances
            SET balance = MAX(balance, 100)
            WHERE user_id = ? AND audience_type = ?
            """,
            (user_id, audience),
        )
    print(f"Ensured question balances for user_id={user_id}.")


def main() -> int:
    os.chdir(QI_ROOT)
    print(f"QI root: {QI_ROOT}")
    print(f"DB path: {DB_PATH}")

    ensure_base_from_setup_database()

    conn = _connect()
    try:
        ensure_app_tables(conn)
        tenant_id = seed_tenant(conn)
        user_id = seed_demo_user(conn, tenant_id)
        seed_dummy_model(conn, tenant_id)
        seed_balances(conn, user_id)
        conn.commit()
    finally:
        conn.close()

    print()
    print("Local demo seed complete.")
    print(f"  Login:  {DEMO_USERNAME} / {DEMO_PASSWORD}")
    print(f"  Model:  {DUMMY_MODEL_DISPLAY} ({DUMMY_MODEL_API_NAME})")
    print("  Next:   python run_server.py")
    print("          cd frontend && python3 -m http.server 6016")
    return 0


if __name__ == "__main__":
    sys.exit(main())
