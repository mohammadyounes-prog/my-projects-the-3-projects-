# Automated Exam Generation Solution

## 1. Overview

This document outlines a solution to automate the process of generating questions using the `new-q-bank` project's AI capabilities and then automatically creating an exam in the `online-exam` project using these generated questions. This solution bridges the two systems, streamlining the creation of new electronic exams.

## 2. Problem Statement

The user needs a way to:
*   Generate questions using the AI-powered `new-q-bank` project.
*   Automatically transfer these generated questions into the `schooldemo12` database, which serves as the question bank for the `online-exam` project.
*   Automatically create a new exam in the `online-exam` project, populated with these newly generated questions, without manual intervention through the `online-exam` dashboard.

## 3. Solution Overview

The solution involves three main phases:

1.  **AI Question Generation:** Generate questions using the `new-q-bank` project's AI scripts and store them in its local `questions.db`.
2.  **Question Export and Import:** Modify the existing `export_to_tams.py` script to directly insert the generated questions from `new-q-bank`'s `questions.db` into the `schooldemo12` database's `bank` table.
3.  **Automated Exam Creation:** Develop a new script that interacts with the `online-exam` project's API (`api.exam.php`) to automatically create and populate an exam with the questions imported in Phase 2.

## 4. Detailed Steps and Implementation

### Phase 1: AI Question Generation (within `new-q-bank` project)

This phase leverages the existing capabilities of the `new-q-bank` project.

*   **Process:**
    *   The `new-q-bank` project contains Python scripts (e.g., `gemini_api.py`, `google_api.py`, `openai_api.py` in its `backend` directory) that interact with AI models to generate question content.
    *   These scripts would be executed (e.g., via a command-line interface or an internal trigger) with appropriate prompts or parameters to generate the desired questions.
    *   The generated questions, including their text, answer choices, correct answers, type, mark, duration, and any associated metadata (like filters), are stored in the `new-q-bank`'s local SQLite database, `questions.db`.
*   **Output:** New question records in `D:\QuestionRetrieval\new-q-bank\questions.db`.

### Phase 2: Export Questions to `schooldemo12` `bank` table

This phase involves modifying an existing script to facilitate direct database insertion.

*   **Tool:** The `D:\QuestionRetrieval\new-q-bank\scripts\export_to_tams.py` script.
*   **Current Functionality:** Currently, `export_to_tams.py` reads questions from `questions.db` and prints SQL `INSERT` statements to the console, formatted for the `TAMS` `bank` table.
*   **Required Modification:**
    *   **Goal:** Instead of printing SQL, the script needs to connect directly to the `schooldemo12` database and execute the `INSERT` statements.
    *   **Assumptions:** We assume `schooldemo12` is also a SQLite database. If it's a different database type (e.g., MySQL), the connection and `Query::set` calls would need to be adapted accordingly.
    *   **Modification Steps (Conceptual `export_to_tams.py` changes):

        ```python
        import sqlite3
        import json
        import os
        import datetime

        # Configuration for new-q-bank database
        NEW_Q_BANK_DB = os.path.join(os.path.dirname(__file__), '..', 'questions.db')

        # Configuration for schooldemo12 database (ASSUMPTION: SQLite)
        # You will need to confirm the exact path to your schooldemo12 database file.
        # For example, it might be in D:\QuestionRetrieval\new-q-bank\TAMS\app\schooldemo12\schooldemo12.db
        SCHOOLDEMO12_DB = 'D:\\QuestionRetrieval\\new-q-bank\\TAMS\\app\\schooldemo12\\schooldemo12.db' # <<< CONFIRM THIS PATH

        # Default values for TAMS bank table fields not directly mapped
        DEFAULT_TEACHER_ID = 1
        DEFAULT_COURSE_ID = 1
        DEFAULT_CATEGORY_SET = "1"
        DEFAULT_RESOURCES = "{}" # Empty JSON object
        DEFAULT_PARENT = "NULL" # No parent question

        def export_questions_to_schooldemo12():
            conn_q_bank = None
            conn_schooldemo12 = None
            try:
                conn_q_bank = sqlite3.connect(NEW_Q_BANK_DB)
                conn_q_bank.row_factory = sqlite3.Row
                cursor_q_bank = conn_q_bank.cursor()

                conn_schooldemo12 = sqlite3.connect(SCHOOLDEMO12_DB)
                cursor_schooldemo12 = conn_schooldemo12.cursor()

                cursor_q_bank.execute("SELECT * FROM questions")
                questions = cursor_q_bank.fetchall()

                inserted_question_ids = [] # To store IDs of questions inserted into schooldemo12 bank

                for q in questions:
                    # Map fields from new-q-bank to tams bank table
                    title = q['question_text']

                    choices = []
                    if q['choice_1']: choices.append(q['choice_1'])
                    if q['choice_2']: choices.append(q['choice_2'])
                    if q['choice_3']: choices.append(q['choice_3'])
                    if q['choice_4']: choices.append(q['choice_4'])
                    answers = json.dumps(choices)

                    question_type = "mch" # Default to multiple choice
                    correct_option_tams = "NULL"

                    if q['correct_option'] and choices:
                        normalized_correct_option = str(q['correct_option']).strip().upper()
                        if len(normalized_correct_option) == 1 and normalized_correct_option.isalpha() and 'A' <= normalized_correct_option <= chr(ord('A') + len(choices) - 1):
                            correct_index = ord(normalized_correct_option) - ord('A') + 1
                            correct_option_tams = str(correct_index)
                        else:
                            for i, choice in enumerate(choices):
                                if str(choice).strip().lower() == normalized_correct_option.lower():
                                    correct_option_tams = str(i + 1)
                                    break
                            if correct_option_tams == "NULL":
                                print(f"Warning: No direct match for correct option '{q['correct_option']}' in choices for question ID {q['question_id']}. Setting to NULL.")

                    mark = q['mark'] if q['mark'] is not None else 0.00
                    duration = q['time_seconds'] if q['time_seconds'] is not None else 0
                    
                    date_created = q['date_created']
                    if date_created:
                        try:
                            dt_object = datetime.datetime.fromisoformat(date_created)
                            date_created = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            date_object = datetime.datetime.now()
                            date_created = date_object.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        date_object = datetime.datetime.now()
                        date_created = date_object.strftime('%Y-%m-%d %H:%M:%S')

                    # Prepare data for insertion into schooldemo12 bank table
                    insert_data = (
                        title,
                        answers,
                        correct_option_tams,
                        DEFAULT_TEACHER_ID,
                        DEFAULT_COURSE_ID,
                        question_type,
                        DEFAULT_CATEGORY_SET,
                        mark,
                        duration,
                        date_created,
                        DEFAULT_RESOURCES,
                        DEFAULT_PARENT
                    )

                    # Execute INSERT statement
                    cursor_schooldemo12.execute(f"""
                        INSERT INTO `bank` (`title`, `answers`, `correct`, `teacherId`, `courseId`, `type`, `categorySet`, `mark`, `duration`, `date`, `resources`, `parent`)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, insert_data)
                    
                    inserted_question_ids.append(cursor_schooldemo12.lastrowid) # Get the ID of the newly inserted question

                conn_schooldemo12.commit()
                print(f"Successfully inserted {len(inserted_question_ids)} questions into schooldemo12 bank table.")
                return inserted_question_ids

            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return []
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return []
            finally:
                if conn_q_bank:
                    conn_q_bank.close()
                if conn_schooldemo12:
                    conn_schooldemo12.close()

        if __name__ == "__main__":
            export_questions_to_schooldemo12()
        ```
*   **Output:** Questions from `new-q-bank`'s `questions.db` are directly inserted into the `bank` table of the `schooldemo12` database. The `export_questions_to_schooldemo12` function will return a list of the `bankId`s of the newly inserted questions.

### Phase 3: Automated Exam Creation (using `online-exam` API)

This phase requires creating a new script to interact with the `online-exam` project's API.

*   **Tool:** A new Python script (e.g., `create_automated_exam.py`).
*   **Process:**
    1.  **Get Question IDs:** The script will receive the list of `bankId`s of the newly inserted questions from Phase 2.
    2.  **Define Exam Metadata:** Define the desired properties for the new exam (e.g., name, date, duration, total marks, settings).
    3.  **Construct API Request Payload:** Create a JSON payload that matches the expected structure for the `API::POST` endpoint in `api.exam.php`. This payload will include:
        *   `name`, `status` (e.g., "draft" or "published"), `date`, `duration`, `totalQ`, `mark`, `settings` (as a JSON string), `courseId`, `teacherLinkId`, etc.
        *   A `questions` array, where each element represents a question in the exam. For questions already in the `bank` table, you would primarily need to provide their `bankId`. Other fields like `mark`, `duration`, `type`, `title`, `answers`, `correct` can be included if you want to override the bank's values or if the `online-exam` API expects them even for `bankId`-linked questions.
            ```json
            {
                "name": "AI Generated Exam - [Date]",
                "status": "draft", // or "published"
                "date": "YYYY-MM-DD HH:MM:SS",
                "duration": 60,
                "totalQ": 10, // Count of questions
                "mark": 100, // Sum of question marks
                "courseId": 1,
                "teacherLinkId": "1",
                "settings": "{\"random\":true, \"view\":\"scroll\"}", // Example settings
                "questions": [
                    { "bankId": 101, "mark": 10, "duration": 5 },
                    { "bankId": 102, "mark": 10, "duration": 5 },
                    // ... more questions
                ]
            }
            ```
    4.  **Make API Call:** Send an HTTP `POST` request to the `online-exam` API endpoint (e.g., `http://your-online-exam-url/api/exam`).
    5.  **Handle Response:** Process the API response to confirm exam creation and handle any errors.
*   **Example Python Script (`create_automated_exam.py` - Conceptual):

    ```python
    import requests
    import json
    import datetime

    # --- Configuration ---
    ONLINE_EXAM_API_URL = "http://localhost/tams/app/schooldemo12/apps/online-exam/api/exam" # <<< CONFIRM THIS URL
    # Assuming the schooldemo12 database is local for export_questions_to_schooldemo12
    # and this script will receive the question_ids from that process.

    # --- Exam Details ---
    EXAM_NAME_PREFIX = "AI Generated Exam"
    DEFAULT_DURATION = 60 # minutes
    DEFAULT_COURSE_ID = 1
    DEFAULT_TEACHER_LINK_ID = "1" # Comma-separated string if multiple
    DEFAULT_SETTINGS = {"random": True, "view": "scroll"} # Example settings

    def create_exam_automatically(question_ids: list, exam_details: dict = None):
        if not question_ids:
            print("No questions provided to create an exam.")
            return None

        # Fetch question details from schooldemo12 bank table to get marks/durations
        # This would require another DB connection or an API call to api.bank.php
        # For simplicity, let's assume default marks/durations or pass them in exam_details
        
        questions_payload = []
        total_mark = 0
        total_duration = 0
        for q_id in question_ids:
            # In a real scenario, you'd fetch mark/duration from the DB for q_id
            # For this example, we'll use placeholders or assume they are passed.
            q_mark = exam_details.get('default_question_mark', 10)
            q_duration = exam_details.get('default_question_duration', 5)
            questions_payload.append({
                "bankId": q_id,
                "mark": q_mark,
                "duration": q_duration
            })
            total_mark += q_mark
            total_duration += q_duration

        # Default exam details if not provided
        if exam_details is None:
            exam_details = {}

        exam_name = exam_details.get("name", f"{EXAM_NAME_PREFIX} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        exam_date = exam_details.get("date", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        exam_duration = exam_details.get("duration", DEFAULT_DURATION)
        exam_total_q = len(question_ids)
        exam_mark = exam_details.get("mark", total_mark)
        exam_status = exam_details.get("status", "draft") # "draft" or "published"
        exam_course_id = exam_details.get("courseId", DEFAULT_COURSE_ID)
        exam_teacher_link_id = exam_details.get("teacherLinkId", DEFAULT_TEACHER_LINK_ID)
        exam_settings = exam_details.get("settings", DEFAULT_SETTINGS)

        payload = {
            "name": exam_name,
            "status": exam_status,
            "date": exam_date,
            "duration": exam_duration,
            "totalQ": exam_total_q,
            "mark": exam_mark,
            "courseId": exam_course_id,
            "teacherLinkId": exam_teacher_link_id,
            "settings": json.dumps(exam_settings),
            "questions": questions_payload
        }

        headers = {
            'Content-Type': 'application/json'
            # Add any necessary authentication headers here (e.g., API key, session token)
            # This is a critical part that needs to be implemented based on online-exam's auth
        }

        try:
            response = requests.post(ONLINE_EXAM_API_URL, data=json.dumps(payload), headers=headers)
            response.raise_for_status() # Raise an exception for HTTP errors

            result = response.json()
            if result.get("status") == "success" or result.get("status") == True: # Adjust based on actual API response
                print(f"Exam '{exam_name}' created successfully. Response: {result}")
                return result
            else:
                print(f"Failed to create exam '{exam_name}'. Response: {result}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None

    if __name__ == "__main__":
        # --- Example Usage ---
        # In a real scenario, question_ids would come from the modified export_to_tams.py script
        # For demonstration, let's use some dummy IDs
        dummy_question_ids = [1, 2, 3, 4, 5] # These would be the bankIds from schooldemo12

        # Example exam details (can be customized)
        my_exam_details = {
            "name": "My First AI Exam",
            "status": "published", # Publish directly or keep as "draft"
            "date": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "duration": 90,
            "mark": 150,
            "courseId": 2,
            "teacherLinkId": "2",
            "settings": {"random": True, "view": "page", "models": 1}
        }

        created_exam = create_exam_automatically(dummy_question_ids, my_exam_details)
        if created_exam:
            print(f"Automated exam creation process finished. Exam ID: {created_exam.get('id')}")
        else:
            print("Automated exam creation failed.")
    ```

## 5. Prerequisites and Assumptions

*   **Database Access:** The `export_to_tams.py` script must have direct write access to the `schooldemo12` database file.
*   **`schooldemo12` Database Path:** The exact absolute path to the `schooldemo12` database file must be correctly configured in `export_to_tams.py`.
*   **`online-exam` API URL:** The correct base URL for the `online-exam` API must be configured in the `create_automated_exam.py` script.
*   **Authentication:** The `create_automated_exam.py` script will need to handle authentication with the `online-exam` API. This typically involves sending an API key, session token, or other credentials in the request headers. The example script includes a placeholder for this.
*   **Question Details:** When creating the exam payload, the `create_automated_exam.py` script needs to know the `mark` and `duration` for each question. These can either be fetched from the `schooldemo12` `bank` table after insertion or passed along from the `new-q-bank` generation process.
*   **PHP Environment:** The `online-exam` project must be running in a PHP environment (e.g., Apache, Nginx with PHP-FPM) for its API endpoints to be accessible via HTTP requests.

## 6. Future Considerations and Improvements

*   **Error Handling:** Implement more robust error handling and logging in both Python scripts.
*   **Configuration Management:** Externalize database paths, API URLs, and default exam settings into a configuration file (e.g., `.ini`, `.json`, `.env`) for easier management.
*   **Authentication Mechanism:** Implement a proper authentication mechanism for the `create_automated_exam.py` script to securely interact with the `online-exam` API.
*   **Question Filtering/Selection:** Enhance the `create_automated_exam.py` script to intelligently select questions from the `schooldemo12` `bank` based on criteria (e.g., difficulty, topic, number of questions per type) rather than just taking all newly inserted questions. This could involve querying `online-exam`'s `api.bank.php`'s `random` endpoint.
*   **Idempotency:** Consider how to handle re-running the process to avoid duplicate questions or exams.
*   **User Interface:** Potentially create a simple UI or CLI tool to trigger this automated workflow.
*   **Database Abstraction:** If `schooldemo12` is not SQLite, use a proper database connector for Python (e.g., `pymysql` for MySQL) and adjust SQL syntax.
*   **Transaction Management:** Ensure that the database operations in `export_to_tams.py` are wrapped in transactions for atomicity.

This detailed documentation provides a clear roadmap for implementing the automated exam generation solution.
