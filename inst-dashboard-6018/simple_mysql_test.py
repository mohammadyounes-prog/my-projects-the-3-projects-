
import pymysql
import os

MYSQL_HOST = "localhost"
MYSQL_PORT = 3307
MYSQL_DB = "schooldemo12"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"

print(f"Connecting to {MYSQL_HOST}:{MYSQL_PORT}...")
try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connection successful!")
    cur = conn.cursor()
    
    cur.execute("SELECT id, xId, name FROM student WHERE xId LIKE '%teacher110%'")
    print("Students:", cur.fetchall())
    
    cur.execute("SELECT id, name, email FROM employee WHERE name LIKE '%teacher110%'")
    print("Employees:", cur.fetchall())
    
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
