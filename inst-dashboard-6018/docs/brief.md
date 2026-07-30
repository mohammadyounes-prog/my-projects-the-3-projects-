# Project Brief: AI Question Collector

## Executive Summary

This document outlines the project brief for the "AI Question Collector," an application designed to automate the sourcing, categorization, and exporting of educational exam questions. The primary problem this project addresses is the manual, time-consuming, and inconsistent process of creating question banks for educational purposes. The proposed solution is a web application that implements a "Define, Generate, Review, Export" workflow, leveraging a Large Language Model (LLM) to generate questions based on highly specific user criteria. The key value proposition is a massive reduction in the time and effort required to assemble high-quality, standardized question sets.

## Problem Statement

Educators, curriculum developers, and researchers currently spend countless hours manually searching for, writing, and standardizing exam questions. This process is inefficient, prone to inconsistency, and difficult to scale. Existing solutions are often simple content repositories without intelligent generation or categorization capabilities, failing to address the core need for custom, criteria-driven question creation. The urgency is to provide a tool that frees up valuable time for educators, allowing them to focus on teaching rather than administrative tasks.

## Proposed Solution

The proposed solution is a web application centered around a four-step workflow: **Define, Generate, Review, and Export**.

1.  **Define:** A user specifies detailed parameters for a batch of questions, including `Country`, `Educational Level`, `Speciality`, `Course`, `Unit/Section`, `Question Type`, and `Number of Questions`.
2.  **Generate:** The application sends a structured prompt to an AI model, which generates the questions along with rich metadata such as `Learning Outcome`, `Cognitive Level`, and `Difficulty Score`.
3.  **Review:** A human reviewer assesses the AI-generated questions for quality and accuracy, with the ability to edit or discard them.
4.  **Export:** The approved questions are saved to a database and can be exported to a CSV file for use in other systems.

The key differentiator is the shift from manual searching to automated, on-demand generation, combined with a human-in-the-loop quality assurance process.

## Target Users

The primary user segment is **Curriculum Developers & Educators**. These users are responsible for creating assessments and course materials. Their main pain point is the immense time investment required to create question banks. They need a tool that is fast, reliable, and produces questions that are accurately categorized and aligned with educational standards.

## Goals & Success Metrics

*   **Business Objective:** Reduce the time required to create a standardized question bank by at least 80% compared to manual methods.
*   **User Success Metric:** A user can successfully generate, review, and export a batch of 50 high-quality questions in under 15 minutes.
*   **Key Performance Indicators (KPIs):**
    *   Number of questions generated per week.
    *   Average user rating of generated question quality (1-5 stars).
    *   Time from initial request to final export.

## MVP Scope

**Core Features (Must Have):**
*   **User Authentication:** Basic user login and registration.
*   **Define Request Form:** A UI for users to input all parameters for question generation.
*   **AI Generation Service:** Backend integration with an LLM API to handle question generation.
*   **Review Interface:** A UI for a human reviewer to see generated questions, edit them, and approve or reject them.
*   **Database Storage:** A system to store approved questions with all their associated metadata.
*   **CSV Export:** Functionality to export the stored questions into a CSV file.

**Out of Scope for MVP:**
*   AI-Powered Retrieval of questions from the internet.
*   Automated source validation.
*   Advanced analytics dashboards.
*   Multiple export formats (only CSV for MVP).

## Post-MVP Vision

*   **Phase 2 Features:** Implement the "AI-Powered Retrieval" feature to find and extract existing questions from pre-approved, reputable online sources.
*   **Long-term Vision:** Develop an ecosystem of tools for assessment creation, including features for generating entire quizzes and exams, not just individual questions.
*   **Expansion Opportunities:** Expand the AI's capabilities to handle more complex question types, such as short-answer or diagram-based questions.

## Technical Considerations

*   **Platform Requirements:** Web-based application, accessible on modern desktop browsers.
*   **Technology Preferences (Initial Thoughts):**
    *   **Frontend:** A modern JavaScript framework (e.g., React, Vue).
    *   **Backend:** A scalable backend language (e.g., Python, Node.js).
    *   **Database:** A relational or NoSQL database suitable for storing structured question data.
    *   **Hosting/Infrastructure:** Cloud-based hosting (e.g., AWS, Google Cloud, Azure).
*   **Integration Requirements:** A critical integration with at least one major LLM provider's API (e.g., OpenAI, Google Gemini).

## Constraints & Assumptions

*   **Constraints:** This project will be developed by a small team with a limited initial budget, emphasizing a lean MVP.
*   **Key Assumptions:**
    *   A suitable and affordable LLM API is available that can consistently generate high-quality questions and metadata from structured prompts.
    *   A human reviewer will be available to ensure the quality of the questions.
    *   The target users are comfortable using web applications and reviewing AI-generated content.

## Risks & Open Questions

*   **Key Risks:**
    *   **Quality of AI Generation:** The AI may produce inaccurate, biased, or low-quality questions. (Mitigation: Human reviewer).
    *   **API Cost:** The cost of the LLM API calls could become prohibitively expensive at scale. (Mitigation: Research and select a cost-effective model; implement usage quotas).
*   **Open Questions:**
    *   What is the optimal prompt structure to send to the AI to maximize the quality of the generated questions and metadata?
    *   What is the most efficient UI for the human review process?

## Appendices

*   **References:** The detailed ideation process and initial mind maps are captured in `docs/brainstorming-session-results.md`.

## Next Steps

1.  **Design UI/UX Mockups:** Create mockups for the "Define Request" and "Human Review" screens.
2.  **Prototype AI Integration:** Develop a small-scale prototype to test the feasibility of generating questions with a chosen LLM API.
3.  **Develop PRD:** Create a full Product Requirements Document (PRD) based on this brief.
