echo import sys > tmpcheck.py
echo with open('D:/questionretrieval/new-q-bank/backend/main.py', 'r') as f: >> tmpcheck.py
echo     lines = f.readlines() >> tmpcheck.py
echo for i, line in enumerate(lines[638:660], start=639): >> tmpcheck.py
echo     print(f'{i}: {repr(line)}') >> tmpcheck.py
python tmpcheck.py