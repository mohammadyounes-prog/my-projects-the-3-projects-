import sqlite3
conn = sqlite3.connect(r'E:\questionretrieval\new-q-bank\config-manager\backend\instances.db')
cursor = conn.cursor()
cursor.execute("UPDATE instances SET base_path = replace(base_path, 'E:/instances', 'E:/questionretrieval/new-q-bank/instances')")
conn.commit()
print(f"{cursor.rowcount} rows updated")
conn.close()
