# Brainstorming Session Results

## Executive Summary

*   **Session Topic:** An application to source, categorize, and export school and university exam questions.
*   **Initial Goal:** Focused ideation on the app concept.
*   **Technique Used:** Mind Mapping.
*   **Total Ideas Generated:** The session resulted in a fully-fledged MVP (Minimum Viable Product) concept.
*   **Key Themes & Patterns:** The most significant outcome was the strategic pivot from a complex, retrieval-based system to a more feasible AI generation model for the MVP. This decision was driven by clarifying the role of a human reviewer, which de-risked the initial development effort.

---

## Technique Sections

### Mind Mapping

*   **Technique Description:** We used Mind Mapping to visually structure the application's components, starting with a central topic and branching out to explore relationships and hierarchies.
*   **Ideas & Insights:**
    1.  **Initial Structure:** The session began by mapping out the core data structure: `School Year`, `Speciality`, and `Course`.
    2.  **Hierarchical Insight:** The user introduced the concept of `Country / Region` as a top-level category, realizing that educational systems are geographically dependent. This fundamentally reframed the information architecture.
    3.  **Final Hierarchy:** The agreed-upon content hierarchy is: `Country/Region` → `School/University Level` → `Speciality` → `Course` → `Unit/Section`.
    4.  **Core Purpose Pivot:** The user clarified that the app's primary purpose was to *collect, categorize, and export* questions, not for students to answer them. A critical insight was the introduction of a **Human Reviewer** role.
    5.  **Sourcing Method Pivot:** We initially explored a complex "AI-Powered Retrieval" method. However, the user made the strategic decision to pivot to a simpler **"AI Generation"** model for the MVP, designating retrieval as a future feature.
*   **Final Data Model:** We concluded by defining a clear separation between the user's request and the AI's output:
    *   **User Inputs (The Request):** Country, Level, Speciality, Course, Unit/Section, Question Type (MCQ/Yes-No), Number of Questions.
    *   **AI Outputs (The Generated Properties):** Question Text, Answer Options, Correct Answer, Learning Outcome, Cognitive Level, Difficulty Score, Discrimination Factor.

---

## Idea Categorization

*   **Immediate Opportunities (MVP):**
    *   Build the app based on the **"Define, Generate, Review, Export"** workflow using AI question generation. This is the core, achievable MVP.
*   **Future Innovations (Post-MVP):**
    *   Implement the **"AI-Powered Retrieval"** feature to find and extract real-world questions from reputable online sources.
    *   Develop the "Human-in-the-Loop" system for approving sources to train the retrieval AI over time.
*   **Moonshots (Ambitious Future Concepts):**
    *   Develop an "AI Vision" system that can visually parse screenshots or complex PDFs of exams to extract questions automatically.

---

## Action Planning

*   **Top Priority Idea:**
    1.  **Develop the MVP:** Focus exclusively on the AI Generation workflow.
*   **Next Steps:**
    1.  **Design the UI/UX:** Create the user interface for the "Define Request" form, ensuring all input fields are clear and easy to use.
    2.  **Select an AI Model:** Research and choose a suitable AI generation model/API that can fulfill the detailed requests.
    3.  **Develop the Reviewer Interface:** Design the screen where the human reviewer can efficiently approve, edit, or reject the AI-generated questions.
*   **Resources/Research Needed:**
    *   Comparison of different Large Language Model (LLM) APIs for cost, quality, and ease of integration.

---

## Reflection & Follow-up

*   **What Worked Well:** The session was highly effective due to the willingness to pivot. The clarification of the "human reviewer" role was a key moment that unlocked the simplified MVP path. The Mind Mapping technique proved useful in adapting the app's structure as new insights emerged.
*   **Areas for Further Exploration:**
    *   How to best structure the prompts sent to the AI to get high-quality, well-formed questions with accurate metadata.
*   **Recommended Follow-up:**
    *   Begin creating mockups for the "Define Request" and "Human Review" screens.
