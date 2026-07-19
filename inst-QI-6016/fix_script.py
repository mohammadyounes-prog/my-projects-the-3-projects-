import re
import os
from pathlib import Path

def fix_main_py(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove all existing CORS configurations
    content = re.sub(r'origins=\[\".*?\"\]\n\nprint\(f\"DEBUG: CORS middleware initialized with origins: {origins}\\"\)\napp.add_middleware\(\n  CORSMiddleware,\n  allow_origins=origins,\n  allow_credentials=True,\n  allow_methods=\[\"GET\", \"POST\", \"PUT\", \"PATCH\", \"DELETE\", \"OPTIONS\"\]\n  allow_headers=\[\"Authorization\", \"Content-Type\", \"X-Requested-With\"\]\n  \)', '', content, flags=re.DOTALL)
    content = re.sub(r'origins=\[\".*?\"\]\n\nprint\(f\"DEBUG: CORS middleware initialized with origins: {origins}\\"\)\napp.add_middleware\(\n  CORSMiddleware,\n  allow_credentials=True,\n  allow_methods=\[\"GET\", \"POST\", \"PUT\", \"PATCH\", \"DELETE\", \"OPTIONS\"\]\n  allow_headers=\[\"Authorization\", \"Content-Type\", \"X-Requested-With\"\]\n  allow_origins=origins,\n  \)', '', content, flags=re.DOTALL)

    # Add the correct CORS configuration once
    cors_config = '''\norigins=[\"*\"]\n\nprint(f\"DEBUG: CORS middleware initialized with origins: {origins}\")\napp.add_middleware(\n  CORSMiddleware,\n  allow_origins=origins,\n  allow_credentials=True,\n  allow_methods=[\"GET\", \"POST\", \"PUT\", \"PATCH\", \"DELETE\", \"OPTIONS\"],\n  allow_headers=[\"Authorization\", \"Content-Type\", \"X-Requested-With\"],\n  )\n'''
    # Find the line where app = FastAPI() is defined and insert CORS after it
    content = re.sub(r"(app = FastAPI\(\) # Moved this line to here)", r"\\1" + cors_config, content, flags=re.DOTALL)

    with open(file_path, 'w') as f:
        f.write(content)

def fix_admin_py(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Fix billing_events.created_at to billing_events.timestamp in SELECT
    content = re.sub(r"billing_events.created_at as timestamp,", "billing_events.timestamp as timestamp,", content)
    # Fix billing_events.created_at to billing_events.timestamp in ORDER BY
    content = re.sub(r"ORDER BY billing_events.created_at DESC", "ORDER BY billing_events.timestamp DESC", content)
    # Fix billing_events.created_at to billing_events.timestamp in date filters
    content = re.sub(r"date\\(billing_events.created_at\\) >= date\\(\\?\\)", "date(billing_events.timestamp) >= date(?)", content)
    content = re.sub(r"date\\(billing_events.created_at\\) <= date\\(\\?\\)", "date(billing_events.timestamp) <= date(?)", content)
    # Fix billing_events.currency_code to bp.currency_code
    content = re.sub(r"billing_events.currency_code", "bp.currency_code as currency_code", content)

    with open(file_path, 'w') as f:
        f.write(content)

# Define file paths
main_py_path = r"D:\\QuestionRetrieval\\new-q-bank\\backend\\main.py"
admin_py_path = r"D:\\QuestionRetrieval\\new-q-bank\\backend\\admin.py"

# Apply fixes
fix_main_py(main_py_path)
fix_admin_py(admin_py_path)

print("Files updated successfully.")