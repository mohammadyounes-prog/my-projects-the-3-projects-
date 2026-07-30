# Brainstorming Session: Question Generation Project

## Executive Summary

- **Session Topic:** A question generation project for educators and professionals to create questions for exams, assignments, and training.
- **Session Goals:** Focused ideation on the features and workflow for a question generation tool that exports to XLS format for use in a larger examination system.
- **Project Scope:** The project is a **Question Generator** that allows users to retrieve and/or generate questions with specific metadata, then export them to an XLS file.
- **Techniques Used:** Job-to-be-Done (JTBD)
- **Total Ideas Generated:** 8 core ideas/features.
- **Key Themes Identified:** The central themes are (1) deep, metadata-driven filtering, (2) a hybrid retrieval/generation model, and (3) the importance of a structured XLS export.

---

## Idea Categorization

### Immediate Opportunities (Core MVP Features)
- **Cascading Filter UI:** The detailed, multi-level dropdown menu system (Country, Audience, Course, etc.) is the core of the user experience and the first thing to build.
- **Structured XLS Export:** The system's primary output must be a correctly formatted XLS file. This is a critical, non-negotiable feature.
- **Question Metadata:** The ability to define and attach metadata like **Difficulty Level** and **Bloom's Taxonomy Level** to each question.

### Future Innovations (Version 2.0)
- **Hybrid Generation/Retrieval Model:** Implementing a seamless workflow for a user to first search for questions and then, if needed, generate new ones. The retrieval part should be prioritized first.
- **AI-Powered Question Generation:** The "generation" part of the hybrid model. This involves more complex AI work and can be built upon the initial retrieval-based system.

### Moonshots (Ambitious, Long-Term Goals)
- **Item Response Theory (IRT) Integration:** Building in advanced psychometric analysis (like the "discrimination" factor) is a complex, data-intensive feature that would make the tool world-class but requires significant specialized development.

---

## Action Planning

### Top 3 Priority Ideas
1.  **Build the Cascading Filter UI:** This is the foundation of the entire application workflow.
2.  **Define and Implement the XLS Export Template:** The tool is not functional without its primary output.
3.  **Develop the Question Database and Retrieval System:** Create a database schema that includes all the required metadata fields and build the basic search/retrieval functionality.

### Next Steps
- **For Priority 1 (Filtering UI):**
  - **Next Step:** Create a detailed UI mockup or wireframe of the cascading dropdown workflow.
  - **Research Needed:** Define the complete data hierarchy for all potential dropdowns (e.g., a list of all countries, streams, courses).
- **For Priority 2 (XLS Export):**
  - **Next Step:** Create a definitive sample of the target XLS file, including all required columns and formatting.
- **For Priority 3 (Database):**
  - **Next Step:** Design a database schema for the question bank that accommodates all specified metadata (Difficulty, Bloom's, IRT stats, etc.).

---

## Reflection & Follow-up

- **What Worked Well:** The Job-to-be-Done (JTBD) technique was highly effective. It helped us pivot from a broad, vague concept to a very specific and well-defined project scope (a question generator exporting to XLS). The clarification of "user as creator" vs. "user as consumer" was a critical turning point.
- **Areas for Further Exploration:**
  - The specifics of the **AI Question Generation** model need their own dedicated brainstorming session. What are the inputs (e.g., a topic, a paragraph of text)? What AI models will be used?
  - The source of the **retrievable questions** needs to be defined. Will there be an initial database? Will the system scrape public sources?
- **Recommended Follow-up:** The immediate next step should be to create the UI wireframes and the sample XLS file, as they will provide the concrete specifications needed for development.
