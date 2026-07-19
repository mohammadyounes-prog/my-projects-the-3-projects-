import os
import shutil
import sys

def delete_pycache(path):
    for root, dirs, files in os.walk(path):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"Deleting: {pycache_path}")
            try:
                shutil.rmtree(pycache_path)
            except OSError as e:
                print(f"Error deleting {pycache_path}: {e}")

if __name__ == "__main__":
    project_root = r"E:\questionretrieval
ew-q-bank"
    backend_path = os.path.join(project_root, "backend")
    newboard_backend_path = os.path.join(project_root, "newboard", "backend")

    print("Attempting to delete __pycache__ in backend directories...")
    delete_pycache(backend_path)
    delete_pycache(newboard_backend_path)
    print("Finished __pycache__ deletion script.")
