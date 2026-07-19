with open('D:/questionretrieval/new-q-bank/backend/database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find create_generation_model function
for i, line in enumerate(lines):
    if 'def create_generation_model' in line:
        print(f"create_generation_model starts at line {i+1}:")
        for j in range(i, min(len(lines), i+40)):
            print(f"{j+1}: {repr(lines[j])}")
        break

print("\n---\n")

# Find get_user_by_id function
for i, line in enumerate(lines):
    if 'def get_user_by_id' in line:
        print(f"get_user_by_id starts at line {i+1}:")
        for j in range(i, min(len(lines), i+25)):
            print(f"{j+1}: {repr(lines[j])}")
        break

print("\n---\n")

# Find create_tenant function
for i, line in enumerate(lines):
    if 'def create_tenant' in line:
        print(f"create_tenant starts at line {i+1}:")
        for j in range(i, min(len(lines), i+25)):
            print(f"{j+1}: {repr(lines[j])}")
        break
