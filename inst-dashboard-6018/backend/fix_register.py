with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    content = f.read()

old_block = '''    except HTTPException as e:
        # Rollback on HTTPException
        db.rollback()
        raise e
    except Exception as e:
        # Rollback on any other exception
        db.rollback()
        logging.exception(f"FATAL EXCEPTION in register_user (outer block)") # Differentiate this log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
       try:
            cur.close()
       except Exception:
            pass
        # Ensure the cursor is closed

        cur.close()'''

new_block = '''    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        logging.exception(f"FATAL EXCEPTION in register_user (outer block)")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            cur.close()
        except Exception:
            pass'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w') as f:
        f.write(content)
    print("SUCCESS: Fixed the finally block!")
else:
    print("ERROR: Could not find the block. Trying to show what's there...")
    # Show the finally area
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'finally:' in line and i > 400:
            for j in range(max(0,i-5), min(len(lines), i+15)):
                print(f"{j+1}: {repr(lines[j])}")
            break
