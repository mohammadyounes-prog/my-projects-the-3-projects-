import mysqli
import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="schooldemo12",
        port=3307
    )
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in schooldemo12:")
    for table in tables:
        print(table[0])
    db.close()
except Exception as e:
    print(f"Error: {e}")
