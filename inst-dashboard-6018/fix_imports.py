import os
import re

directory = r"E:\questionretrieval\new-q-bank\test-questai\backend"

for filename in os.listdir(directory):
    if filename.endswith(".py"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace 'from . import <module>' with 'import <module>'
        new_content = re.sub(r'from \. import (\w+)', r'import \1', content)
        # Replace 'from .<module> import' with 'from <module> import'
        new_content = re.sub(r'from \.(\w+) import', r'from \1 import', new_content)

        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filename}")
