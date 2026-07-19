import sqlite3
import os

db_path = 'E:/questionretrieval/new-q-bank/config-manager/backend/instances.db'
instance_name = 'instance-questai-6016'

conn = None
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT base_path FROM instances WHERE instance_name=?", (instance_name,))
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print(f'Instance "{instance_name}" not found.')
except sqlite3.Error as e:
    print(f'Database error: {e}')
except Exception as e:
    print(f'An error occurred: {e}')
finally:
    if conn:
        conn.close()
