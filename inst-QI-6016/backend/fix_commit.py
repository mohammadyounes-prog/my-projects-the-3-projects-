with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    content = f.read()

old = '''        logging.debug("DEBUG: Just before final db.commit().")
        try:
            cur.close()
            db.commit() # Commit all changes at the very end of the successful transaction 
            logging.debug("DEBUG: After final db.commit().")
        except Exception as commit_e:
            db.rollback()
            logging.exception(f"FATAL EXCEPTION during final db.commit() in register_user")
            raise HTTPException(status_code=500, detail=f"Database commit failed: {commit_e}")'''

new = '''        cur.close()
        logging.debug("DEBUG: Just before final db.commit().")
        try:
            db.commit() # Commit all changes at the very end of the successful transaction
            logging.debug("DEBUG: After final db.commit().")
        except Exception as commit_e:
            db.rollback()
            logging.exception(f"FATAL EXCEPTION during final db.commit() in register_user")
            raise HTTPException(status_code=500, detail=f"Database commit failed: {commit_e}")'''

if old in content:
    content = content.replace(old, new)
    with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w') as f:
        f.write(content)
    print("SUCCESS: Moved cur.close() before db.commit()!")
else:
    # Try to find the commit block to show context
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Just before final db.commit' in line:
            print(f"Found commit block at line {i+1}, showing context:")
            for j in range(max(0,i-3), min(len(lines), i+12)):
                print(f"{j+1}: {repr(lines[j])}")
            break
    else:
        print("ERROR: Could not find commit block at all")
