import requests

url = "http://localhost:8300/dashboard/online-exam/generate-advice"
data = {"test": "data"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
