import sqlite3
import os

DATABASE_PATH = "E:/questionretrieval/new-q-bank/config-manager/backend/instances.db"

def query_instances():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT instance_name, app_port, status FROM instances WHERE app_port = 6016")
        instances = [dict(row) for row in cursor.fetchall()]
        return instances
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    found_instances = query_instances()
    if found_instances:
        for instance in found_instances:
            print(f"Instance Name: {instance['instance_name']}")
            print(f"App Port: {instance['app_port']}")
            print(f"Status: {instance['status']}")
            print("")
    else:
        print("No instances found with base port 6016 or an error occurred.")
