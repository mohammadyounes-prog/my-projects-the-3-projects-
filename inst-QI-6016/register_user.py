import requests
import argparse

def register_user(username, password, tenant_id, email, country):
    url = "http://127.0.0.1:8300/register"
    headers = {"Content-Type": "application/json"}
    data = {"username": username, "password": password, "tenant_id": tenant_id, "email": email, "country": country}
    response = requests.post(url, headers=headers, json=data)
    try:
        print(response.json())
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response. Status Code: {response.status_code}, Response Text: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Register a new user.')
    parser.add_argument('username', type=str, help='The username.')
    parser.add_argument('password', type=str, help='The password.')
    parser.add_argument('tenant_id', type=int, help='The tenant ID.')
    parser.add_argument('email', type=str, help='The user\'s email address.') # New argument
    parser.add_argument('country', type=str, help='The user\'s country.') # New argument
    args = parser.parse_args()
    register_user(args.username, args.password, args.tenant_id, args.email, args.country) # Modified call
