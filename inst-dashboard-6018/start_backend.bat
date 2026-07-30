@echo off
set ONLINE_EXAM_FRONTEND_BASE_URL=http://schooldemo12.examforall.com:8888
echo Starting server with dynamic port from .env via run_server.py

:: Try to find the virtual environment in common locations
IF EXIST .\.venv\Scripts\activate (
    echo [DEBUG] Found local virtual environment.
    call .\.venv\Scripts\activate
) ELSE IF EXIST ..\..\..\.venv\Scripts\activate (
    echo [DEBUG] Found main project virtual environment.
    call ..\..\..\.venv\Scripts\activate
) ELSE (
    echo [WARNING] Virtual environment not found. Attempting to use system python.
)

python run_server.py
cmd /k
