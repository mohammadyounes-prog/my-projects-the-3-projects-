import sqlite3
conn = sqlite3.connect('E:/questionretrieval/new-q-bank/instances/cust-1/inst-QI-6016/backend/questions.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
