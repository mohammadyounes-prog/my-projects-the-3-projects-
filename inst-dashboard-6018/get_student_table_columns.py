import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("ONLINE_EXAM_MYSQL_PORT", 3307))
MYSQL_DB = os.getenv("ONLINE_EXAM_MYSQL_DB", "schooldemo12")
MYSQL_USER = os.getenv("ONLINE_EXAM_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD", "root")

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
    cursor.execute("SHOW COLUMNS FROM student;")
    columns_info = cursor.fetchall()
    
    if columns_info:
        # Get the last 10 columns
        last_10_columns = columns_info[-10:]
        print("Last 10 columns of the 'student' table in schooldemo12:")
        for col in last_10_columns:
            print(f"  Field: {col['Field']}, Type: {col['Type']}")
    else:
        print("No columns found for 'student' table or table does not exist.")
    
    cursor.close()
    conn.close()

except pymysql.Error as e:
    print(f"Error connecting to or querying schooldemo12 database: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
