import google.generativeai as genai
import logging
import time
import os
import traceback
from typing import Optional, List

# Configure Gemini only if a non-empty key is provided
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Cache for Gemini model instances
_gemini_models = {}


def generate_questions_with_gemini(
    topic_context: str,
    question_type: str,
    difficulty_level: str,
    cognitive_level: str,
    learning_outcome: str,
    num_questions: int,
    api_key: str,
    num_choices: int = 4,
    incorrect_choice_strategy: str = "Plausible distractors",
    model: str = 'gemini-1.5-flash',
    lang: str = None,
    subject: Optional[str] = None,
    country: Optional[str] = None,
    audience_type: Optional[str] = None,
    school_type: Optional[str] = None,
    year: Optional[str] = None,
    major: Optional[str] = None,
    course: Optional[str] = None,
    material: Optional[str] = None,
    semester: Optional[str] = None,
    company: Optional[str] = None,
    department: Optional[str] = None,
    job_role: Optional[str] = None
):
    """
    Generates a batch of questions using the Gemini API with JSON mode for speed and accuracy.
    """

    if not api_key:
        return {"error": "Gemini API key not configured"}

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    system_instruction = (
        r"You are an expert question generator. Your task is to create high-quality, "
        r"educational questions based on the provided context. You MUST output the "
        r"results in a valid JSON array format. IMPORTANT: Ensure all backslashes (\\) "
        r"in LaTeX expressions are properly escaped for JSON. Always format mathematical "
        r"expressions using LaTeX, enclosed in \\( and \\). For example, x squared "
        r"should be written as \\(x^2\\). Ensure the JSON is structurally sound and "
        r"all strings are properly terminated and escaped."
    )

    if lang:
        system_instruction += f" You must respond in {lang.capitalize()}."

    model_name_to_use = model or 'gemini-1.5-flash'

    model_instance = genai.GenerativeModel(
        model_name=model_name_to_use,
        generation_config=generation_config,
        system_instruction=system_instruction
    )

    prompt = f"""Create {num_questions} {question_type} questions.

Subject: {subject if subject else 'Not specified'}
Country: {country if country else 'Not specified'}
Audience Type: {audience_type if audience_type else 'Not specified'}
Context: {topic_context[:15000]}

Difficulty: {difficulty_level}
Cognitive Level: {cognitive_level}
Learning Outcome: {learning_outcome}

Additional Specifics:
School Type: {school_type if school_type else 'N/A'}
Year: {year if year else 'N/A'}
Major: {major if major else 'N/A'}
Course: {course if course else 'N/A'}
Material: {material if material else 'N/A'}
Semester: {semester if semester else 'N/A'}
Company: {company if company else 'N/A'}
Department: {department if department else 'N/A'}
Job Role: {job_role if job_role else 'N/A'}

Return a VALID JSON array of objects with these keys:

- question_text:
    * The text of the question.
    * For 'text' (fill-in-the-blank), include a blank space like "_______".

- choices:
    * For 'multiple choice': An array of 4 strings.
    * For 'yes_no': ["Yes", "No"] or Arabic equivalent.
    * For 'accept_reject': ["Accept", "Reject"] or Arabic equivalent.
    * For 'multiple_answer': An array of 4 strings.
    * For 'text': Use an empty array [].

- correct_option:
    * For 'multiple choice': A, B, C, or D.
    * For 'yes_no': A or B.
    * For 'accept_reject': A or B.
    * For 'multiple_answer': Exactly two letters, e.g. "AB".
    * For 'text': The actual answer text.

- solution: A step-by-step explanation.
- question_type: The type of question generated.
"""

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text

        except Exception as e:
            err_str = str(e)

            if "429" in err_str or "quota" in err_str.lower():
                if attempt < max_retries - 1:
                    logging.warning(
                        f"Gemini Rate Limit (429) hit. Retrying in {retry_delay}s... "
                        f"(Attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(retry_delay)
                    continue

            logging.error(f"Gemini API Error: {e}")
            logging.error(traceback.format_exc())
            return {"error": err_str}


def generate_solution_with_gemini(
    question_text: str,
    question_type: str,
    difficulty_level: str,
    cognitive_level: str,
    learning_outcome: str,
    api_key: str,
    model: str = 'gemini-1.5-flash-latest'
):
    if not api_key:
        return {"error": "Gemini API key not configured"}

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

    system_instruction = (
        "You are an expert tutor providing clear, step-by-step solutions "
        "to educational questions. Focus on logical progression and understanding."
    )

    models_to_try = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-pro'
    ]

    last_error = None

    for model_name in models_to_try:
        try:
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction
            )

            prompt = f"""You are an expert tutor. Provide a step-by-step solution for the following question:

Question: {question_text}

Question Type: {question_type}
Difficulty Level: {difficulty_level}
Cognitive Level: {cognitive_level}
Learning Outcome: {learning_outcome}

Please provide a clear, step-by-step explanation that helps a student understand how to arrive at the correct answer.
"""

            response = model_instance.generate_content(prompt)
            return response.text

        except Exception as e:
            last_error = str(e)
            print(f"--- GEMINI API WARNING (Model {model_name} failed) ---")
            print(last_error)
            continue

    return {
        "error": f"Failed to generate solution with all attempted models. Last error: {last_error}"
    }


def list_available_gemini_models():
    """
    Lists available Gemini models and their supported methods.
    """

    if not os.getenv("GOOGLE_API_KEY"):
        print("Gemini API key not configured; skipping model list.")
        return

    print("\\n--- Available Gemini Models ---")

    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"Name: {m.name}, Supported methods: {m.supported_generation_methods}")


if __name__ == "__main__":
    list_available_gemini_models()
