with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        created_user = get_user_by_id(created_user_id, tenant_id=tenant_id, conn=db, cursor=cur)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")
        cur.close()  # Close cursor before commit to release all in-progress statements'''

new = '''        cur.close()  # Close cursor before get_user_by_id to release all in-progress statements
        created_user = get_user_by_id(created_user_id, tenant_id=tenant_id, conn=db)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")'''

if old in content:
    content = content.replace(old, new)
    with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: cur.close() now before get_user_by_id, and cursor=cur removed from that call")
else:
    print("ERROR: Could not find block. Showing lines 615-625:")
    lines = content.split('\n')
    for i in range(614, 625):
        print(f"{i+1}: {repr(lines[i])}")
