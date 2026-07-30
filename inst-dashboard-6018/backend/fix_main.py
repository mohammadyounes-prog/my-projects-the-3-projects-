with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    content = f.read()

# The bad block
old = '    finally:\n       try:\n            cur.close()\n       except Exception:\n            pass\n        # Ensure the cursor is closed\n\n        cur.close()\n'

# The correct block
new = '    finally:\n        try:\n            cur.close()\n        except Exception:\n            pass\n'

if old in content:
    content = content.replace(old, new)
    with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w') as f:
        f.write(content)
    print("SUCCESS: Fixed indentation in main.py")
else:
    print("ERROR: Could not find the exact block to replace. No changes made.")
    print("Please fix manually in Notepad.")
