import pymysql
import os
from pathlib import Path

# Database configuration for the online-exam project's MySQL database
# These values are derived from D:\QuestionRetrieval\new-q-bank\TAMS\app\schooldemo12\apps\online-exam\config.php
MYSQL_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("ONLINE_EXAM_MYSQL_PORT", 3307))
MYSQL_DB = os.getenv("ONLINE_EXAM_MYSQL_DB", "schooldemo12")
MYSQL_USER = os.getenv("ONLINE_EXAM_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD", "root")

def list_tables_in_online_exam_db():
    """Connects to the online-exam database and lists all tables."""
    conn = None
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        print(f"Connected to database: {MYSQL_DB} on {MYSQL_HOST}:{MYSQL_PORT}")
        print("\n--- Tables in schooldemo12 database ---")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            # The key for the table name depends on the pymysql version and cursor type
            # It's usually the first value or 'Tables_in_dbname'
            table_name = list(table.values())[0]
            print(f"- {table_name}")
        print("--------------------------------------")

    except pymysql.Error as e:
        print(f"ERROR: Could not connect to online-exam MySQL database or list tables: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Load environment variables if not already loaded (e.g., when running standalone)
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')
    list_tables_in_online_exam_db()
