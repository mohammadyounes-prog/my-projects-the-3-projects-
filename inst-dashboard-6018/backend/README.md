# Backend API (FastAPI)

This directory will house the backend application logic, built with FastAPI.

## Project Structure:

```
backend/
├── __init__.py
├── main.py               # FastAPI application instance
├── api/                  # API routers and endpoints
│   ├── __init__.py
│   ├── v1/               # Version 1 API endpoints
│   │   ├── __init__.py
│   │   ├── endpoints/    # Specific endpoint groups (e.g., auth, data, settings)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── data.py
│   │   │   └── settings.py
│   │   └── deps.py       # Dependency injection
│   └── api.py            # Main API router
├── core/                 # Core utilities and configurations
│   ├── __init__.py
│   ├── config.py         # Configuration loading (dotenv, etc.)
│   ├── security.py       # JWT, password hashing, etc.
│   └── translations.py   # Multilingual support
├── database/             # Database interaction logic
│   ├── __init__.py
│   ├── session.py        # Database connection management
│   └── models.py         # Pydantic models for data validation
├── models/               # Pydantic models for request/response bodies (if not in db)
│   ├── __init__.py
│   └── dashboard_models.py
├── requirements.txt      # Python dependencies
└── uvicorn_config.py     # Uvicorn server configuration (optional)
```

## Key Components:

*   **`main.py`**: Initializes the FastAPI app, configures middleware (CORS, static files), and includes API routers.
*   **`core/config.py`**: Handles loading environment variables (e.g., database connection strings, JWT secrets) using `python-dotenv`.
*   **`core/security.py`**: Manages authentication utilities like JWT token creation/validation and password hashing.
*   **`database/session.py`**: Handles establishing and managing connections to the QuestAI SQLite database and the Online Exam MySQL database.
*   **`api/v1/endpoints/`**: Contains specific endpoint logic for different functionalities (e.g., fetching aggregated data, managing settings).
*   **`models/dashboard_models.py`**: Defines Pydantic models for API request and response payloads.
*   **`requirements.txt`**: Lists all necessary Python packages.
