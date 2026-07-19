import os
import re

file_path = r"E:\questionretrieval
ew-q-bank\backend\gemini_api.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- Apply fixes ---

    # Fix 1: Modify generate_solution_with_gemini to include generation_config and system_instruction
    # and remove 'models/' prefix from models_to_try
    old_solution_func = """def generate_solution_with_gemini(question_text: str, question_type: str, difficulty_level: str,
                                  cognitive_level: str, learning_outcome: str, api_key: str,
                                  model: str = 'gemini-1.5-flash-latest'):
    if not api_key:
        return {"error": "Gemini API key not configured"}

    genai.configure(api_key=api_key)

    model_name_to_use = model or 'gemini-1.5-flash-latest'
    models_to_try = ['models/gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'models/gemini-pro']
    
    last_error = None
    for model_name in models_to_try:
        try:
            model_instance = genai.GenerativeModel(model_name)"""

    new_solution_func = """def generate_solution_with_gemini(question_text: str, question_type: str, difficulty_level: str,
                                  cognitive_level: str, learning_outcome: str, api_key: str,
                                  model: str = 'gemini-1.5-flash-latest'):
    if not api_key:
        return {"error": "Gemini API key not configured"}

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

    system_instruction = "You are an expert tutor providing clear, step-by-step solutions to educational questions. Focus on logical progression and understanding."

    models_to_try = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro'] # Use un-prefixed names here as genai.GenerativeModel will handle it.
    
    last_error = None
    for model_name in models_to_try:
        try:
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_instruction
            )"""
    
    if old_solution_func in content and new_solution_func not in content:
        content = content.replace(old_solution_func, new_solution_func)
        print("Applied fix 1: Updated generate_solution_with_gemini function.")
    else:
        print("Fix 1 (generate_solution_with_gemini) already applied or old content not found.")


    # Fix 2: Ensure os.getenv is used for GOOGLE_API_KEY in list_available_gemini_models()
    old_list_models_key = """def list_available_gemini_models():
    """
    Lists available Gemini models and their supported methods.
    """
    if not GOOGLE_API_KEY:"""
    new_list_models_key = """def list_available_gemini_models():
    """
    Lists available Gemini models and their supported methods.
    """
    if not os.getenv("GOOGLE_API_KEY"):"""

    if old_list_models_key in content and new_list_models_key not in content:
        content = content.replace(old_list_models_key, new_list_models_key)
        print("Applied fix 2: Updated GOOGLE_API_KEY usage in list_available_gemini_models.")
    else:
        print("Fix 2 (list_available_gemini_models GOOGLE_API_KEY) already applied or old content not found.")

    # Fix 3: Remove duplicate code at the end of the file (if it exists)
    # This is a bit tricky, relying on regex to find the duplicate block after the first __main__
    # The duplicate starts with a mis-indented line.
    duplicate_pattern = re.compile(r"(
# Example usage \(for testing purposes\)
if __name__ == "__main__":
    list_available_gemini_models\(\)
).*
 not configured; skipping model list\."")
    
    # Try to find the second occurrence of the pattern to replace only that part
    match = list(re.finditer(r"(
# Example usage \(for testing purposes\)
if __name__ == "__main__":
    list_available_gemini_models\(\))", content))
    
    if len(match) > 1:
        # If there's more than one, we want to remove from the start of the second match to the end of the file
        start_of_duplicate = match[1].start()
        content = content[:start_of_duplicate]
        # Add back the correct main block from the first match
        content += match[0].group(1)
        print("Applied fix 3: Removed duplicate code block at the end of the file.")
    else:
        print("Fix 3 (duplicate code removal) not needed or duplicate not found.")


    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully updated {file_path}")

except Exception as e:
    print(f"An error occurred: {e}")
