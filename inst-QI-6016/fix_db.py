import sqlite3

# Using forward slashes for better compatibility with Python on Windows when using raw strings
db_path = 'E:/questionretrieval/new-q-bank/config-manager/backend/instances.db'
instance_name = 'inst-questai-6016'
new_frontend_port = 6017

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE instances SET frontend_port=? WHERE instance_name=?", (new_frontend_port, instance_name))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"Successfully updated {instance_name} frontend_port to {new_frontend_port}")
    else:
        print(f"No instance found with name {instance_name}")
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
