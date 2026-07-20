import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

print("Attempting to generate content...")
try:
    response = model.generate_content("Hello, can you hear me?")
    print("Response:", response.text)
except Exception as e:
    print("Error:", str(e))
