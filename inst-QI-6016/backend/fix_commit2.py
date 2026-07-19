with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    lines = f.readlines()

# Find the "Just before final db.commit" line
for i, line in enumerate(lines):
    if 'Just before final db.commit' in line:
        # Check if cur.close() is already right before it
        prev = lines[i-1].strip() if i > 0 else ''
        if 'cur.close()' in prev:
            print(f"cur.close() already at line {i}, no change needed")
        else:
            # Insert cur.close() before this line, matching indentation (8 spaces)
            lines.insert(i, '        cur.close()\n')
            with open('D:/questionretrieval/new-q-bank/backend/main.py', 'w') as f:
                f.writelines(lines)
            print(f"SUCCESS: Inserted cur.close() before line {i+1}")
            # Verify
            for j in range(i-1, i+5):
                print(f"{j+1}: {repr(lines[j])}")
        break
