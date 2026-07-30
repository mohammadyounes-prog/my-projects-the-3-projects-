import sys 
with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f: 
    lines = f.readlines() 
for i, line in enumerate(lines[638:660], start=639): 
    print(f'{i}: {repr(line)}') 
