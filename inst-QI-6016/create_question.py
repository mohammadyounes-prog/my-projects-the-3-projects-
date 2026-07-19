import requests
import argparse

def create_question(token, question_text):
    url = "http://127.0.0.1:8000/generate_questions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "topic_context": question_text,
        "question_type": "multiple choice",
        "difficulty_level": "Easy",
        "country": "USA",
        "audience_type": "school",
        "num_questions": 1,
        "generation_method": "dummy"
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a new question.')
    parser.add_argument('question_text', type=str, help='The text of the question.')
    args = parser.parse_args()
    with open('token.txt', 'r') as f:
        token = f.read().strip()
    create_question(token, args.question_text)
