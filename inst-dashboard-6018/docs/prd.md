# AI Question Collector Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1. Goals

*   **Business Objective:** Reduce the time required to create a standardized question bank by at least 80% compared to manual methods.
*   **User Success Metric:** A user can successfully generate, review, and export a batch of 50 high-quality questions in under 15 minutes.
*   **Key Performance Indicators (KPIs):**
    *   Number of questions generated per week.
    *   Average user rating of generated question quality (1-5 stars).
    *   Time from initial request to final export.

### 1.2. Background Context

The project aims to solve the inefficiency and inconsistency in the manual creation of educational exam questions. Educators and curriculum developers spend a significant amount of time on this task, which could be better spent on teaching.

The proposed solution is a web application that automates the generation of questions using an AI model. The workflow consists of four steps: Define, Generate, Review, and Export. This will allow users to quickly generate high-quality, standardized question sets based on specific criteria, with a human-in-the-loop process to ensure quality.

### 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
|      |         |             |        |

---

## 2. Requirements

### 2.1. Functional

1.  **FR1:** The system shall provide user authentication (registration and login).
2.  **FR2:** The system shall include a "Define Request" form for users to input all parameters for question generation.
3.  **FR3:** The system shall have an AI Generation Service that integrates with an LLM API to handle question generation.
4.  **FR4:** The system shall have a "Review Interface" for a human reviewer to see, edit, approve, or reject generated questions.
5.  **FR5:** The system shall have a database to store approved questions and their associated metadata.
6.  **FR6:** The system shall allow users to export stored questions into a CSV file.

### 2.2. Non-Functional

1.  **NFR1:** The application must be a web-based application accessible on modern desktop browsers.
2.  **NFR2:** The frontend should be built with a modern JavaScript framework (e.g., React, Vue).
3.  **NFR3:** The backend should be built with a scalable language (e.g., Python, Node.js).
4.  **NFR4:** The system must use a relational or NoSQL database suitable for storing structured question data.
5.  **NFR5:** The application must be hosted on a cloud-based infrastructure (e.g., AWS, Google Cloud, Azure).
6.  **NFR6:** The system requires a critical integration with at least one major LLM provider's API.

---

## 3. User Interface Design Goals

### 3.1. Overall UX Vision

The user experience should be clean, minimalist, and professional, prioritizing efficiency and ease of use. The primary goal is to guide the user seamlessly through the "Define, Generate, Review, Export" workflow with clear, step-by-step instructions and minimal cognitive load.

### 3.2. Key Interaction Paradigms

*   **Define Step:** A multi-step, wizard-style interface will be used to guide the user through the process of defining the parameters for a question batch. This breaks down a complex form into manageable steps.
*   **Review Step:** A table-based or card-based layout will be used to display the list of generated questions, allowing for quick scanning, inline editing, and approval or rejection.

### 3.3. Core Screens and Views

*   Login/Registration Screen
*   Main Dashboard (to view and manage question generation tasks)
*   Define Request Screen (the wizard interface)
*   Review Screen (for quality assurance of generated questions)
*   User Profile/Settings Page

### 3.4. Accessibility: WCAG AA

### 3.5. Branding

To be determined. No specific branding guidelines have been provided.

### 3.6. Target Device and Platforms: Web Responsive

---

## 4. Technical Assumptions

### 4.1. Repository Structure: Monorepo

A single repository will be used to house both the frontend and backend code.

### 4.2. Service Architecture: Monolith

The application will be built as a single, unified service (a monolith).

### 4.3. Testing Requirements: Unit + Integration

The project will require both unit tests for individual components and integration tests to verify interactions between them.

### 4.4. Additional Technical Assumptions and Requests

*   **Frontend:** A modern JavaScript framework (e.g., React, Vue) will be used.
*   **Backend:** A scalable backend language (e.g., Python, Node.js) will be used.
*   **Database:** A relational or NoSQL database will be chosen based on the final data model.
*   **Hosting:** The application will be deployed on a major cloud platform (e.g., AWS, Google Cloud, Azure).
*   **LLM Integration:** A critical integration with a major LLM provider's API is required.

---

## 5. Epic List

*   **Epic 1: Foundation & Core Question Generation Workflow:** This epic establishes the project's technical foundation and delivers the complete, end-to-end user workflow for generating, reviewing, and exporting a batch of questions.
*   **Epic 2: Enhanced Task Management & User Settings:** This epic builds upon the core workflow by introducing a dashboard to manage past and present generation tasks and allowing users to manage their own settings.

---

### Epic 1: Foundation & Core Question Generation Workflow

**Goal:** This epic focuses on establishing the project's foundational infrastructure and delivering the core, end-to-end functionality. By the end of this epic, a user will be able to register, log in, define criteria for question generation, have the AI generate those questions, review the results, and export them to a CSV file.

---

#### **Story 1.1: Project Setup & Health Check**

*   **As a** developer,
*   **I want** to set up the initial project structure with a basic CI/CD pipeline,
*   **so that** we have a stable foundation for development and deployment.

**Acceptance Criteria:**
1.  A monorepo is created in version control (e.g., Git).
2.  A basic health-check endpoint is created for the backend service.
3.  A basic placeholder page is created for the frontend application.
4.  A CI/CD pipeline is configured to build and test the application on every commit.

---

#### **Story 1.2: User Authentication**

*   **As a** user,
*   **I want** to register for an account and log in,
*   **so that** I can securely access the application.

**Acceptance Criteria:**
1.  A user can navigate to registration and login pages.
2.  A user can register with an email and password.
3.  A user can log in with their credentials.
4.  Passwords are securely stored (hashed and salted).
5.  The user is redirected to the main application page after a successful login.

---

#### **Story 1.3: Define Request Form**

*   **As a** user,
*   **I want** to access a form to specify all required parameters for generating questions,
*   **so that** I can define the exact type of questions I need.

**Acceptance Criteria:**
1.  A "Define Request" page is available to authenticated users.
2.  The form contains input fields for all specified parameters (`Country`, `Educational Level`, `Speciality`, etc.).
3.  The form includes a "Generate" button to submit the request.
4.  Basic form validation is implemented to ensure required fields are filled.

---

#### **Story 1.4: AI Generation & Review Interface**

*   **As a** user,
*   **I want** the system to generate questions based on my request and display them in a review interface,
*   **so that** I can assess their quality.

**Acceptance Criteria:**
1.  Submitting the "Define Request" form triggers the AI generation process.
2.  The backend service calls the configured LLM API with a structured prompt.
3.  The generated questions and their metadata are displayed to the user in a clear, list-based interface.
4.  The user can edit the text of a question and its associated metadata.
5.  The user can approve or reject each individual question.

---

#### **Story 1.5: Database Storage & CSV Export**

*   **As a** user,
*   **I want** the system to save my approved questions and allow me to export them as a CSV file,
*   **so that** I can use them in other systems.

**Acceptance Criteria:**
1.  Approved questions are saved to the database.
2.  Rejected questions are discarded.
3.  An "Export to CSV" button is available on the review page.
4.  Clicking the export button downloads a CSV file containing all the approved questions from the current batch, with all data and metadata in columns.

---

### Epic 2: Enhanced Task Management & User Settings

**Goal:** This epic builds upon the core functionality delivered in Epic 1. It introduces features that improve the user's ability to manage their work over time and customize their experience. By the end of this epic, users will be able to view their history of generation tasks and manage their personal settings.

---

#### **Story 2.1: Task History Dashboard**

*   **As a** user,
*   **I want** to see a dashboard with a list of my past and current question generation tasks,
*   **so that** I can track my work and revisit previous batches.

**Acceptance Criteria:**
1.  A "Dashboard" or "My Tasks" page is available after login.
2.  The page displays a list of all generation tasks initiated by the user.
3.  Each item in the list shows key information, such as the date, the number of questions requested, and the task's status (e.g., "In Progress," "Completed").
4.  Clicking on a completed task navigates the user to the review page for that specific batch of questions.

---

#### **Story 2.2: User Profile & Settings Page**

*   **As a** user,
*   **I want** a settings page where I can manage my profile information,
*   **so that** I can keep my account details up to date.

**Acceptance Criteria:**
1.  A "Settings" or "Profile" page is accessible to the user.
2.  The user can view their registered email address on this page.
3.  The user has an option to change their password, which follows secure practices (e.g., requires current password).

---