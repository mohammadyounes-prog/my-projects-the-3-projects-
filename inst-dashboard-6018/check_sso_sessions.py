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
        cursor.execute("SELECT NOW()")
        now = cursor.fetchone()
        print(f"MySQL NOW(): {now[0]}")
        cursor.execute("SELECT * FROM sso_sessions")
        rows = cursor.fetchall()
        print("SSO Sessions in schooldemo12:")
        for row in rows:
            print(row)
    connection.close()
except Exception as e:
    print(f"Error: {e}")
