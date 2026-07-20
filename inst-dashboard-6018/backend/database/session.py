# Database Connection Management

import sqlite3
import pymysql
import os
from pathlib import Path
from fastapi.concurrency import run_in_threadpool
from contextlib import contextmanager

# --- Import Settings ---
# Assuming settings are loaded from a central config module
try:
    from ..core.config import get_settings
    settings = get_settings()
except ImportError:
    # Fallback for direct execution or when config module isn't yet set up
    print("WARNING: Could not import settings from ..core.config. Using fallback.")
    # Define placeholder settings if import fails
    class PlaceholderSettings:
        # Resolve path to be one level above 'newboard'
        _root = Path(__file__).resolve().parent.parent.parent.parent
        QUESTAI_DB_PATH = str(_root / 'questions.db')
        ONLINE_EXAM_DB_HOST = os.getenv("ONLINE_EXAM_DB_HOST", "localhost")
        ONLINE_EXAM_DB_PORT = int(os.getenv("ONLINE_EXAM_DB_PORT", 3306))
        ONLINE_EXAM_DB_NAME = os.getenv("ONLINE_EXAM_DB_NAME", "schooldemo12")
        ONLINE_EXAM_DB_USER = os.getenv("ONLINE_EXAM_DB_USER", "root")
        ONLINE_EXAM_DB_PASS = os.getenv("ONLINE_EXAM_DB_PASS", "your_mysql_password")
    settings = PlaceholderSettings()

# --- QuestAI SQLite Connection ---
def get_questai_db_connection():
    """Synchronous connection to QuestAI SQLite DB."""
    try:
        print(f"DEBUG: Connecting to SQLite at {settings.QUESTAI_DB_PATH}")
        # Add check_same_thread=False to allow sharing the connection across threads
        conn = sqlite3.connect(settings.QUESTAI_DB_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to QuestAI SQLite DB: {e}")
        raise

async def get_questai_db():
    """Async generator to provide QuestAI SQLite DB connection for FastAPI."""
    conn = await run_in_threadpool(get_questai_db_connection)
    try:
        yield conn
    finally:
        await run_in_threadpool(conn.close)

# --- Online Exam MySQL Connection ---
# Using a simple context manager for MySQL connections to manage pooling or ensure closure.
# For production, consider a more robust connection pooling library.
def get_online_exam_db_connection():
    """Synchronous connection to Online Exam MySQL DB."""
    try:
        print(f"DEBUG: Connecting to MySQL at {settings.ONLINE_EXAM_DB_HOST}:{settings.ONLINE_EXAM_DB_PORT}")
        conn = pymysql.connect(
            host=settings.ONLINE_EXAM_DB_HOST,
            port=settings.ONLINE_EXAM_DB_PORT,
            user=settings.ONLINE_EXAM_DB_USER,
            password=settings.ONLINE_EXAM_DB_PASS,
            database=settings.ONLINE_EXAM_DB_NAME,
            cursorclass=pymysql.cursors.DictCursor # Return rows as dictionaries
        )
        return conn
    except pymysql.Error as e:
        print(f"DEBUG: MySQL connection parameters: host={settings.ONLINE_EXAM_DB_HOST}, port={settings.ONLINE_EXAM_DB_PORT}, user={settings.ONLINE_EXAM_DB_USER}, db={settings.ONLINE_EXAM_DB_NAME}")
        print(f"Error connecting to Online Exam MySQL DB: {e}")
        raise

# --- Main Application Configuration ---
# You might have other database-related functions here, e.g., for creating tables
# or running migrations if this dashboard manages its own DB.
# For now, we focus on connecting to the *external* databases.

# Example of how you might use these connections in your API endpoints:
# from fastapi import Depends
# from .database.session import get_questai_db, get_online_exam_db_connection
#
# @app.get("/questai/questions")
# async def read_questai_questions(db: sqlite3.Connection = Depends(get_questai_db)):
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM questions LIMIT 10")
#     rows = cursor.fetchall()
#     return [dict(row) for row in rows]
#
# @app.get("/online-exam/courses")
# def read_online_exam_courses():
#     conn = get_online_exam_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT * FROM courses LIMIT 10")
#             return cursor.fetchall()
#     finally:
#         conn.close()
