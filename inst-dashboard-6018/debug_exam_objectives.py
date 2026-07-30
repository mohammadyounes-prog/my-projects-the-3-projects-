
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
    
    # Get latest 5 exams
    cur.execute("SELECT id, name, date, status FROM exam ORDER BY id DESC LIMIT 5")
    exams = cur.fetchall()
    print("--- LATEST EXAMS ---")
    for exam in exams:
        print(exam)
        
    if exams:
        exam_id = exams[0]['id']
        print(f"\n--- Checking examId: {exam_id} ---")
        
        # Check examdata for this exam
        cur.execute("SELECT id, bankId, title FROM examdata WHERE examId = %s", (exam_id,))
        exam_data = cur.fetchall()
        print(f"Found {len(exam_data)} questions in examdata.")
        
        if exam_data:
            bank_ids = [str(row['bankId']) for row in exam_data]
            bank_ids_str = ",".join(bank_ids)
            
            # Check filtersdata for these bankIds with type 3
            cur.execute(f"SELECT * FROM filtersdata WHERE bankId IN ({bank_ids_str}) AND type = 3")
            filters = cur.fetchall()
            print(f"Found {len(filters)} entries in filtersdata with type=3.")
            for f in filters[:5]:
                print(f)
                
            if filters:
                filter_ids = [str(f['filterId']) for f in filters]
                filter_ids_str = ",".join(filter_ids)
                
                # Check objective table
                cur.execute(f"SELECT * FROM objective WHERE id IN ({filter_ids_str})")
                objectives = cur.fetchall()
                print(f"Found {len(objectives)} entries in objective table.")
                for obj in objectives[:5]:
                    print(obj)
            else:
                print("No type=3 filters found for these bankIds. This is why objectives are missing.")
                
                # Check what types DO exist for these bankIds
                cur.execute(f"SELECT type, count(*) as count FROM filtersdata WHERE bankId IN ({bank_ids_str}) GROUP BY type")
                types = cur.fetchall()
                print("Available types in filtersdata for these bankIds:", types)

    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
