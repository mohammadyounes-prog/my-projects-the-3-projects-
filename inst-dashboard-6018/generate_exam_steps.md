# Steps to Generate a New Exam in the Online Exam Dashboard

Based on the analysis of `api.exam.php` and `api.bank.php`, generating a new exam typically involves the following steps within the online exam dashboard's user interface:

1.  **Navigate to the Exam Creation Section:**
    *   From the main dashboard, go to the "Electronic Exams" tab.
    *   Within the "Electronic Exams" tab, locate and click on the "Exams" sub-tab.
    *   Look for a button or link labeled "Generate New Exam," "Add New Exam," or similar, and click it to open the exam creation form.

2.  **Provide Basic Exam Information:**
    *   Fill in essential details for the new exam in the provided form fields:
        *   **Exam Name:** A descriptive title for the exam.
        *   **Date and Time:** The scheduled date and time for the exam.
        *   **Duration:** The total time allowed for the exam (in minutes).
        *   **Total Questions (totalQ):** The total number of questions that will be in the exam.
        *   **Total Mark (mark):** The maximum possible score for the exam.
        *   **Associated Course (courseId):** Select the relevant course from a dropdown or similar selector.
        *   **Associated Teacher Link (teacherLinkId):** Link the exam to a specific teacher or teacher-course association.
        *   **Access:** Define who can access the exam (e.g., public, private, specific groups).
        *   **Success Mark:** The minimum score required to pass the exam.

3.  **Configure Exam Settings:**
    *   Adjust various settings that control the exam's behavior and presentation. These are often presented as checkboxes, radio buttons, or dropdowns and correspond to the `settings` JSON field:
        *   **Question View:** How questions are displayed (e.g., one question per page, all questions on one page, scrollable).
        *   **Show Marks:** Whether students can see their marks during or after the exam.
        *   **Random Question Order:** Enable or disable randomization of question order for each student.
        *   **Number of Question Models:** If the system supports different versions or sets of questions for an exam, specify the number of models.
        *   **Has Sessions:** If the exam is part of a larger session group.
        *   **Require Reservations:** If students need to reserve a spot for the exam.

4.  **Add Questions to the Exam:**
    *   This is where the actual exam content is assembled. There are typically a few ways to add questions:
        *   **Manually Select from Question Bank:** Browse the central question bank (which is populated via `api.bank.php`, `importQB.php`, or `importQuestionsDirect.php`) and select individual questions to include in the exam.
        *   **Generate Random Questions:** Use a feature to automatically select questions based on predefined criteria. You might specify:
            *   **Category:** Select questions from specific categories.
            *   **Difficulty Level:** Choose questions of a certain difficulty.
            *   **Number of Questions:** Specify how many questions to randomly select.
            *   This process likely utilizes the `API::post("random", ...)` endpoint from `api.bank.php`.
        *   **Create New Questions:** If the interface allows, you can directly create new questions within the exam form. These questions will initially be associated only with this exam.

5.  **Review and Validate Questions:**
    *   Before finalizing, review all added questions to ensure their accuracy, completeness, and proper configuration (title, answers, correct option, mark, duration, type).
    *   The system will perform internal validation checks, especially during the publishing phase, to ensure consistency (e.g., total marks of questions match the exam's total mark, all questions have valid answers).

6.  **Save the Exam (Draft):**
    *   Initially, save the exam as a "Draft" status. This allows you to continue working on it later without it being accessible to students.

7.  **Publish the Exam:**
    *   Once the exam is complete and thoroughly reviewed, change its status to "Published" (or "parent-published", "part-published", "part").
    *   **Crucial Step:** Publishing triggers a series of backend processes (handled by `api.exam.php`):
        *   **Final Validation:** A comprehensive check for all required data and consistency.
        *   **Question Bank Integration:** Any new questions that were created directly within this exam (i.e., not pulled from the existing question bank) will be formally added to the central `bank` table. Their `bankId` in the `examdata` table will be updated to reflect this.
        *   **Logging:** The publishing action is logged.
    *   If any validation errors occur, the system will prevent publishing and provide feedback.

Following these steps will allow you to successfully generate and publish a new electronic exam within the system.