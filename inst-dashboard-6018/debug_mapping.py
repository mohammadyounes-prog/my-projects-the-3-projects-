import sqlite3
import mysql.connector
from pathlib import Path
import os
from dotenv import load_dotenv

# Path to the .env file in the parent of the project
ENV_FILE_PATH = Path(r"E:\questionretrieval\new-q-bank\.env")
load_dotenv(dotenv_path=ENV_FILE_PATH)

# SQLite QuestAI DB
QUESTAI_DB_PATH = r"E:\questionretrieval\new-q-bank\instances\cust-1\inst-QI-6016\questions.db"

# MySQL Exam DB details
DB_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("ONLINE_EXAM_MYSQL_PORT", "3307"))
DB_USER = os.getenv("ONLINE_EXAM_MYSQL_USER")
DB_PASS = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD")
DB_NAME = os.getenv("ONLINE_EXAM_MYSQL_DB")

def inspect_mapping():
    # ... (connection setup)
    # 2. Connect to MySQL
    mysql_conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME)
    # ... rest of the code
    # Get a sample result
    mysql_cursor.execute("SELECT examDataId FROM studentresult LIMIT 1")
    res = mysql_cursor.fetchone()
    if not res:
        print("No results found in studentresult.")
        return

    examDataId = res['examDataId']
    print(f"DEBUG: Inspecting sample examDataId: {examDataId}")
    
    # Get bankId for this examDataId
    mysql_cursor.execute("SELECT bankId FROM examdata WHERE id = %s", (examDataId,))
    examdata = mysql_cursor.fetchone()
    
    if not examdata:
        print(f"DEBUG: No examdata found for examDataId: {examDataId}")
    else:
        bankId = examdata['bankId']
        print(f"DEBUG: Found bankId: {bankId} for examDataId: {examDataId}")
        
        if bankId in q_lo_map:
            print("SUCCESS: bankId is in q_lo_map.")
        else:
            print("FAILURE: bankId is NOT in q_lo_map.")
            # Check what's in q_lo_map keys
            sample_keys = list(q_lo_map.keys())[:5]
            print(f"DEBUG: Sample keys in q_lo_map: {sample_keys}")
            print(f"DEBUG: Type of bankId: {type(bankId)}")
            print(f"DEBUG: Type of q_lo_map keys: {type(sample_keys[0])}")

    mysql_conn.close()
    sqlite_conn.close()

if __name__ == "__main__":
    inspect_mapping()
