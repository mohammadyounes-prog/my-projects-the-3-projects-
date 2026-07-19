import requests
import argparse

def login_user(username, password, tenant_id):
    url = "http://127.0.0.1:8000/token"
    data = {"username": username, "password": password, "tenant_id": tenant_id}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(response.json()["access_token"])
    else:
        print(response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Login a user.')
    parser.add_argument('username', type=str, help='The username.')
    parser.add_argument('password', type=str, help='The password.')
    parser.add_argument('tenant_id', type=int, help='The tenant ID.')
    args = parser.parse_args()
    login_user(args.username, args.password, args.tenant_id)
