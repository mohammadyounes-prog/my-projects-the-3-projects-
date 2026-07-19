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

def inspect_bank_table_schema():
    """Connects to the online-exam database and shows the CREATE TABLE statement for the 'bank' table."""
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
        print("\n--- Schema for 'bank' table ---")
        cursor.execute("SHOW CREATE TABLE bank;")
        schema = cursor.fetchone()
        if schema:
            # The 'Create Table' key holds the DDL statement
            print(schema['Create Table'])
        else:
            print("Table 'bank' not found.")
        print("-------------------------------")

    except pymysql.Error as e:
        print(f"ERROR: Could not connect to online-exam MySQL database or inspect table: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Load environment variables if not already loaded (e.g., when running standalone)
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')
    inspect_bank_table_schema()
