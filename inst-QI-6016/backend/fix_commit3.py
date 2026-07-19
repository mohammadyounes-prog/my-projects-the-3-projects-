with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    content = f.read()

# Show lines around get_user_by_id and the commit
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'get_user_by_id' in line and i > 400:
        print(f"Found get_user_by_id at line {i+1}:")
        for j in range(max(0,i-2), min(len(lines), i+10)):
            print(f"{j+1}: {repr(lines[j])}")
        break

# The fix: replace the get_user_by_id call + commit block
old = '''        created_user = get_user_by_id(created_user_id, tenant_id=tenant_id, conn=db, cursor=cur)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")'''

new = '''        created_user = get_user_by_id(created_user_id, tenant_id=tenant_id, conn=db, cursor=cur)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")
        cur.close()  # Close cursor before commit to release all in-progress statements'''

if old in content:
    # Also remove any existing cur.close() that's right before the logging line
    content = content.replace(
        '        cur.close()\n        logging.debug("DEBUG: Just before final db.commit().")',
        '        logging.debug("DEBUG: Just before final db.commit().")'
    )
    content = content.replace(old, new)
    with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w') as f:
        f.write(content)
    print("\nSUCCESS: Fixed! cur.close() now placed right after get_user_by_id")
else:
    print("\nERROR: Could not find the get_user_by_id block to replace")
    print("Showing content around that area...")
