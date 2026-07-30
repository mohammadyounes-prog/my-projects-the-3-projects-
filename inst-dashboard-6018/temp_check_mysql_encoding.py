import pymysql
import os
import json
from pathlib import Path
from fastapi import HTTPException, status # Needed for get_online_exam_db_connection
import sys

# Assume these are defined as in online_exam_db_connector.py
MYSQL_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST")
MYSQL_PORT = os.getenv("ONLINE_EXAM_MYSQL_PORT")
MYSQL_USER = os.getenv("ONLINE_EXAM_MYSQL_USER")
MYSQL_PASSWORD = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD")
MYSQL_DB = os.getenv("ONLINE_EXAM_MYSQL_DB")

# Explicitly print environment variables for debugging
print(f"DEBUG ENV - MYSQL_HOST: {MYSQL_HOST}", flush=True)
print(f"DEBUG ENV - MYSQL_PORT: {MYSQL_PORT}", flush=True)
print(f"DEBUG ENV - MYSQL_USER: {MYSQL_USER}", flush=True)
print(f"DEBUG ENV - MYSQL_PASSWORD: {'*' * len(MYSQL_PASSWORD) if MYSQL_PASSWORD else 'None'}", flush=True) # Mask password
print(f"DEBUG ENV - MYSQL_DB: {MYSQL_DB}", flush=True)

def get_online_exam_db_connection():
    """Establishes and returns a connection to the online-exam project's MySQL database."""
    try:
        # Convert port to int, provide default if None
        port_int = int(MYSQL_PORT) if MYSQL_PORT else 3307

        conn = pymysql.connect(
            host=MYSQL_HOST if MYSQL_HOST else "localhost",
            port=port_int,
            user=MYSQL_USER if MYSQL_USER else "root",
            password=MYSQL_PASSWORD if MYSQL_PASSWORD else "root",
            database=MYSQL_DB if MYSQL_DB else "schooldemo12",
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            use_unicode=True
        )
        print("DEBUG: Successfully connected to MySQL database.", flush=True)
        return conn
    except pymysql.Error as e:
        print(f"ERROR: Could not connect to online-exam MySQL database: {e}", file=sys.stdout, flush=True) # Redirect to stdout
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {e}"
        )
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during connection: {e}", file=sys.stdout, flush=True) # Redirect to stdout
        raise e

def check_mysql_encoding_settings():
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()

        print("\n--- MySQL Server & Database Character Set Settings ---", flush=True)
        cursor.execute("SHOW VARIABLES LIKE 'character_set%';")
        for row in cursor.fetchall():
            print(f"{row['Variable_name']}: {row['Value']}", flush=True)
        
        cursor.execute("SHOW VARIABLES LIKE 'collation%';")
        for row in cursor.fetchall():
            print(f"{row['Variable_name']}: {row['Value']}", flush=True)

        print(f"\n--- Database '{MYSQL_DB}' Character Set ---", flush=True)
        cursor.execute(f"SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{MYSQL_DB}';")
        db_info = cursor.fetchone()
        if db_info:
            print(f"Database Character Set: {db_info['DEFAULT_CHARACTER_SET_NAME']}", flush=True)
            print(f"Database Collation: {db_info['DEFAULT_COLLATION_NAME']}", flush=True)
        else:
            print(f"Could not retrieve info for database '{MYSQL_DB}'.", flush=True)

        print("\n--- 'bank' Table and 'answers' Column Character Set ---", flush=True)
        cursor.execute("SHOW CREATE TABLE bank;")
        create_table_sql = cursor.fetchone()['Create Table']
        print(create_table_sql, flush=True)

        # Extract column info more precisely
        cursor.execute(f"SELECT COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{MYSQL_DB}' AND TABLE_NAME = 'bank' AND COLUMN_NAME = 'answers';")
        answers_column_info = cursor.fetchone()
        if answers_column_info:
            print(f"\nAnswers Column ('answers') in 'bank' Table:", flush=True)
            print(f"  Column Type: {answers_column_info['COLUMN_TYPE']}", flush=True)
            print(f"  Character Set: {answers_column_info['CHARACTER_SET_NAME']}", flush=True)
            print(f"  Collation: {answers_column_info['COLLATION_NAME']}", flush=True)
        else:
            print("Could not retrieve info for 'answers' column in 'bank' table.", flush=True)

    except pymysql.Error as e:
        print(f"ERROR: MySQL query failed: {e}", file=sys.stdout, flush=True) # Redirect to stdout
    except HTTPException as e:
        print(f"ERROR: {e.detail}", file=sys.stdout, flush=True) # Redirect to stdout
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stdout, flush=True) # Redirect to stdout
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Load environment variables if they exist
    dotenv_path = Path(__file__).resolve().parent.parent / '.env'
    try:
        if dotenv_path.exists():
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=dotenv_path)
            print(f"DEBUG: .env file loaded from {dotenv_path}", flush=True)
        else:
            print(f"WARNING: .env file not found at {dotenv_path}. Using default MySQL connection parameters or system environment variables.", file=sys.stdout, flush=True)
    except Exception as e:
        print(f"ERROR: Failed to load .env file: {e}", file=sys.stdout, flush=True)
    
    check_mysql_encoding_settings()