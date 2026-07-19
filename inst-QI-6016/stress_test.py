
import requests
import json
import time

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "superadmin"

NUM_AGENTS = 10
NUM_USERS_PER_AGENT = 50
NUM_QUESTIONS_PER_USER = 100

# --- Helper Functions ---

def get_auth_token(username, password):
    """Logs in a user and returns the auth token."""
    try:
        response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting auth token: {e}")
        return None

def create_agent(token, agent_name, country):
    """Creates a new agent (tenant)."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"name": agent_name, "country": country}
        response = requests.post(f"{BASE_URL}/admin/tenants", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating agent {agent_name}: {e}")
        return None

def create_user(token, username, password, full_name, tenant_id, country):
    """Creates a new user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "username": username,
            "password": password,
            "full_name": full_name,
            "country": country,
            "is_admin": False
        }
        response = requests.post(f"{BASE_URL}/admin/users", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Error creating user {username}: {e.response.status_code} {e.response.reason} - {e.response.json().get('detail', 'No detail provided')}")
        else:
            print(f"Error creating user {username}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating user {username}: {e}")
        return None

def generate_questions(token, user_id, num_questions):
    """Generates questions for a user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "topic_context": "This is a stress test.",
            "question_type": "multiple_choice",
            "difficulty_level": "Easy",
            "country": "United States",
            "audience_type": "general",
            "num_questions": num_questions,
            "model_api_name": "dummy"
        }
        response = requests.post(f"{BASE_URL}/generate", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error generating questions for user {user_id}: {e}")
        return None

def retrieve_questions(token, user_id):
    """Retrieves questions for a user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/questions?user_id={user_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving questions for user {user_id}: {e}")
        return None

def cleanup_test_data(token):
    """Deletes all test users and tenants created by the stress test."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete users
    try:
        users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        users_response.raise_for_status()
        users = users_response.json()
        for user in users:
            if user["username"].startswith("stress_"):
                print(f"  Deleting user: {user["username"]}")
                requests.delete(f"{BASE_URL}/admin/users/{user["id"]}", headers=headers).raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during user cleanup: {e}")

    # Delete tenants
    try:
        tenants_response = requests.get(f"{BASE_URL}/admin/tenants", headers=headers)
        tenants_response.raise_for_status()
        tenants = tenants_response.json()
        for tenant in tenants:
            if tenant["name"].startswith("stress_"):
                print(f"  Deleting tenant: {tenant["name"]}")
                requests.delete(f"{BASE_URL}/admin/tenants/{tenant["id"]}", headers=headers).raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during tenant cleanup: {e}")

# --- Main Script ---

def main():
    start_time = time.time()

    print("--- Stress Test Starting ---")

    # 1. Get superadmin auth token
    print("Logging in as superadmin...")
    superadmin_token = get_auth_token(SUPERADMIN_USERNAME, SUPERADMIN_PASSWORD)
    if not superadmin_token:
        print("Could not get superadmin token. Aborting.")
        return

    # 2. Clean up previous test data
    print("Cleaning up previous test data...")
    cleanup_test_data(superadmin_token)

    # 3. Create agents
    print(f"Creating {NUM_AGENTS} agents...")
    timestamp = int(time.time())
    for i in range(NUM_AGENTS):
        agent_name = f"stress_agent_{timestamp}_{i}"
        print(f"  Attempting to create agent: {agent_name}") # NEW DEBUG PRINT
        country = "United States"  # Using a default country for simplicity
        agent = create_agent(superadmin_token, agent_name, country)
        if not agent:
            continue
        time.sleep(0.1) # Small delay to prevent database locking

        agent_id = agent["id"]
        print(f"  Created agent: {agent_name} (ID: {agent_id})")

        # 3. Create users for each agent
        print(f"  Creating {NUM_USERS_PER_AGENT} users for agent {agent_name}...")
        for j in range(NUM_USERS_PER_AGENT):
            username = f"stress_user_{i}_{j}"
            password = "password"
            full_name = f"Stress User {i}-{j}"
            user = create_user(superadmin_token, username, password, full_name, agent_id, country)
            if not user:
                continue
            time.sleep(0.05) # Small delay to prevent database locking

            user_id = user["id"]
            print(f"    Created user: {username} (ID: {user_id})")

            # 4. Generate questions for each user
            print(f"    Generating {NUM_QUESTIONS_PER_USER} questions for user {username}...")
            # For the stress test, we'll log in as the user to generate questions
            user_token = get_auth_token(username, password)
            if not user_token:
                print(f"    Could not get token for user {username}. Skipping question generation.")
                continue
            
            generate_questions(user_token, user_id, NUM_QUESTIONS_PER_USER)

            # 5. Retrieve questions for each user
            print(f"    Retrieving questions for user {username}...")
            retrieve_questions(user_token, user_id)

    end_time = time.time()
    print(f"--- Stress Test Finished in {end_time - start_time:.2f} seconds ---")

if __name__ == "__main__":
    main()
