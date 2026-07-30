# QuestAI Functional Features

This document lists the functional features of the QuestAI platform, categorized for clarity, based on the project analysis.

**I. User and Authentication Management:**
1.  **User Registration:** Allows new users to register with username, password, full name, mobile, email, audience type, and country.
2.  **User Login:** Secure login with JWT (JSON Web Tokens).
3.  **Token Refresh:** Mechanism to refresh access tokens to maintain user sessions.
4.  **Role-Based Access Control (RBAC):** Supports different user roles (regular user, admin, superadmin) with varying access levels to features and data.
5.  **User Profile Management:** Users can manage their personal information.

**II. Question Generation (AI-Powered):**
6.  **Multi-Factor Question Generation:** Generates questions based on a comprehensive set of parameters:
    *   Topic Context
    *   Question Type (multiple choice, open-ended, etc.)
    *   Difficulty Level
    *   Cognitive Level (e.g., Remembering, Understanding, Applying)
    *   Learning Outcome
    *   Audience Type (School, University, Company)
    *   Audience-Specific Properties (e.g., School Type, Subject, Year, Major, Course, Material, Semester, Company, Department, Job Role).
7.  **AI Model Integration:** Supports question generation via Google Gemini and OpenAI models.
8.  **Dummy Model Support:** Allows for testing and development without consuming external AI API quotas.
9.  **Question Parsing:** Parses AI model outputs into a structured format for storage.

**III. Question Management (CRUD & Workflow):**
10. **Question Creation:** Stores newly generated questions with all associated metadata.
11. **Question Retrieval/Search:**
    *   Search by text query across question text, choices, correct options.
    *   Filter by status (pending, approved, rejected).
    *   Filter by user, tenant, date range.
    *   Admin/Superadmin specific filters (approved by, rejected by, edited by, deleted by).
    *   Pagination for large datasets.
12. **Question Editing:** Users with appropriate permissions can edit existing questions.
13. **Question Deletion:** Users with appropriate permissions can delete single or multiple questions.
14. **Question Status Update:** Workflow for approving/rejecting questions.
15. **Question History/Audit Trail:** Logs actions performed on questions (approved, rejected, edited, deleted) with actor and timestamp.
16. **Solution Retrieval:** Provides solutions for specific questions.

**IV. Tenant Management:**
17. **Dynamic Tenant Creation:** Automatically creates tenants based on country for new user registrations.
18. **Tenant Listing/Management:** (Admin/Superadmin functionality) View and manage tenants.
19. **Tenant Hierarchy:** (Implied by `parent_id` field, and `get_tenant_hierarchy` function) Supports multi-level tenant structures.

**V. AI Model Management:**
20. **Dynamic AI Model Registration:** Allows registration of different AI generation models.
21. **Model Configuration:** Stores model API names, generation methods, default status, active status, and API keys.
22. **Tenant-Specific Models:** Supports models configured for specific tenants or global models.

**VI. Billing and Usage Tracking:**
23. **Question Balance Management:** Tracks user-specific question balances per audience type.
24. **Usage Deduction:** Automatically deducts questions from user balance upon generation.
25. **Billing Events Logging:** Records billing events (e.g., debits for question generation).
26. **Product Management:** (Admin/Superadmin functionality) Manage billing products.
27. **Billing Event Reporting:** (Admin/Superadmin functionality) View and filter billing events.

**VII. Lookup Data and Dynamic Properties:**
28. **Dynamic Lookup System:** Provides API endpoints to fetch lists of various academic/professional properties (e.g., school types, subjects, difficulty levels, cognitive levels, learning outcomes, university majors, companies, job roles).
29. **User-Specific Preferences:** Allows users to store and retrieve specific audience items (e.g., their preferred subjects, majors).

**VIII. TamsQB (Online-Exam System) Integration:**
30. **Course and Category Setup:** Creates daily courses and sequentially numbered user-specific categories in the `online-exam` MySQL database.
31. **Default Filter/Objective Setup:** Initializes default filters and learning objectives for newly created courses/categories in the `online-exam` system.
32. **Question Banking:** Pushes generated questions from QuestAI's `questions.db` to the `online-exam` system's `bank` table, including data transformation and type mapping.
33. **Exam Creation:** Automatically creates full exams in the `online-exam` system based on banked questions, including settings and questions payload.
34. **Exam Publishing:** Sets the status of an exam in the `online-exam` system to 'published'.
35. **Student Status Management:** Adds student status records to the `online-exam` system.
36. **Question Logging for Exams:** Logs which questions from the bank are used in a specific exam.
37. **Online-Exam User Registration:** Registers QuestAI users as students in the `online-exam` database, including compatible password hashing.

**IX. Frontend/UI Features:**
38. **Intuitive Dashboard:** A central interface for question generation and management.
39. **Dynamic Forms:** Generation forms adapt based on selected audience type to show relevant fields.
40. **Pagination and Filtering:** User-friendly navigation and search capabilities for question lists.
41. **Modal Dialogs:** For editing questions, displaying solutions, and confirming actions.
42. **CSV Export:** Export generated/filtered questions to CSV format.
43. **Internationalization (i18n):** Supports multiple languages (English and Arabic detected).
44. **Right-to-Left (RTL) Support:** CSS (`rtl.css`) for proper display of RTL languages.
45. **Responsive Design:** (Implied by Bootstrap 5 usage) Adapts to different screen sizes.
46. **Session-Based Workflow Enforcement:** Enforces a specific user journey (e.g., generate questions before taking a test) using `sessionStorage`.
