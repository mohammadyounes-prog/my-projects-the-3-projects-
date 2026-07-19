import sqlite3
db_path = r'E:\instances\cust-2\instance-questAI-6016\question-retrieval\questions.db'
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cur.fetchall())
    conn.close()
except Exception as e:
    print(f"Error: {e}")
