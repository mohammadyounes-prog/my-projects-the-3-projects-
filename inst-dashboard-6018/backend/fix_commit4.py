with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f:
    content = f.read()

# Show lines 610-640 to see exact current state
lines = content.split('\n')
print("Current state lines 610-645:")
for i in range(609, 644):
    print(f"{i+1}: {repr(lines[i])}")
