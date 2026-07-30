import requests

def get_questions(token):
    url = "http://127.0.0.1:8000/questions"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(response.json())

if __name__ == "__main__":
    with open('token.txt', 'r') as f:
        token = f.read().strip()
    get_questions(token)
