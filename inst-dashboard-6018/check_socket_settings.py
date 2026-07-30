
import pymysql

MYSQL_HOST = "localhost"
MYSQL_PORT = 3307
MYSQL_DB = "schooldemo12"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"

try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM settings WHERE name LIKE '%socket%'")
    settings = cur.fetchall()
    print("--- SOCKET SETTINGS IN DB ---")
    for s in settings:
        print(s)
        
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
