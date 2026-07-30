import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='schooldemo12',
        port=3307
    )
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_COMMENT 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'schooldemo12'
        """)
        tables = cursor.fetchall()
        print("Tables and Comments in schooldemo12:")
        for table in tables:
            print(f"Name: {table[0]}, Comment: {table[1]}")
    connection.close()
except Exception as e:
    print(f"Error: {e}")
