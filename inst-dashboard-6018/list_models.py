
# This script needs to load the environment to get the API key
# and then call the function from gemini_api.
import os

# This will also trigger the print statement in config
# We need to make sure the backend package is in the python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import GOOGLE_API_KEY 
from backend.gemini_api import list_available_gemini_models

print("--- Attempting to list available Gemini models for the configured API key ---")
if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY is not set. Cannot list models.")
else:
    # The function itself prints the output
    list_available_gemini_models()
print("--- End of model list ---")

