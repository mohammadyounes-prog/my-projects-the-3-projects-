with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the register_user function and replace the entire try block
# The strategy: remove all cursor=cur passing, close cur early, use db directly for raw SQL

old = '''@app.post("/register")
async def register_user(payload: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    # Use a single cursor for all operations within this function for transactional integrity
    cur = db.cursor()
    try:'''

new = '''@app.post("/register")
async def register_user(payload: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    try:'''

if old in content:
    content = content.replace(old, new)
    print("Step 1: OK")
else:
    print("Step 1: not found, skipping")

# Remove cursor=cur from all sub-function calls, keep conn=db
import re
content = re.sub(r',\s*conn=db,\s*cursor=cur', ', conn=db', content)
content = re.sub(r',\s*cursor=cur\b', '', content)
print("Step 2: Removed all cursor=cur from sub-function calls")

# Now close cur right after the last direct cur.execute in the function
# The last direct use of cur is the tenant_countries INSERT
# Let's close cur right before create_user call since create_user will use conn=db with its own cursor

old2 = '''        existing = get_user(payload.username, tenant_id=tenant_id, conn=db)
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed = get_password_hash(payload.password)
        # create_user supports hashed_password
        # Pass the connection and cursor to create_user
        created_user_id = create_user('''

new2 = '''        existing = get_user(payload.username, tenant_id=tenant_id, conn=db)
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

        cur.close()  # Done with direct cursor operations - close before sub-function calls

        hashed = get_password_hash(payload.password)
        created_user_id = create_user('''

if old2 in content:
    content = content.replace(old2, new2)
    print("Step 3: Added cur.close() before create_user")
else:
    # Try without the comment lines
    old2b = '''        existing = get_user(payload.username, tenant_id=tenant_id, conn=db)
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed = get_password_hash(payload.password)'''
    if old2b in content:
        content = content.replace(old2b, 
            '''        existing = get_user(payload.username, tenant_id=tenant_id, conn=db)
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

        cur.close()  # Done with direct cursor operations

        hashed = get_password_hash(payload.password)''')
        print("Step 3b: Added cur.close() before hashed")
    else:
        print("Step 3: ERROR - could not find insertion point")

# Remove the duplicate cur.close() that was added before get_user_by_id
content = content.replace(
    '        cur.close()  # Close cursor before get_user_by_id to release all in-progress statements\n        created_user = get_user_by_id(',
    '        created_user = get_user_by_id('
)
print("Step 4: Removed duplicate cur.close()")

with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Verifying register function area:")
lines = content.split('\n')
in_register = False
for i, line in enumerate(lines):
    if '@app.post("/register")' in line:
        in_register = True
    if in_register:
        print(f"{i+1}: {line}")
    if in_register and i > 400 and 'class QuestionRequest' in line:
        break
