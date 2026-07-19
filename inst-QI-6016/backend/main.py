# print("MARKER: backend/main.py loaded by uvicorn")
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Callable
# Add debug print for .env file path
dotenv_path = Path(__file__).resolve().parent / '.env'
# print(f"DEBUG: Attempting to load .env from: {dotenv_path}")
# Use override=True to ensure .env values take precedence over system environment variables
load_dotenv(dotenv_path=dotenv_path, override=True)

import logging
import time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Log active URLs on startup for debugging
logging.info(f"STARTUP: ONLINE_EXAM_API_BASE_URL = {os.getenv('ONLINE_EXAM_API_BASE_URL')}")
logging.info(f"STARTUP: ONLINE_EXAM_FRONTEND_BASE_URL = {os.getenv('ONLINE_EXAM_FRONTEND_BASE_URL')}")

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CountryLookupItem(BaseModel):
    id: int
    name: str
    english_name: Optional[str] = None
    name_ar: Optional[str] = None

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from pathlib import Path
import re
import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os # Ensure os is imported for getenv

# JWT Configuration for Online Exam API (matching PHP application's expected token)
ONLINE_EXAM_JWT_SECRET_KEY = os.getenv("ONLINE_EXAM_JWT_SECRET", "0598251486UserPassSecret") # From PHP config.php license hash
ONLINE_EXAM_JWT_ALGORITHM = "HS256"
ONLINE_EXAM_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

def create_online_exam_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ONLINE_EXAM_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ONLINE_EXAM_JWT_SECRET_KEY, algorithm=ONLINE_EXAM_JWT_ALGORITHM)
    return encoded_jwt
import json
import mimetypes
import hashlib
import uuid
import docx
import pdfplumber
import fitz # PyMuPDF
import pytesseract # For OCR
from PIL import Image # For image processing in OCR
import logging
import sys
import time

# Explicitly set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_translations(lang: str) -> Dict:
    # Use absolute path relative to this script's directory
    backend_dir = Path(__file__).resolve().parent
    locale_path = backend_dir.parent / "frontend" / "locales" / f"{lang}.json"

    if not locale_path.exists():
        # Fallback to English if the requested language doesn't exist
        locale_path = backend_dir.parent / "frontend" / "locales" / "en.json"

    try:
        with open(locale_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Translation file not found at: {locale_path}")
        return {}
# Configure a new logger to ensure all messages are captured at the appropriate level
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clear existing handlers to prevent duplicate output or interference
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

# Create a console handler to print messages to stderr
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Use RotatingFileHandler to keep log file size small and prevent disk I/O bottlenecks
from logging.handlers import RotatingFileHandler
DEBUG_LOG_FILE_PATH = Path(__file__).resolve().parent / "new_debug.log"
# Limit to 5MB, keep 3 backup files
file_handler = RotatingFileHandler(DEBUG_LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# SILENCE CHATTY LIBRARIES
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)


# Original logging initialization (removed or commented out)
# LOG_FILE_PATH = Path(__file__).resolve().parent / "debug.log"
# file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
# file_handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)
# logging.info(f"Logging initialized. Log file: {LOG_FILE_PATH}")

import hashlib # Ensure hashlib is imported for file hashing
import database
from database import (
    get_lookup_data_list, insert_question, get_user, create_user, get_questions, delete_question,
    get_question_by_id, update_question, update_question_status, insert_generation_task,
    get_generation_tasks_by_user, update_generation_task_status, update_user_password,
    get_total_questions_count, get_search_suggestions, get_property_types_by_audience, get_question_types_by_audience,
    get_all_users, get_all_tenants, get_all_generation_models, get_generation_model_by_api_name,
    get_question_history, create_generation_model, get_user_specific_audience_items,
    add_user_specific_audience_item, delete_user_specific_audience_item, get_db_connection,
    get_unbanked_questions_for_user, update_question_tamsqb_bank_added_status,
    insert_uploaded_file, get_uploaded_file_content, update_generation_task_generated_count, update_uploaded_file_task_id, get_uploaded_file_by_hash, # NEW IMPORT
    insert_exam, link_question_to_exam, get_finished_exams_for_user, get_question_ids_for_exam, unhide_answers_for_questions, get_exams_for_user, update_user_schooldemo12_id, get_total_exams_for_user_count, get_exam_questions_and_details, get_student_results_for_exam, get_exam_by_id, update_exam_report_image_path, delete_exam_report,
    insert_printed_exam, # NEW IMPORT
    get_unique_categories_for_audience, # NEWLY ADDED
    get_course_filter_options, # NEWLY ADDED
    create_tenant, # ADDED
    get_user_by_id, # ADDED
    get_user_by_schooldemo12_id, # ADDED
    get_db, # ADDED FOR FASTAPI DEPENDENCY INJECTION
    run_migrations # ADDED
)
import sqlite3
from fastapi.responses import FileResponse
from online_exam_db_connector import add_course_and_category_to_online_exam_db, setup_course_defaults, insert_question_to_bank, get_user_course_category_ids, create_exam_in_online_exam_db, publish_exam_status, add_student_to_online_exam_db, add_student_status_to_online_exam_db, log_questions_for_exam, get_employee_by_id, get_teacher_link_id_by_teacher_id, get_teacher_link_details, _add_exam_specific_filters, get_all_exam_names # NEW IMPORT
from report_generator import generate_report_image, generate_report_html, REPORT_DIR # NEW IMPORT

logging.info(f"DEBUG: main.py loaded from: {os.path.abspath(__file__)}")
logging.info(f"DEBUG: database.py loaded from: {os.path.abspath(database.__file__)}")

from gemini_api import generate_questions_with_gemini, list_available_gemini_models, generate_solution_with_gemini
from openai_api import call_openai_chat
from auth_utils import (
    User,
    Token,
    get_current_user,
    get_user_from_expired_token,
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from admin import router as admin_router
from admin_billing import router as admin_billing_router
from billing import router as billing_router, deduct_from_balance, get_user_question_balance
from dashboard import router as dashboard_router
from admin import LookupItem, UserOut

import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Application startup: Database migrations are disabled in lifespan.")
    # run_migrations()  # Disabled to prevent CPU overhead on startup
    yield

app = FastAPI(lifespan=lifespan) # Trigger reload V4

@app.post("/api/debug/log")
async def log_frontend_debug(data: dict):
    """Logs frontend debug information using the established rotating logger."""
    logger.info(f"FRONTEND DEBUG: {json.dumps(data)}")
    return {"status": "ok"}

from auth_utils import (
    User,
    Token,
    get_current_user,
    get_user_from_expired_token,
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from sso_utils import verify_sso_token
from database import get_user_by_id

class SSOExchangeRequest(BaseModel):
    sso_token: str

class GoogleAuthRequest(BaseModel):
    token: str

@app.post("/api/v1/auth/google")
async def google_auth(request: GoogleAuthRequest):
    """
    Placeholder for Google OAuth token verification and local login.
    """
    print(f"[DEBUG] Received Google Token: {request.token[:10]}...")
    # NOTE: You need to implement Google token verification here!
    # For now, return a dummy success to allow the flow to continue.
    return {
        "access_token": "dummy_token_from_backend",
        "name": "User",
        "is_super_admin": False
    }

@app.post("/api/v1/auth/exchange-sso-token", response_model=Token)
async def exchange_sso_token(request: SSOExchangeRequest):
    """
    Exchanges a global SSO token for a local-service-specific JWT.
    """
    # 1. Verify SSO Token against central database
    user_id = verify_sso_token(request.sso_token)
    
    # 2. Generate local JWT for this specific app
    # We need to fetch user details to include tenant_id and audience_type in JWT
    user = get_user_by_id(user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create local JWT
    access_token = create_access_token(
        data={"sub": str(user_id), "tenant_id": user["tenant_id"]},
        audience_type=user["audience_type"]
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": user["is_admin"],
        "expires_in": 1440 * 60, # 24 hours in seconds
        "is_super_admin": user["is_super_admin"]
    }

UPLOAD_DIRECTORY = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True) # Ensure upload directory exists

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def generate_pdf_from_html(html_content: str, output_path: Path) -> bool:
    """
    Converts HTML content to a PDF file using imgkit.
    """
    options = {
        'enable-local-file-access': None, # Needed if HTML contains local file references (e.g., CSS, images)
        'enable-smart-shrinking': True,
        'no-stop-slow-scripts': True, # Important for complex HTML/JS
        'enable-javascript': True, # Enable JavaScript
        'debug-javascript': True, # Debug JavaScript
        'log-level': 'debug', # Set log level to debug
        'page-size': 'A4', # Explicitly set page size
        'orientation': 'Portrait', # Explicitly set orientation
    }
    try:
        if CONFIG_PDF: # Use CONFIG_PDF
            success = imgkit.from_string(html_content, str(output_path), options=options, config=CONFIG_PDF)
        else:
            success = imgkit.from_string(html_content, str(output_path), options=options, config=CONFIG_PDF)
        
        if not success:
            logging.error(f"imgkit.from_string returned False for {output_path}. Check wkhtmltopdf installation and PATH.")
        return success
    except Exception as e:
        logging.error(f"Error generating PDF with imgkit: {e}", exc_info=True)
        return False

def extract_text_from_file(file_path: Path, file_type: str) -> str:
    text_content = ""
    if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": # .docx
        try:
            document = docx.Document(file_path)
            for paragraph in document.paragraphs:
                text_content += paragraph.text + "\n"
        except Exception as e:
            logging.error(f"Failed to extract text from DOCX file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to extract text from DOCX file: {e}")
    elif file_type == "application/pdf": # .pdf
        text_content = ""
        
        # 1. Try PyMuPDF (fitz) - FASTEST
        logging.info(f"PDF Extraction: Attempting PyMuPDF (fitz) for {file_path.name}")
        start_time = time.perf_counter()
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text_content += page_text + "\n"
            doc.close()
            
            if text_content.strip():
                duration = time.perf_counter() - start_time
                logging.info(f"SUCCESS: PyMuPDF (fitz) extraction took {duration:.4f} seconds.")
                return text_content.strip()
            else:
                logging.warning(f"PyMuPDF (fitz) returned NO TEXT for {file_path.name}. It might be a scanned image.")
        except Exception as e:
            logging.warning(f"PyMuPDF (fitz) FAILED for {file_path.name}: {str(e)}")

        # 2. Try pdfplumber - FALLBACK (more accurate for tables but slower)
        logging.info(f"PDF Extraction: Attempting pdfplumber fallback for {file_path.name}")
        start_time = time.perf_counter()
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if text_content.strip():
                duration = time.perf_counter() - start_time
                logging.info(f"SUCCESS: pdfplumber extraction took {duration:.4f} seconds.")
                return text_content.strip()
            else:
                logging.warning(f"pdfplumber returned NO TEXT for {file_path.name}. Moving to OCR.")
        except Exception as e:
            logging.warning(f"pdfplumber FAILED for {file_path.name}: {str(e)}")

        # 3. Fallback to Parallel OCR if both fast extractors fail
        logging.info(f"PDF Extraction: Both fast extractors failed. Attempting OCR for: {file_path.name}")
        start_time = time.perf_counter()
        try:
            doc = fitz.open(file_path)
            page_count = doc.page_count
            
            def ocr_page(page):
                page_num = page.number + 1
                logging.info(f"OCR: Processing page {page_num}...")
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                logging.info(f"OCR: Finished page {page_num}. Extracted {len(text)} chars.")
                return text

            if page_count == 1:
                # Skip executor overhead for single page
                ocr_text_content = ocr_page(doc.load_page(0))
            else:
                import concurrent.futures
                pages_to_ocr = [doc.load_page(i) for i in range(page_count)]
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    results = list(executor.map(ocr_page, pages_to_ocr))
                ocr_text_content = "\n".join(results)
            
            doc.close()
            
            if ocr_text_content.strip():
                duration = time.perf_counter() - start_time
                logging.info(f"SUCCESS: OCR extraction took {duration:.4f} seconds.")
                return ocr_text_content.strip()
            else:
                logging.error("OCR yielded no text content.")
                raise HTTPException(status_code=500, detail="Failed to extract any text even with OCR.")
        except pytesseract.TesseractNotFoundError:
            logging.error("Tesseract not found at expected path.")
            raise HTTPException(status_code=500, detail="Tesseract OCR engine not found.")
        except Exception as e:
            logging.error(f"OCR failed with error: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during OCR: {e}")

    else:
        # For other text-based files, or as a fallback
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                text_content = f.read()
        except Exception as e:
            logging.error(f"Failed to extract text from file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    return text_content.strip()

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user) # Re-add dependency
):
    logging.debug(f"Received file upload request for user: {current_user['username']}")
    logging.debug(f"File details - Filename: {file.filename}, Content-Type: {file.content_type}")

    try:
        # Authentication check (though Depends should handle much of it)
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Check file size (e.g., limit to 10MB)
        MAX_FILE_SIZE_MB = 50
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
        file_content = await file.read() # Read content once
        if len(file_content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")
        
        # Rewind file for subsequent reads (e.g., by text extractor)
        await file.seek(0) 

        # Sanitize the filename to remove non-ASCII characters
        sanitized_filename = re.sub(r'[^\x00-\x7F]+', '', file.filename)
        
        # Generate a unique filename to prevent collisions
        unique_filename = f"{uuid.uuid4()}_{sanitized_filename}"
        file_location = UPLOAD_DIRECTORY / unique_filename

        # Save the file
        with open(file_location, "wb") as file_object:
            file_object.write(file_content)

        # Extract text content
        extracted_text = extract_text_from_file(file_location, file.content_type)
        logging.debug(f"Extracted text length: {len(extracted_text)}")

        # Store metadata in the database
        file_id = insert_uploaded_file(
            user_id=current_user["id"],
            tenant_id=current_user["tenant_id"],
            file_name=file.filename,
            file_path=str(file_location),
            file_type=file.content_type,
            extracted_content=extracted_text
        )

        return {"message": "File uploaded and processed successfully", "file_id": file_id, "file_name": file.filename}
    except HTTPException as e:
        logging.error(f"HTTPException in /uploadfile: {e.detail}")
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/conlib/list")
async def list_conlib_contents(rel_path: str = "", current_user: User = Depends(get_current_user)):
    conlib_root = Path(__file__).resolve().parent / "conlib"
    # Ensure rel_path doesn't try to escape conlib_root
    safe_rel_path = rel_path.lstrip("/").lstrip("\\")
    target_path = (conlib_root / safe_rel_path).resolve()

    # Security check: Ensure target_path is within conlib_root
    if not str(target_path).startswith(str(conlib_root)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Directory not found")

    items = []
    try:
        for entry in os.scandir(target_path):
            is_dir = entry.is_dir()
            items.append({
                "name": entry.name,
                "is_dir": is_dir,
                "rel_path": str(Path(safe_rel_path) / entry.name).replace("\\", "/")
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower()))

class ConlibSelectRequest(BaseModel):
    rel_path: str

@app.post("/conlib/select")
async def select_conlib_file(request: ConlibSelectRequest, current_user: User = Depends(get_current_user)):
    conlib_root = Path(__file__).resolve().parent / "conlib"
    safe_rel_path = request.rel_path.lstrip("/").lstrip("\\")
    file_path = (conlib_root / safe_rel_path).resolve()

    # Security check
    if not str(file_path).startswith(str(conlib_root)):
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Extract text
    file_type, _ = mimetypes.guess_type(file_path)
    if not file_type:
        if file_path.suffix == ".docx":
            file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_path.suffix == ".pdf":
            file_type = "application/pdf"
        else:
            file_type = "text/plain"

    try:
        # Calculate hash for reuse
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Check if already processed
        existing_file = get_uploaded_file_by_hash(file_hash)
        if existing_file:
            return {"message": "Server file already processed", "file_id": existing_file["id"], "file_name": file_path.name}

        extracted_text = extract_text_from_file(file_path, file_type)

        # Store in DB
        file_id = insert_uploaded_file(
            user_id=current_user["id"],
            tenant_id=current_user["tenant_id"],
            file_name=file_path.name,
            file_path=str(file_path),
            file_type=file_type,
            extracted_content=extracted_text,
            file_hash=file_hash
        )

        return {"message": "Server file processed successfully", "file_id": file_id, "file_name": file_path.name}
    except Exception as e:
        logging.error(f"Error processing server file {request.rel_path}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process server file: {e}")


@app.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordVerifyRequest(BaseModel): # NEW MODEL
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    mobile_phone: Optional[str] = None
    email: str # Added email field
    audience_type: Optional[str] = None
    country: str
    role: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None

class AudienceItemRequest(BaseModel):
    name: str
    field_name: str # e.g., school_type, subject, major, etc.

@app.get("/users/me/preferences/{audience_type}")
async def get_my_preferences(audience_type: str, field_name: str, current_user: User = Depends(get_current_user)):
    if audience_type not in ["school", "university", "company", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    items = get_user_specific_audience_items(current_user["id"], audience_type, field_name)
    return items

@app.post("/users/me/preferences/{audience_type}")
async def add_my_preference(audience_type: str, item: AudienceItemRequest, current_user: User = Depends(get_current_user)):
    if audience_type not in ["school", "university", "company", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    item_id = add_user_specific_audience_item(current_user["id"], audience_type, item.field_name, item.name)
    return {"id": item_id, "name": item.name}

@app.delete("/users/me/preferences/{audience_type}/{item_id}")
async def delete_my_preference(audience_type: str, item_id: int, field_name: str, current_user: User = Depends(get_current_user)):
    if audience_type not in ["school", "university", "company", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    delete_user_specific_audience_item(current_user["id"], audience_type, field_name, item_id)
    return {"status": "success"}

@app.get("/tenants")
async def read_tenants():
    return get_all_tenants()

@app.post("/refresh_token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_user_from_expired_token)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={
            "sub": str(current_user["id"]),
            "is_admin": current_user["is_admin"],
            "is_super_admin": current_user["is_super_admin"],
            "tenant_id": current_user["tenant_id"],
        },
        expires_delta=access_token_expires,
        audience_type=current_user.get("audience_type")
    )

    return {"access_token": new_access_token, "token_type": "bearer", "is_admin": current_user["is_admin"], "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60}


origins = [
    "http://localhost:3700",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8300",
    "http://127.0.0.1:8300",
    "http://localhost:8888",
    "http://schooldemo12.localhost:8300",
    "http://schooldemo12.localhost:8888",
    "http://localhost:9000",
    "http://localhost:6015",
    "http://questai.examforall.com",
    "https://questai.examforall.com",
    "http://questai.examforall.com:8000",
    "http://aiquest.examforall.com:8000",
    "https://questai.skyline-inov.com",
    "http://questai.skyline-inov.com",
]

# Add dynamic BACKEND_BASE_URL to origins if it exists
env_backend_url = os.getenv("BACKEND_BASE_URL")
if env_backend_url and env_backend_url not in origins:
    origins.append(env_backend_url)
    # Also add the URL without port if it has one
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(env_backend_url)
        base_url_no_port = f"{parsed_url.scheme}://{parsed_url.hostname}"
        if base_url_no_port not in origins:
            origins.append(base_url_no_port)
    except Exception:
        pass



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.include_router(admin_router, prefix="/admin")
app.include_router(admin_billing_router, prefix="/admin")
app.include_router(billing_router, prefix="/billing")
app.include_router(dashboard_router, prefix="/dashboard/advice", tags=["Dashboard"])

from sso_utils import verify_sso_token, generate_sso_token

@app.post("/api/v1/auth/generate-sso-token")
async def create_sso_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Generates a global SSO token for the current authenticated user.
    """
    # 1. Get the schooldemo12_user_id (which is used in sso_sessions)
    # If the user is a teacher, their id in local DB is linked to teacher_id in online-exam
    # If student, linked via schooldemo12_user_id column.
    
    # For now, we assume the 'sub' in JWT is the primary user ID that online-exam recognizes
    # or we fetch the linked ID.
    schooldemo12_user_id = current_user.get("schooldemo12_user_id") or current_user.get("id")
    
    sso_token = generate_sso_token(user_id=int(schooldemo12_user_id))
    return {"sso_token": sso_token}

@app.get("/verify-sso")
async def verify_sso(sso_token: str, db: sqlite3.Connection = Depends(get_db)):
    print(f"[DEBUG] verify_sso: Received token: {sso_token}")
    # Verify token in MySQL to get the valid schooldemo12_user_id
    try:
        # verify_sso_token returns the user_id that generated the token (e.g., 93)
        schooldemo12_user_id = verify_sso_token(sso_token)
        logging.info(f"verify_sso: Token verified for user_id (primary): {schooldemo12_user_id}")
        
        # 1. Fetch user details from MySQL to get the username
        employee = get_employee_by_id(int(schooldemo12_user_id))
        username = employee['name'] if employee else None
        
        # 2. Try to find the user in local DB
        user = get_user_by_schooldemo12_id(int(schooldemo12_user_id), conn=db)
        
        # 3. If not found, try resolving shadow student ID and check again
        if not user and username:
            shadow_id = database.resolve_student_id_for_user(None, username)
            if shadow_id:
                logging.info(f"verify_sso: Found shadow ID {shadow_id} for user {username}, checking local DB...")
                user = get_user_by_schooldemo12_id(int(shadow_id), conn=db)
        
        # 4. If still not found, then provision
        if not user:
            logging.info(f"verify_sso: User {schooldemo12_user_id} not found locally, provisioning...")
            if not employee:
                raise HTTPException(status_code=404, detail="User not found in central DB")
            
            new_user_id = database.create_user(
                username=employee['email'],
                hashed_password="SSO_USER_NO_PASSWORD",
                email=employee['email'],
                full_name=employee['name'],
                conn=db
            )
            database.update_user_schooldemo12_id(new_user_id, int(schooldemo12_user_id), conn=db)
            user = get_user_by_id(new_user_id, conn=db)
            logging.info(f"verify_sso: User provisioned with local ID {new_user_id}")
        
        # Now resolve the actual student ID (172) used for exams if it's a teacher
        resolved_student_id = database.resolve_student_id_for_user(user['id'], user['username'])
        logging.info(f"verify_sso: Resolved student ID for exams: {resolved_student_id}")

    except Exception as e:
        print(f"[ERROR] verify_sso: Token verification failed: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")

    # Generate a new local JWT for this project using the verified schooldemo12_user_id to find the user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "is_admin": user["is_admin"],
            "is_super_admin": user["is_super_admin"],
            "tenant_id": user["tenant_id"],
            "schooldemo12_user_id": resolved_student_id # Pass the resolved student ID!
        },
        expires_delta=access_token_expires,
        audience_type=user["audience_type"]
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(payload: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    # Use a single cursor for all operations within this function for transactional integrity
    cur = None # Initialize cur to None
    try:
        cur = db.cursor()
        country_name = (payload.country or '').strip()
        if not country_name:
            raise HTTPException(status_code=400, detail="Country is required")

        if len(payload.username) < 6:
            raise HTTPException(status_code=400, detail="Username must be at least 6 characters")

        if len(payload.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        tenant_id = None
        # Attempt to find an existing tenant for the given country_name
        cur.execute("""
            SELECT t.id FROM tenants t
            JOIN tenant_countries tc ON t.id = tc.tenant_id
            JOIN countries c ON tc.country_id = c.country_id
            WHERE c.name = ?
            ORDER BY t.id ASC LIMIT 1
        """, (country_name,))
        existing_country_tenant_row = cur.fetchone()

        if existing_country_tenant_row:
            tenant_id = existing_country_tenant_row["id"]
            logging.debug(f"DEBUG: Reusing existing tenant_id {tenant_id} for country '{country_name}'.")
        else:
            # If no tenant exists for the country, create a new one with sequential naming
            country_prefix = country_name[:3].upper()
            cur.execute("SELECT name FROM tenants WHERE name LIKE ? || '%' ORDER BY name DESC", (country_prefix,))
            existing_tenants_with_prefix = cur.fetchall()
            
            next_suffix = 1
            if existing_tenants_with_prefix:
                suffixes = []
                for tenant in existing_tenants_with_prefix:
                    match = re.match(rf"^{country_prefix}(\d+)", tenant["name"])
                    if match:
                        suffixes.append(int(match.group(1)))
                if suffixes:
                    next_suffix = max(suffixes) + 1
            
            new_tenant_name = f"{country_prefix}{next_suffix}"
            tenant_id = create_tenant(name=new_tenant_name, conn=db)
            logging.debug(f"DEBUG: Created new tenant_id {tenant_id} with name '{new_tenant_name}' for country '{country_name}'.")

            # Link the new tenant to its country
            cur.execute("SELECT country_id FROM countries WHERE name = ?", (country_name,))
            country_row = cur.fetchone()
            if country_row:
                country_id = country_row["country_id"]
                cur.execute("INSERT OR IGNORE INTO tenant_countries (tenant_id, country_id) VALUES (?, ?)", (tenant_id, country_id))
                logging.debug(f"DEBUG: Linked new tenant {tenant_id} to country {country_id} ('{country_name}').")
            else:
                logging.warning(f"Country '{country_name}' not found in 'countries' table. Cannot link new tenant to country.")

        # Ensure a default dummy AI model exists for this tenant
        dummy_model_api_name = f"dummy_{tenant_id}"
        # Check if the dummy model already exists for this tenant
        cur.execute("SELECT id FROM generation_models WHERE model_api_name = ?", (dummy_model_api_name,))
        dummy_model_row = cur.fetchone()
        
        if not dummy_model_row:
            create_generation_model(
                model_name="Dummy Generator",
                model_api_name=dummy_model_api_name,
                generation_method='ai',
                tenant_id=tenant_id,
                is_default=True,
                is_active=True,
                api_key="dummy_key", # Placeholder
                conn=db
            )
            logging.debug(f"DEBUG: Created default dummy AI model '{dummy_model_api_name}' for tenant {tenant_id}.")
        else:
            logging.debug(f"DEBUG: Default dummy AI model '{dummy_model_api_name}' already exists for tenant {tenant_id}. Skipping creation.")

        # Check if user exists in that tenant
        existing = get_user(payload.username, tenant_id=tenant_id, conn=db)
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")

        cur.close()  # Done with direct cursor operations

        hashed = get_password_hash(payload.password)
        created_user_id = create_user(
            username=payload.username, 
            hashed_password=hashed, 
            is_admin=0, 
            full_name=payload.full_name, 
            tenant_id=tenant_id,
            mobile_phone=payload.mobile_phone,
            email=payload.email,
            audience_type=payload.audience_type,
            role=payload.role,
            institution=payload.institution,
            department=payload.department,
            country=payload.country, 
            conn=db
        )
        
        # After successful primary user registration, add to online-exam DB
        schooldemo12_user_id = None
        try:
            student_id = add_student_to_online_exam_db(
                username=payload.username,
                email=payload.email,
                raw_password=payload.password, # Pass the raw password for online-exam's hashing
                full_name=payload.full_name,
                mobile_phone=payload.mobile_phone,
                country=payload.country, # Pass country for the data JSON
                role=payload.role # Pass role for conditional S- prefix
            )
        
            if student_id:
                schooldemo12_user_id = student_id
        except Exception as e:
            logging.error(f"Failed to add user '{payload.username}' to online-exam student table: {e}")
            # Log the error but don't prevent primary registration from completing
        
        # Conditionally add to employees table if audience_type is school and role is teacher
        if (payload.audience_type == "school" and payload.role == "teacher") or payload.audience_type in ["company", "university"]:
            try:
                from online_exam_db_connector import add_employee_to_online_exam_db, add_teacher_link
                
                # Add employee and get back the created IDs
                employee_data = add_employee_to_online_exam_db(
                    full_name=payload.full_name if payload.full_name else payload.username,
                    email=payload.email,
                    raw_password=payload.password,
                    mobile_phone=payload.mobile_phone
                )

                if employee_data and employee_data.get("teacherId"):
                    # Use teacherId as the primary schooldemo12_user_id for instructors/teachers
                    schooldemo12_user_id = employee_data["teacherId"]
                    
                    # Create a course and category for the new teacher
                    course_data = add_course_and_category_to_online_exam_db(username=payload.username)
                    
                    if course_data:
                        # Setup default filters and objectives for the new course
                        setup_course_defaults(
                            course_id=course_data["course_id"],
                            category_id=course_data["category_id"],
                            course_name=course_data["course_name"],
                            username=payload.username
                        )

                        # Now, create the teacher link
                        teacher_link_id = add_teacher_link(
                            teacher_id=employee_data["teacherId"],
                            course_id=course_data["course_id"],
                            class_id=employee_data["classId"],
                            faculty_id=employee_data["facultyId"],
                            major_id=employee_data["majorId"]
                        )

                        if teacher_link_id:
                            # Add to studentstatus table for the new teacher
                            add_student_status_to_online_exam_db(
                                username=payload.username,
                                class_id=employee_data["classId"],
                                faculty_id=employee_data["facultyId"],
                                major_id=employee_data["majorId"],
                                teacher_link_id=teacher_link_id,
                                role=payload.role
                            )
                        else:
                            logging.error(f"Teacher link creation failed for '{payload.username}', so student status was not added.")
                    else:
                        logging.error(f"Course/category creation failed for teacher '{payload.username}', so teacher link was not created.")
                else:
                    logging.error(f"Employee creation failed for '{payload.username}', so course/category and teacher link were not created.")

            except Exception as e:
                logging.error(f"An exception occurred during teacher registration post-processing for '{payload.username}': {e}")
                # Log the error but don't prevent primary registration from completing
            
        
        # Get the newly created user using the ID returned by create_user
        created_user = get_user_by_id(created_user_id, tenant_id=tenant_id, conn=db)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")

        if schooldemo12_user_id:
            logging.debug(f"DEBUG: Before update_user_schooldemo12_id. created_user: {created_user}, schooldemo12_user_id: {schooldemo12_user_id}")
            # Pass the connection and cursor to update_user_schooldemo12_id
            update_user_schooldemo12_id(created_user['id'], schooldemo12_user_id, conn=db)

        logging.debug("DEBUG: Just before final db.commit().")
        # --- CRITICAL FIX: Close cursor BEFORE commit ---
        if cur: # Ensure cur exists before trying to close
            cur.close()
        # --- END CRITICAL FIX ---
        try:
            db.commit() # Commit all changes at the very end of the successful transaction
            logging.debug("DEBUG: After final db.commit().")
        except Exception as commit_e:
            db.rollback() # Rollback if commit fails
            logging.exception(f"FATAL EXCEPTION during final db.commit() in register_user")
            raise HTTPException(status_code=500, detail=f"Database commit failed: {commit_e}")

        logging.debug("DEBUG: Just before returning from register_user.")
        
        return {"id": created_user["id"], "username": created_user["username"], "tenant_id": tenant_id}
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        logging.exception(f"FATAL EXCEPTION in register_user (outer block)") # Differentiate this log
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the cursor is closed
        if cur: # Added check if cursor exists, defensive programming
            try:
                cur.close()
            except Exception as e:
                logging.error(f"Error closing cursor in register_user finally block: {e}")


class QuestionRequest(BaseModel):
    topic_context: str
    question_type: Optional[str] = None # Make optional
    difficulty_level: Optional[str] = None # Make optional # Now corresponds to name in difficulty_levels table
    country: str
    audience_type: str
    uploaded_file_id: Optional[int] = None # NEW FIELD
    # Dynamic fields based on audience_type
    school_type: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None
    major: Optional[str] = None
    course: Optional[str] = None
    material: Optional[str] = None
    semester: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    learning_outcome: Optional[str] = None # Now corresponds to name in learning_outcomes table
    cognitive_level: Optional[str] = None # Now corresponds to name in cognitive_levels table
    num_questions: int
    model_api_name: str
    similarity_threshold: Optional[float] = None # For 'both' method
    hide_answers: Optional[bool] = False # NEW FIELD for hiding answers in generated exam
    lang: Optional[str] = None # NEW FIELD: Language for generation

class QuestionResponse(BaseModel):
    question_id: Optional[int] = None
    author_creator: Optional[str] = None
    date_created: Optional[str] = None # Will be set by backend
    question_text: str
    choice_1: Optional[str] = None
    choice_2: Optional[str] = None
    choice_3: Optional[str] = None
    choice_4: Optional[str] = None
    correct_option: Optional[str] = None
    difficulty_level: Optional[str]
    cognitive_level: Optional[str]
    learning_outcome: Optional[str]
    question_type: Optional[str]
    school_type: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None
    major: Optional[str] = None
    course: Optional[str] = None
    material: Optional[str] = None
    semester: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    audience_type: Optional[str] = None # Added audience_type
    mark: Optional[int] = None
    time_seconds: Optional[int] = None
    discriminating_factor: Optional[float] = None
    status: Optional[str] = "pending" # Added status field
    variables: Optional[dict] = None
    solution: Optional[str] = None
    answers_hidden: Optional[bool] = False # NEW FIELD to indicate if answers are hidden for exam


class QuestionUpdateRequest(BaseModel):
    question_text: Optional[str] = None
    choice_1: Optional[str] = None
    choice_2: Optional[str] = None
    choice_3: Optional[str] = None
    choice_4: Optional[str] = None
    correct_option: Optional[str] = None
    difficulty_level: Optional[str] = None
    cognitive_level: Optional[str] = None
    learning_outcome: Optional[str] = None
    question_type: Optional[str] = None
    school_type: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None
    major: Optional[str] = None
    course: Optional[str] = None
    material: Optional[str] = None
    semester: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    job_role: Optional[str] = None
    mark: Optional[int] = None
    time_seconds: Optional[int] = None
    discriminating_factor: Optional[float] = None
    status: Optional[str] = None # Added status field
    variables: Optional[dict] = None

class ExamCreateRequest(BaseModel):
    name: str
    courseId: int
    categoryId: int
    teacherId: int
    duration: int
    total_marks: float
    pass_mark: float
    exam_date: str # Assuming datetime string "YYYY-MM-DD HH:MM:SS"
    status: int = 1 # Default to active
    instructions: str
    settings: Dict[str, Any] # The JSON settings object
    questions: List[Dict[str, Any]] # List of questions for examdata

class GenerationModel(BaseModel):
    id: int
    model_name: str
    model_api_name: str

class PaginatedQuestionsResponse(BaseModel):
    total_count: int
    questions: List[QuestionResponse]


class GenerationTask(BaseModel):
    task_id: Optional[int] = None
    user_id: int
    timestamp: str
    request_parameters: str
    num_questions_requested: int
    num_questions_generated: int
    status: str
    uploaded_file_name: Optional[str] = None
    generated_question_ids: Optional[List[int]] = None # NEW FIELD

class GenerationTaskUpdate(BaseModel):
    status: str

class QuestionStatusUpdate(BaseModel):
    status: str

def _parse_json_to_questions(json_data: List[Dict[str, Any]], request: QuestionRequest, hide_answers: bool) -> List[QuestionResponse]:
    questions = []
    for item in json_data:
        # Handle variations in field names
        q_text = item.get("question_text") or item.get("question") or ""
        choices_raw = item.get("choices", [None, None, None, None])
        
        # Robustly handle choices if they are not a list
        if isinstance(choices_raw, list):
            choices = choices_raw
        elif isinstance(choices_raw, dict):
            # Sort by key (A, B, C, D) and get values
            choices = [choices_raw.get(k) for k in sorted(choices_raw.keys())[:4]]
        else:
            choices = [None, None, None, None]
            
        correct = item.get("correct_option") or item.get("answer") or ""
        sol = item.get("solution") or ""
        
        # --- Map null strings to None ---
        _difficulty = request.difficulty_level if request.difficulty_level != 'null' else None
        _cognitive = request.cognitive_level if request.cognitive_level != 'null' else None
        _learning = request.learning_outcome if request.learning_outcome != 'null' else None
        
        # Prefer question_type from AI if present
        parsed_qtype = item.get("question_type") or item.get("type")
        if parsed_qtype and isinstance(parsed_qtype, str) and parsed_qtype.lower() != 'null':
            _qtype = parsed_qtype.strip()
        else:
            _qtype = request.question_type if request.question_type != 'null' else None

        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        if _qtype == "text":
            choices = [] # Ensure choices is empty for text type
        
        questions.append(QuestionResponse(
            question_text=str(q_text).strip(),
            choice_1=choices[0] if len(choices) > 0 else None,
            choice_2=choices[1] if len(choices) > 1 else None,
            choice_3=choices[2] if len(choices) > 2 else None,
            choice_4=choices[3] if len(choices) > 3 else None,
            correct_option=str(correct).strip(),
            solution=str(sol).strip(),
            difficulty_level=_difficulty,
            cognitive_level=_cognitive,
            learning_outcome=_learning,
            question_type=_qtype,
            audience_type=request.audience_type,
            author_creator="TDM-AI-Engin",
            date_created=str(datetime.now(timezone.utc).date()),
            mark=5,
            time_seconds=120,
            answers_hidden=hide_answers
        ))
    return questions

def parse_gemini_questions_output_old_text_parser(gemini_text: str, request: QuestionRequest, hide_answers: bool) -> List[QuestionResponse]:
    questions = []
    current_question_data = {}
    state = "LOOKING_FOR_QUESTION"  # States: LOOKING_FOR_QUESTION, IN_QUESTION_TEXT, IN_CHOICES_SECTION, IN_CHOICE_TEXT, IN_CORRECT_ANSWER, IN_SOLUTION
    choices_map = { "A": 0, "B": 1, "C": 2, "D": 3 } # To map choice letter to index

    # Normalize question type once
    qtype = (request.question_type or "").lower().replace("_", " ").strip()

    lines = gemini_text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # Remove markdown bolding for easier matching
        clean_line = line.replace('*', '').strip()

        # Skip empty lines, unless we are actively accumulating multi-line content
        if not line and state not in ["IN_QUESTION_TEXT", "IN_CHOICE_TEXT", "IN_CORRECT_ANSWER", "IN_SOLUTION"]:
            continue

        # Detect start of a new question
        if re.match(r"Question \d+:", clean_line) or clean_line.startswith("Question:"):
            if current_question_data.get("question_text"): # Save previous question
                final_correct_option = current_question_data.get("correct_option", "").strip()
                
                # --- FIX: Improved handling for multiple_answer and chbox types ---
                qtype_lower = qtype # use normalized qtype from earlier
                # The existing logic for concatenating lines for correct_option should already handle multi-character answers like "AB"
                # if they appear on a single line. This block ensures we don't inadvertently alter it or
                # rely on a default if the AI provided a multi-character answer.
                if not final_correct_option and "dummy" in (request.model_api_name or "").lower():
                    # If the AI didn't provide an answer and it's a dummy model, assign a default
                    final_correct_option = "A" if "multiple" in qtype_lower else "Dummy Answer"
                
                _difficulty = request.difficulty_level if request.difficulty_level != 'null' else None
                _cognitive = request.cognitive_level if request.cognitive_level != 'null' else None
                _learning = request.learning_outcome if request.learning_outcome != 'null' else None
                _qtype = request.question_type if request.question_type != 'null' else None

                questions.append(QuestionResponse(
                    question_text=current_question_data["question_text"].strip(),
                    choice_1=current_question_data["choices"][0],
                    choice_2=current_question_data["choices"][1],
                    choice_3=current_question_data["choices"][2],
                    choice_4=current_question_data["choices"][3],
                    correct_option=final_correct_option, # This should now correctly capture "AB" if AI provides it
                    solution=current_question_data.get("solution", "").strip(),
                    difficulty_level=_difficulty,
                    cognitive_level=_cognitive,
                    learning_outcome=_learning,
                    question_type=_qtype,
                    audience_type=request.audience_type,
                    author_creator="TDM-AI-Engin",
                    date_created=str(datetime.now(timezone.utc).date()),
                    mark=5,
                    time_seconds=120,
                    answers_hidden=hide_answers
                ))
            
            current_question_data = {"choices": [None, None, None, None], "question_text": ""}
            match_numbered_q = re.match(r"Question \d+:\s*(.*)", clean_line)
            match_unnum_q = re.match(r"Question:\s*(.*)", clean_line)

            if match_numbered_q and match_numbered_q.group(1):
                current_question_data["question_text"] = match_numbered_q.group(1).strip()
                state = "IN_QUESTION_TEXT"
            elif match_unnum_q and match_unnum_q.group(1):
                current_question_data["question_text"] = match_unnum_q.group(1).strip()
                state = "IN_QUESTION_TEXT"
            else:
                state = "IN_QUESTION_TEXT"
            continue

        if state == "IN_QUESTION_TEXT":
            is_choices_start = ("Choices:" in clean_line) or (re.match(r"[A-D]\.\s*", clean_line))
            types_with_choices = ["multiple", "yes no", "accept reject", "multiple answer", "yn", "ar", "chbox"]
            should_have_choices = any(t in qtype for t in types_with_choices)

            if is_choices_start and should_have_choices:
                state = "IN_CHOICES_SECTION"
            elif "Model Answer:" in clean_line or "Correct Answer:" in clean_line:
                label = "Model Answer:" if "Model Answer:" in clean_line else "Correct Answer:"
                current_question_data["correct_option"] = clean_line.replace(label, "").strip()
                # For open-ended/fill-in-the-blank, model answer is also the solution
                if "open" in qtype or "text" in qtype or "blank" in qtype:
                    current_question_data["solution"] = current_question_data["correct_option"]
                state = "IN_CORRECT_ANSWER"
            elif "Solution:" in clean_line:
                current_question_data["solution"] = clean_line.replace("Solution:", "").strip()
                state = "IN_SOLUTION"
            elif line:
                if not current_question_data["question_text"]:
                     current_question_data["question_text"] = line
                else:
                    current_question_data["question_text"] += " " + line

        if state == "IN_CHOICES_SECTION":
            match_start = re.match(r"([A-D])\.\s*(.*)", clean_line)
            if match_start:
                choice_letter = match_start.group(1)
                choice_text = re.sub(r'^(Choice|Answer|\?\?\?\?\?\?|\?\?\?\?\?\?|\?\?\?\?\?)\s*', '', match_start.group(2).strip(), flags=re.IGNORECASE).strip()
                if choice_letter in choices_map:
                    current_question_data["choices"][choices_map[choice_letter]] = choice_text
                state = "IN_CHOICE_TEXT"
            elif "Correct Answer:" in clean_line:
                current_question_data["correct_option"] = clean_line.replace("Correct Answer:", "").strip()
                state = "IN_CORRECT_ANSWER"
            elif "Solution:" in clean_line:
                current_question_data["solution"] = clean_line.replace("Solution:", "").strip()
                state = "IN_SOLUTION"

        elif state == "IN_CHOICE_TEXT":
            if re.match(r"([A-D])\.\s*(.*)", clean_line):
                # Handle next choice immediately
                match_start = re.match(r"([A-D])\.\s*(.*)", clean_line)
                choice_letter = match_start.group(1)
                choice_text = re.sub(r'^(Choice|Answer|\?\?\?\?\?\?|\?\?\?\?\?\?|\?\?\?\?\?)\s*', '', match_start.group(2).strip(), flags=re.IGNORECASE).strip()
                if choice_letter in choices_map:
                    current_question_data["choices"][choices_map[choice_letter]] = choice_text
            elif "Correct Answer:" in clean_line:
                current_question_data["correct_option"] = clean_line.replace("Correct Answer:", "").strip()
                state = "IN_CORRECT_ANSWER"
            elif "Solution:" in clean_line:
                current_question_data["solution"] = clean_line.replace("Solution:", "").strip()
                state = "IN_SOLUTION"
            elif line:
                 # Append to the last choice
                 last_choice_idx = -1
                 for idx, val in enumerate(current_question_data["choices"]):
                     if val is not None: last_choice_idx = idx
                 if last_choice_idx != -1:
                     current_question_data["choices"][last_choice_idx] += " " + line

        elif state == "IN_CORRECT_ANSWER":
            if "Solution:" in clean_line:
                current_question_data["solution"] = clean_line.replace("Solution:", "").strip()
                state = "IN_SOLUTION"
            elif line:
                current_question_data["correct_option"] += " " + line

        elif state == "IN_SOLUTION":
            if line:
                current_question_data["solution"] += " " + line

    if current_question_data.get("question_text"):
        final_correct_option = current_question_data.get("correct_option", "").strip()
        # --- FIX: Ensure correct_option is captured correctly, especially for multiple answers ---
        # The logic here is to ensure that if the AI provides multiple correct options (like "AB"),
        # it's captured as such. The text parser already concatenates lines for correct_option, so it should capture "AB" if AI outputs it on one line.
        # For now, we ensure that if AI provides a non-empty correct_option for multiple types, we trust it.
        if not final_correct_option and "dummy" in (request.model_api_name or "").lower():
            # If the AI didn't provide an answer and it's a dummy model, assign a default
            final_correct_option = "A" if "multiple" in qtype else "Dummy Answer"
        
        _difficulty = request.difficulty_level if request.difficulty_level != 'null' else None
        _cognitive = request.cognitive_level if request.cognitive_level != 'null' else None
        _learning = request.learning_outcome if request.learning_outcome != 'null' else None
        _qtype = request.question_type if request.question_type != 'null' else None

        questions.append(QuestionResponse(
            question_text=current_question_data["question_text"].strip(),
            choice_1=current_question_data["choices"][0],
            choice_2=current_question_data["choices"][1],
            choice_3=current_question_data["choices"][2],
            choice_4=current_question_data["choices"][3],
            correct_option=final_correct_option, # This should now correctly capture "AB" if AI provides it
            solution=current_question_data.get("solution", "").strip(),
            difficulty_level=_difficulty,
            cognitive_level=_cognitive,
            learning_outcome=_learning,
            question_type=_qtype,
            audience_type=request.audience_type,
            author_creator="TDM-AI-Engin",
            date_created=str(datetime.now(timezone.utc).date()),
            mark=5,
            time_seconds=120,
            answers_hidden=hide_answers
        ))
    return questions
# Removed from the original code to avoid confusion, focus on the text parser fix.
# def parse_gemini_questions_output(gemini_text: str, request: QuestionRequest, hide_answers: bool) -> List[QuestionResponse]:
#     # --- NEW: Attempt JSON parsing first ---
#     try:
#         # Strip potential markdown formatting if present
#         json_str = gemini_text.strip()
#         if json_str.startswith("```json"):
#             json_str = json_str[7:]
#         if json_str.endswith("```"):
#             json_str = json_str[:-3]
#         
#         # Use strict=False to allow literal control characters like newlines in strings
#         try:
#             parsed_json = json.loads(json_str, strict=False)
#             if isinstance(parsed_json, list) and parsed_json:
#                 return _parse_json_to_questions(parsed_json, request, hide_answers)
#             elif isinstance(parsed_json, dict):
#                 # If AI returned a single object instead of a list
#                 return _parse_json_to_questions([parsed_json], request, hide_answers)
#             else:
#                 logging.warning(f"Parsed JSON is not a non-empty list. Falling back to text parser.")
#         except json.JSONDecodeError as e:
#             logging.warning(f"JSONDecodeError encountered: {e}. Attempting to clean and re-parse.")
#             
#             # Aggressive Cleaning:
#             # 1. Escape backslashes that are not valid JSON escape sequences
#             cleaned = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', json_str)
#             # 2. Fix potential unescaped double quotes inside strings (best-effort)
#             # This is tricky, but common in AI output like "text": "He said "Hello""
#             # Here we just try to allow strict=False to handle some issues, 
#             # but for truly broken quotes, we'd need more complex logic.
#             
#             try:
#                 parsed_json = json.loads(cleaned, strict=False)
#                 if isinstance(parsed_json, (list, dict)):
#                     logging.info("Successfully parsed JSON after cleaning.")
#                     return _parse_json_to_questions(parsed_json if isinstance(parsed_json, list) else [parsed_json], request, hide_answers)
#             except Exception as e_cleaned:
#                 logging.error(f"Cleaning failed to parse JSON: {e_cleaned}")
#     except Exception as e:
#         logging.info(f"JSON parsing failed or not applicable, falling back to text parser: {e}")
# 
#     # Fallback to legacy text parser
#     return parse_gemini_questions_output_old_text_parser(gemini_text, request, hide_answers)

def parse_gemini_questions_output(gemini_text: str, request: QuestionRequest, hide_answers: bool) -> List[QuestionResponse]:
    # --- NEW: Attempt JSON parsing first ---
    try:
        # Strip potential markdown formatting if present
        json_str = gemini_text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        # Use strict=False to allow literal control characters like newlines in strings
        try:
            parsed_json = json.loads(json_str, strict=False)
            if isinstance(parsed_json, list) and parsed_json:
                return _parse_json_to_questions(parsed_json, request, hide_answers)
            elif isinstance(parsed_json, dict):
                # If AI returned a single object instead of a list
                return _parse_json_to_questions([parsed_json], request, hide_answers)
            else:
                logging.warning(f"Parsed JSON is not a non-empty list. Falling back to text parser.")
        except json.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError encountered: {e}. Attempting to clean and re-parse.")
            
            # Aggressive Cleaning:
            # 1. Escape backslashes that are not valid JSON escape sequences
            cleaned = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', json_str)
            # 2. Fix potential unescaped double quotes inside strings (best-effort)
            # This is tricky, but common in AI output like "text": "He said "Hello""
            # Here we just try to allow strict=False to handle some issues, 
            # but for truly broken quotes, we'd need more complex logic.
            
            try:
                parsed_json = json.loads(cleaned, strict=False)
                if isinstance(parsed_json, (list, dict)):
                    logging.info("Successfully parsed JSON after cleaning.")
                    return _parse_json_to_questions(parsed_json if isinstance(parsed_json, list) else [parsed_json], request, hide_answers)
            except Exception as e_cleaned:
                logging.error(f"Cleaning failed to parse JSON: {e_cleaned}")
    except Exception as e:
        logging.info(f"JSON parsing failed or not applicable, falling back to text parser: {e}")

    # Fallback to legacy text parser
    return parse_gemini_questions_output_old_text_parser(gemini_text, request, hide_answers)


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0: # Handle case where both sets are empty
        return 1.0
    return intersection / union

def perform_google_search(query: str, num_results: int = 10):
    return [{"link": "https://www.google.com"}]

def fetch_page_content(link: str):
    return "dummy content"

def generate_questions_with_openai(request: QuestionRequest, user_id: int):
    # Build a strict, parser-friendly prompt that matches parse_gemini_questions_output expectations
    base = []
    base.append(f"Generate {request.num_questions} {request.question_type} questions.")
    base.append("Output ONLY in this exact format; do not add extra text:")
    base.append("\nQuestion 1:\nChoices:\nA. ...\nB. ...\nC. ...\nD. ...\nCorrect Answer: A\n")
    base.append("Question 2:\nChoices:\nA. ...\nB. ...\nC. ...\nD. ...\nCorrect Answer: B\n")

    base.append("\nConstraints:")
    base.append(f"- Topic Context: {request.topic_context}")
    base.append(f"- Difficulty Level: {request.difficulty_level}")
    if request.cognitive_level:
        base.append(f"- Cognitive Level: {request.cognitive_level}")
    if request.learning_outcome:
        base.append(f"- Learning Outcome: {request.learning_outcome}")
    if request.audience_type:
        base.append(f"- Audience Type: {request.audience_type}")
    # audience-specific hints (best-effort)
    for name in [
        ("school_type", request.school_type), ("subject", request.subject), ("year", request.year),
        ("major", request.major), ("course", request.course), ("material", request.material), ("semester", request.semester),
        ("company", request.company), ("department", request.department), ("job_role", request.job_role),
    ]:
        if name[1]:
            base.append(f"- {name[0].replace('_',' ').title()}: {name[1]}")

    if request.lang:
        lang_name = "Arabic" if request.lang.lower() == "ar" else "English"
        base.append(f"- Language: {lang_name}")
    
    base.append("\nRules:")
    base.append("- Provide exactly 4 choices (A-D) for 'multiple choice', 'yes_no', 'accept_reject', and 'text' (fill-in-the-blank) types.")
    if request.lang and request.lang.lower() == "ar":
        base.append("- For 'yes_no' in Arabic, use exactly [\"???\", \"??\"].")
        base.append("- For 'accept_reject' in Arabic, use exactly [\"?????\", \"????\"].")
    else:
        base.append("- For 'yes_no' in English, use exactly [\"Yes\", \"No\"].")
        base.append("- For 'accept_reject' in English, use exactly [\"Accept\", \"Reject\"].")
    
    base.append("- For 'text' (fill-in-the-blank), ensure the question_text includes a '_______' placeholder.")
    base.append("- For 'multiple_answer', provide exactly two correct letters (e.g., 'Correct Answer: AB').")
    base.append("- For all other types except 'multiple_answer', ensure exactly one correct answer is marked under 'Correct Answer:' (e.g., 'Correct Answer: A').")
    base.append("- Do not include any commentary or JSON.")

    prompt = "\n".join(base)
    try:
        return call_openai_chat(prompt)
    except Exception as e:
        # Surface minimal information; main flow will handle empty parse and warn user
        logging.error(f"OpenAI generation failed: {e}")
        return ""

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):

    user = get_user(username=form_data.username)



    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-AUTHENTICATE": "Bearer"},
        )

    if not verify_password(form_data.password, user["password"]):
    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-AUTHENTICATE": "Bearer"},
        )


    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "is_admin": user["is_admin"],
            "is_super_admin": user["is_super_admin"], # Directly use the value from sqlite3.Row
            "tenant_id": user["tenant_id"],
        },
        expires_delta=access_token_expires,
        audience_type=user["audience_type"] # Pass audience_type
    )
    # This is the correct return statement for the login_for_access_token function
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": user["is_admin"],
        "is_super_admin": user["is_super_admin"], # Directly use the value from sqlite3.Row
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "tenant_id": user["tenant_id"],
        "name": user["full_name"] if "full_name" in user.keys() else user["username"],
        "username": user["username"],
    }
@app.get("/models") # Removed response_model=List[GenerationModel] for now, as it will return a dict
async def get_models(current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 100): # Added skip and limit
    is_super_admin = current_user.get("is_super_admin", False)
    total_count: int
    models: List[Dict[str, Any]]

    if is_super_admin:
        # Super-admins can see all models across all tenants
        total_count, models = get_all_generation_models(tenant_id=None, skip=skip, limit=limit) # Pass skip and limit
    else:
        # Regular users and admins only see models for their tenant or global models (tenant_id IS NULL)
        total_count, models = get_all_generation_models(tenant_id=current_user["tenant_id"], skip=skip, limit=limit) # Pass skip and limit
    
    return {"total_count": total_count, "models": models} # Return a dict with total_count and models

def _perform_billing_operations(get_db_connection_func: Callable[[], sqlite3.Connection], current_user: User, request: QuestionRequest, model: dict, task_id: int, questions_generated: int):
    conn = get_db_connection_func()

    try:
        cursor = conn.cursor()

        # 1. Check balance


        cursor.execute(
            "SELECT balance FROM billing_user_question_balances WHERE user_id = ? AND audience_type = ?",
            (current_user["id"], request.audience_type)
        )
        balance_row = cursor.fetchone()

        balance = balance_row["balance"] if balance_row else 0

        if balance < request.num_questions:

            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient question balance for '{request.audience_type}' audience. You have {balance}, but need {request.num_questions}."
            )
    finally:
        conn.close()

    # --- Deduct from balance and log event ---

    cursor.execute(
        """INSERT INTO billing_events (tenant_id, user_id, task_id, model, questions_debited, event_type, total_price_cents, currency, audience_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """,
        (current_user["tenant_id"], current_user["id"], task_id, model["model_api_name"], questions_generated, 'debit', 0, 'USD', request.audience_type)
    )

    db.commit()


    # Decrement balance

    cursor.execute(
        "UPDATE billing_user_question_balances SET balance = balance - ? WHERE user_id = ? AND audience_type = ?",
        (questions_generated, current_user["id"], request.audience_type)
    )
    db.commit()

@app.post("/generate", response_model=List[QuestionResponse])
async def generate_questions(request: QuestionRequest, current_user: User = Depends(get_current_user)):
    t_total_start = time.perf_counter() # Start total timer
    # Removed manual connection management to prevent database locking during AI generation.
    # Helper functions (insert_generation_task, insert_question) handle their own connections.
    
    task_id = None # Initialize task_id

    is_dummy_model = "dummy" in request.model_api_name.lower()

    model = None
    if not is_dummy_model: # Only check balance and get model for non-dummy models
        # 1. Check user balance
        logging.debug(f"Checking user balance for user_id={current_user['id']}, audience_type={request.audience_type}")
        user_balance = await get_user_question_balance(current_user["id"], request.audience_type)

        # Re-enabling balance check
        if user_balance < request.num_questions:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient question balance for '{request.audience_type}' audience. You have {user_balance}, but need {request.num_questions}."
            )

        # Get the model from the database
        t_model_start = time.perf_counter()
        model = get_generation_model_by_api_name(request.model_api_name, None)
        logging.info(f"TIMING: Model lookup took {int((time.perf_counter() - t_model_start)*1000)} ms")
        if not model:
            raise HTTPException(status_code=404, detail=f"Model '{request.model_api_name}' not found.")
        
        # list_available_gemini_models() # REMOVED: This is a slow network call
    else: # For dummy models, create a dummy model object
        model = {"model_api_name": "dummy", "model_name": "Dummy Generator"}

    try:
        # Record a generation task as queued/in_progress
        t_task_start = time.perf_counter()
        task_id = insert_generation_task(
            user_id=current_user["id"],
            request_parameters=request.json(),
            num_questions_requested=request.num_questions,
            num_questions_generated=0,
            status='queued',
            tenant_id=current_user["tenant_id"]
        )
        logging.info(f"TIMING: Task insertion took {int((time.perf_counter() - t_task_start)*1000)} ms")

        # Retrieve uploaded file content if an ID is provided
        uploaded_file_content = ""
        if request.uploaded_file_id:
            t_file_start = time.perf_counter()
            # Reuse already extracted content from DB instead of re-parsing the file
            uploaded_file_content = get_uploaded_file_content(request.uploaded_file_id)
            logging.info(f"TIMING: File text retrieval from DB took {int((time.perf_counter() - t_file_start)*1000)} ms")
            if not uploaded_file_content:
                # If content is missing, we could try to re-extract, but for speed, we assume it exists
                logging.warning(f"No extracted content found in DB for file_id: {request.uploaded_file_id}")
        
        # Combine topic context and uploaded file content
        generation_context = request.topic_context
        if uploaded_file_content:
            # Smart truncation: 10k chars is plenty for most tasks and keeps AI fast
            context_snippet = uploaded_file_content[:10000]
            generation_context = f"{generation_context}\n\n--- Document Context ---\n{context_snippet}"
            logging.info(f"Context prepared. Length: {len(generation_context)} chars.")
        
        name_lc = model['model_api_name'].lower()
        gemini_output = ""
        t_ai_start = time.perf_counter()
        
        if "dummy" in name_lc:
            items = []
            q_type_lc = (request.question_type or "").lower()
            for i in range(1, max(1, int(request.num_questions)) + 1):
                qt = f"[Dummy] Q{i}: Based on: {generation_context[:60]}..."
                if "multiple choice" in q_type_lc or "mch" in q_type_lc:
                    items.append(f"Question {i}: {qt}\nChoices:\nA. {i}A\nB. {i}B\nC. {i}C\nD. {i}D\nCorrect Answer: A\nSolution: This is a dummy step-by-step solution.\n")
                elif "yes_no" in q_type_lc or "yes no" in q_type_lc or "yn" in q_type_lc:
                    items.append(f"Question {i}: {qt}\nChoices:\nA. Yes\nB. No\nCorrect Answer: A\nSolution: This is a dummy step-by-step solution.\n")
                elif "accept_reject" in q_type_lc or "accept reject" in q_type_lc or "ar" in q_type_lc:
                    items.append(f"Question {i}: {qt}\nChoices:\nA. Accept\nB. Reject\nCorrect Answer: A\nSolution: This is a dummy step-by-step solution.\n")
                elif "multiple_answer" in q_type_lc or "multi answer" in q_type_lc or "chbox" in q_type_lc:
                    items.append(f"Question {i}: {qt}\nChoices:\nA. {i}A\nB. {i}B\nC. {i}C\nD. {i}D\nCorrect Answer: AB\nSolution: This is a dummy step-by-step solution.\n")
                elif "text" in q_type_lc:
                    items.append(f"Question {i}: {qt}\nChoices:\nA. Paris\nB. Berlin\nC. Madrid\nD. Rome\nCorrect Answer: A\nSolution: This is a dummy step-by-step solution for fill-in-the-blank, where 'Paris' is the correct answer.\n")
                else:
                    items.append(f"Question {i}: {qt}\nModel Answer: This is a dummy answer {i}.\nCorrect Answer: Dummy Answer.\n")
            gemini_output = "\n".join(items)

        elif ("gemini" in name_lc) or ("google" in name_lc):
            api_key = model['api_key'] if 'api_key' in model else os.getenv('GOOGLE_API_KEY')
            # Use models/ prefix as required by the library
            raw_model_name = model['model_api_name']
            gemini_model_name = f"models/{raw_model_name}" if not raw_model_name.startswith("models/") else raw_model_name
            # Pass ONLY the context and metadata. gemini_api.py will build the optimized prompt.
            gemini_output = generate_questions_with_gemini(
                topic_context=generation_context,
                question_type=request.question_type,
                difficulty_level=request.difficulty_level,
                cognitive_level=request.cognitive_level,
                learning_outcome=request.learning_outcome,
                num_questions=request.num_questions,
                api_key=api_key,
                model=gemini_model_name,
                lang=request.lang,
                subject=request.subject,
                country=request.country,
                audience_type=request.audience_type,
                school_type=request.school_type,
                year=request.year,
                major=request.major,
                course=request.course,
                material=request.material,
                semester=request.semester,
                company=request.company,
                department=request.department,
                job_role=request.job_role
            )
            if isinstance(gemini_output, dict) and "error" in gemini_output:
                raise HTTPException(status_code=500, detail=f"AI Generation Error: {gemini_output['error']}")
        elif "openai" in name_lc:
            api_key = model['api_key'] if 'api_key' in model else os.getenv('OPENAI_API_KEY')
            gemini_output = json.dumps(generate_questions_with_openai(request, current_user["id"], api_key=api_key))

        else:
            raise HTTPException(status_code=400, detail=f"Unknown model_api_name '{model['model_api_name']}'.")

        logging.info(f"TIMING: AI generation call ({model['model_api_name']}) took {int((time.perf_counter() - t_ai_start)*1000)} ms")

        t_parse_start = time.perf_counter()
        parsed_items = parse_gemini_questions_output(gemini_output, request, request.hide_answers)
        logging.info(f"TIMING: Parsing AI output took {int((time.perf_counter() - t_parse_start)*1000)} ms")
        
        if not parsed_items:
            # Raise an error to trigger the 'failed' status in the exception handler
            raise HTTPException(
                status_code=500, 
                detail="AI generated output but it could not be parsed into questions. Please try again or with a different model/context."
            )

        if parsed_items:
            questions_generated_by_ai = len(parsed_items)
            t_deduct_start = time.perf_counter()
            await deduct_from_balance(
                user_id=current_user["id"],
                amount=questions_generated_by_ai,
                tenant_id=current_user["tenant_id"],
                event_type='debit',
                audience_type=request.audience_type,
                model_api_name=model['model_api_name']
            )
            logging.info(f"TIMING: Balance deduction took {int((time.perf_counter() - t_deduct_start)*1000)} ms")

        saved_questions: List[QuestionResponse] = []
        if parsed_items:
            # DEBUG: Print the value of request.hide_answers before inserting questions

            # Attempt to get course and category IDs for the current user (for online exam system integration)
            ids = get_user_course_category_ids(current_user["username"])
            course_id = ids.get("course_id")
            category_id = ids.get("category_id")

            if not course_id or not category_id:
                logging.warning(f"Could not retrieve course/category IDs for user {current_user['username']}. Questions will NOT be banked to the online exam system, but will be saved locally.")
            
            # Prepare audience-specific fields to be merged into each question
            audience_fields = {
                'school_type': request.school_type,
                'subject': request.subject,
                'year': request.year,
                'major': request.major,
                'course': request.course,
                'material': request.material,
                'semester': request.semester,
                'company': request.company,
                'department': request.department,
                'job_role': request.job_role,
                'audience_type': request.audience_type
            }

            for q in parsed_items:
                q_dict = q.dict() if hasattr(q, 'dict') else dict(q)
                if 'question_id' in q_dict:
                    del q_dict['question_id']
                
                # Merge audience fields from the request into the question data
                q_dict.update(audience_fields)
                
                # Insert into the local SQLite database regardless of online exam banking success
                t_insert_start = time.perf_counter()
                inserted_id = insert_question(q_dict, task_id=task_id, user_id=current_user["id"], tenant_id=current_user["tenant_id"], hide_answers=request.hide_answers)
                logging.info(f"TIMING: insert_question for question {inserted_id} took {int((time.perf_counter() - t_insert_start)*1000)} ms")
                # Remove answers_hidden from q_dict if it exists, as it's passed explicitly
                if 'answers_hidden' in q_dict:
                    del q_dict['answers_hidden']
                saved_question = QuestionResponse(question_id=inserted_id, answers_hidden=request.hide_answers, **q_dict)
                saved_questions.append(saved_question)

        t_update_task_start = time.perf_counter()
        update_generation_task_status(task_id, 'completed')
        # NEW: Update the number of questions generated for the task

        update_generation_task_generated_count(task_id, len(saved_questions))
        logging.info(f"TIMING: Task status and generated count update took {int((time.perf_counter() - t_update_task_start)*1000)} ms")

        # NEW: Update the uploaded_files table with the task_id
        if request.uploaded_file_id:
            t_update_file_start = time.perf_counter()
            update_uploaded_file_task_id(file_id=request.uploaded_file_id, task_id=task_id)
            logging.info(f"TIMING: Uploaded file update took {int((time.perf_counter() - t_update_file_start)*1000)} ms")


        logging.info(f"TIMING: Total /generate endpoint processing took {int((time.perf_counter() - t_total_start)*1000)} ms")
        return saved_questions

    except HTTPException as e:
        if task_id is not None:
            update_generation_task_status(task_id, 'failed')
        raise e
    except Exception as e:
        import traceback
        if task_id is not None:
            update_generation_task_status(task_id, 'failed')
        logging.error("Unexpected exception in /generate:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/questions", response_model=PaginatedQuestionsResponse)
async def get_all_questions(
    query: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    approved_by: Optional[int] = None,
    rejected_by: Optional[int] = None,
    edited_by: Optional[int] = None,
    deleted_by: Optional[int] = None,
    task_id: Optional[int] = None, # NEW PARAMETER
    filter_by_task_topic_context: Optional[str] = None, # NEW PARAMETER (from previous task)
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):


    
    is_admin = current_user.get("is_admin", False)
    is_super_admin = current_user.get("is_super_admin", False)

    user_id_filter = None
    tenant_id_filter = None

    # Determine user and tenant scope based on role
    if is_super_admin:
        # Superadmin can see all tenants and filter by any user.
        user_id_filter = user_id
        tenant_id_filter = None
    elif is_admin:
        # Admin can see all questions within their tenant.
        user_id_filter = user_id # Keep user_id_filter as is (can be None or specific user)
        tenant_id_filter = current_user.get("tenant_id") # Scope to admin's tenant 
    else:
        # Regular user is always scoped to their own questions and tenant.
        user_id_filter = current_user.get("id")
        tenant_id_filter = current_user.get("tenant_id")



    total_count = get_total_questions_count(
        query,
        status,
        user_id=user_id_filter,
        tenant_id=tenant_id_filter,
        date_from=date_from,
        date_to=date_to,
        approved_by=approved_by,
        rejected_by=rejected_by,
        edited_by=edited_by,
        deleted_by=deleted_by,
        task_id=task_id, # Pass new parameter
        filter_by_task_topic_context=filter_by_task_topic_context, # Pass new parameter (from previous task)
        audience_type=current_user.get("audience_type") # NEW: Pass current user's audience type
    )
    questions = get_questions(
        query,
        status,
        user_id=user_id_filter,
        tenant_id=tenant_id_filter,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        approved_by=approved_by,
        rejected_by=rejected_by,
        edited_by=edited_by,
        deleted_by=deleted_by,
        task_id=task_id, # Pass new parameter
        filter_by_task_topic_context=filter_by_task_topic_context, # Pass new parameter (from previous task)
        include_correct_answer=True, # Hide correct answer by default
        audience_type=current_user.get("audience_type") # NEW: Pass current user's audience type
    )

    return {"total_count": total_count, "questions": questions}


class QuestionIdsRequest(BaseModel):
    question_ids: List[int]

@app.delete("/questions/batch", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_questions_endpoint(payload: QuestionIdsRequest, current_user: User = Depends(get_current_user)):
    delete_multiple_questions(payload.question_ids, tenant_id=current_user["tenant_id"])
    return

@app.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_question(question_id: int, current_user: User = Depends(get_current_user)):
    delete_question(question_id, actor_user_id=current_user["id"], tenant_id=current_user["tenant_id"])
    return

@app.delete("/exams/{exam_id}", status_code=status.HTTP_200_OK) # Changed status to 200 OK as we are not deleting the resource itself
async def delete_exam_report_endpoint(exam_id: int, current_user: User = Depends(get_current_user)):

    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        success = delete_exam_report(exam_id, current_user['id'])
        if not success:
            logging.warning(f"Failed to delete report for exam_id: {exam_id}. Exam not found or unauthorized.")
            raise HTTPException(status_code=404, detail="Exam not found or unauthorized to delete report.")
        
        logging.info(f"Successfully deleted report for exam_id: {exam_id} by user_id: {current_user['id']}")
        return {"message": "Exam report deleted successfully."}
    except HTTPException as he:
        logging.error(f"HTTPException in /exams/{exam_id} DELETE: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"Unexpected exception in /exams/{exam_id} DELETE: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while deleting exam report: {e}")


@app.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_single_question(question_id: int, question: QuestionUpdateRequest, current_user: User = Depends(get_current_user)):
    print(f"***** PUT REQUEST HIT FOR QUESTION {question_id} *****") # VERY UNIQUE PRINT
    try:
        question_data = question.dict(exclude_unset=True)
        if not question_data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        update_question(question_id, question_data, actor_user_id=current_user["id"], tenant_id=current_user["tenant_id"])
        
        updated_question = get_question_by_id(
            question_id,
            include_correct_answer=True,
            tenant_id=current_user["tenant_id"],
            audience_type=current_user.get("audience_type")
        )
        if not updated_question:
            raise HTTPException(status_code=404, detail="Question not found after update")
        return updated_question
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/questions/{question_id}/status", response_model=QuestionResponse)
async def update_question_status_endpoint(
    question_id: int,
    status_update: QuestionStatusUpdate,
    current_user: User = Depends(get_current_user),
):
    try:
        update_question_status(
            question_id,
            status_update.status,
            actor_user_id=current_user["id"],
            tenant_id=current_user["tenant_id"],
        )
        updated_question = get_question_by_id(
            question_id,
            include_correct_answer=True,
            tenant_id=current_user["tenant_id"],
            audience_type=current_user.get("audience_type")
        )
        if not updated_question:
            raise HTTPException(status_code=404, detail="Question not found after status update")
        return updated_question
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions/{question_id}/history")
async def get_question_history_endpoint(question_id: int, current_user: User = Depends(get_current_user)):

    q = get_question_by_id(
        question_id,
        include_correct_answer=False,
        tenant_id=current_user["tenant_id"],
        audience_type=current_user.get("audience_type")
    )
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    # Enforce tenant scope
    if q.get('tenant_id') is not None and q.get('tenant_id') != current_user["tenant_id"] and not current_user.get("is_super_admin", False):
        raise HTTPException(status_code=403, detail="Forbidden")
    # If not admin, enforce ownership
    if not current_user.get("is_admin", False) and not current_user.get("is_super_admin", False) and q.get('user_id') != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    history = get_question_history(question_id, current_user["tenant_id"])

    return history

@app.post("/questions/{question_id}/reveal_answer")
async def reveal_question_correct_answer(
    question_id: int,
    password_request: PasswordVerifyRequest,
    current_user: User = Depends(get_current_user)
):
    # 1. Authorization: Check if user is admin or super-admin
    is_admin = current_user.get("is_admin", 0)
    is_super_admin = current_user.get("is_super_admin", 0)

    if not (is_admin or is_super_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reveal correct answers.")

    # 2. Authentication: Verify user's password
    # Fetch user details from DB to get the password hash
    db_user = get_user(current_user["username"], tenant_id=current_user["tenant_id"])
    if not db_user or not verify_password(password_request.password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password provided.")

    # 3. Retrieve question with correct answer
    question = get_question_by_id(
        question_id,
        include_correct_answer=True,
        tenant_id=current_user["tenant_id"]
    )
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    
    # 4. Enforce tenant scope for admins (super-admins can see all)
    if is_admin and not is_super_admin:
        if question.get('tenant_id') != current_user["tenant_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view questions from other tenants.")

    correct_option = question.get("correct_option")
    if correct_option is None:
        return {"correct_option": "N/A", "message": "Correct option is not available for this question type or not set."}

    return {"correct_option": correct_option}


@app.post("/questions/{question_id}/solution")
async def get_solution_for_question(question_id: int, current_user: User = Depends(get_current_user)):
    logging.debug(f"get_solution_for_question: Called for question_id={question_id}, user={current_user.get('username')}, tenant={current_user.get('tenant_id')}")
    question = get_question_by_id(
        question_id,
        include_correct_answer=False,
        tenant_id=current_user["tenant_id"]
    )
    logging.debug(f"get_solution_for_question: Retrieved question: {question}")
    if not question:
        logging.warning(f"get_solution_for_question: Question {question_id} not found.")
        raise HTTPException(status_code=404, detail="Question not found")

    # Simple check for tenant access, similar to history endpoint
    if question.get('tenant_id') is not None and question.get('tenant_id') != current_user["tenant_id"]:
        logging.warning(f"get_solution_for_question: Forbidden access to question {question_id} by user from different tenant.")
        raise HTTPException(status_code=403, detail="Forbidden")

    if question.get('solution'):
        logging.debug(f"get_solution_for_question: Solution found for question {question_id}.")
        return {"solution": question['solution']}
    else:
        logging.info(f"get_solution_for_question: No solution found in DB for question {question_id}. Returning default message.")
        # If solution is not in DB, do not attempt to generate it via API
        return {"solution": "Solution not available for this question."}




@app.post("/print/save-pdf")
async def save_printed_exam_pdf(request: Dict[str, Any], current_user: User = Depends(get_current_user)):
    logging.info(f"Received request to /print/save-pdf for user {current_user['username']}")
    try:
        exam_name = request.get("exam_name")
        exam_id = request.get("exam_id")
        question_ids = request.get("question_ids", [])
        filters = request.get("filters") # This will be a dict
        
        if not exam_name:
            raise HTTPException(status_code=400, detail="Exam name is required.")
        if not question_ids:
            raise HTTPException(status_code=400, detail="No question IDs provided for printing.")

        # Convert filters dict to a JSON string for storage
        filters_json = json.dumps(filters)

        inserted_print_id = insert_printed_exam(
            user_id=current_user["id"],
            tenant_id=current_user["tenant_id"],
            exam_name=exam_name,
            exam_id=exam_id,
            question_ids=json.dumps(question_ids), # Store as JSON string
            filters_used=filters_json
        )
        logging.info(f"Print event recorded successfully with ID: {inserted_print_id}")
        return {"message": "Print event recorded successfully.", "print_id": inserted_print_id, "status": "success"}
    except HTTPException as e:
        logging.error(f"HTTPException in /print/save-pdf: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"An unexpected error occurred in /print/save-pdf: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/lookup/school_types", response_model=List[LookupItem])
async def get_school_types(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("school_types", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/school_subjects", response_model=List[LookupItem])
async def get_school_subjects(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("school_subjects", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/school_years", response_model=List[LookupItem])
async def get_school_years(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("school_years", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/question_types", response_model=List[LookupItem])
async def get_question_types(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("question_types", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])

@app.get("/lookup/question_types/{audience_type}", response_model=List[LookupItem])
async def get_question_types_for_audience(
    audience_type: str,
    lang: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if audience_type not in ["school", "university", "company", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    return get_question_types_by_audience(audience_type, lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])

@app.get("/lookup/university_majors", response_model=List[LookupItem])
async def get_university_majors(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("university_majors", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/university_courses", response_model=List[LookupItem])
async def get_university_courses(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("university_courses", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])

@app.get("/lookup/university_materials", response_model=List[LookupItem])
async def get_university_materials(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("university_materials", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])

@app.get("/lookup/university_semesters", response_model=List[LookupItem])
async def get_university_semesters(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("university_semesters", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/universities", response_model=List[str])
async def get_universities():
    return ["Harvard University", "Stanford University", "MIT", "University of California, Berkeley", "Oxford University"]


@app.get("/lookup/companies", response_model=List[LookupItem])
async def get_companies(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("companies", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/departments", response_model=List[LookupItem])
async def get_departments(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("departments", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])


@app.get("/lookup/job_roles", response_model=List[LookupItem])
async def get_job_roles(lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    return get_lookup_data_list("job_roles", lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"])

@app.get("/lookup/audience_fields/{audience_type}")
async def get_audience_fields(audience_type: str):
    if audience_type == "school":
        return {
            "school_type": True,
            "subject": True,
            "year": True,
            "gender": True,
            "major": False,
            "course": False,
            "material": False,
            "semester": False,
            "company": False,
            "department": False,
            "job_role": False,
        }
    elif audience_type == "university":
        return {
            "school_type": False,
            "subject": False,
            "year": False,
            "major": True,
            "course": True,
            "material": True,
            "semester": True,
            "company": False,
            "department": False,
            "job_role": False,
        }
    elif audience_type == "company":
        return {
            "school_type": False,
            "subject": False,
            "year": False,
            "major": False,
            "course": False,
            "material": False,
            "semester": False,
            "company": True,
            "department": True,
            "job_role": True,
        }
    elif audience_type == "vocational":
        return {
            "school_type": False,
            "subject": False,
            "year": False,
            "gender": False,
            "major": False,
            "course": True,
            "material": True,
            "semester": False,
            "company": False,
            "department": True,
            "job_role": True,
        }
    elif audience_type == "community":
        return {
            "school_type": False,
            "subject": True, # Community might have subjects/topics
            "year": False,
            "gender": False,
            "major": False,
            "course": False,
            "material": True, # Community might have learning materials
            "semester": False,
            "company": False,
            "department": True, # Community might be structured with departments
            "job_role": False,
        }
        return {
            "school_type": False,
            "subject": False,
            "year": False,
            "gender": False,
            "major": False,
        "course": False,
            "material": False,
            "semester": False,
            "company": False,
            "department": False,
            "job_role": False,
        }
    elif audience_type == "general":
        return {
            "school_type": False,
            "subject": False,
            "year": False,
            "gender": False,
            "major": False,
            "course": False,
            "material": False,
            "semester": False,
            "company": False,
            "department": False,
            "job_role": False,
            "difficulty_level": True, # Assuming general properties include these
            "cognitive_level": True,
            "learning_outcome": True,
            "question_type": True,
        }


@app.get("/lookup/countries", response_model=List[LookupItem])
async def get_countries(lang: Optional[str] = None):
    return get_lookup_data_list("countries", lang=lang)

@app.get("/lookup/difficulty_levels", response_model=List[LookupItem])
async def get_difficulty_levels(lang: Optional[str] = None, current_user: User = Depends(get_current_user)): # Added current_user dependency
    return get_lookup_data_list("difficulty_levels", lang=lang, tenant_id=current_user["tenant_id"]) # Passed tenant_id

@app.get("/lookup/cognitive_levels", response_model=List[LookupItem])
async def get_cognitive_levels(lang: Optional[str] = None, current_user: User = Depends(get_current_user)): # Added current_user dependency
    return get_lookup_data_list("cognitive_levels", lang=lang, tenant_id=current_user["tenant_id"]) # Passed tenant_id

@app.get("/lookup/learning_outcomes", response_model=List[LookupItem])
async def get_learning_outcomes(
    lang: Optional[str] = None,
    audience_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user) # Added current_user dependency
):
    return get_lookup_data_list("learning_outcomes", lang=lang, audience_type=audience_type, category=category, tenant_id=current_user["tenant_id"]) # Passed tenant_id

@app.get("/lookup/users", response_model=List[UserOut])
async def get_all_users_for_lookup(current_user: User = Depends(get_current_user)):

    is_super_admin = current_user.get("is_super_admin", False)
    is_admin = current_user.get("is_admin", False)



    tenant_scope = None
    if not (is_admin or is_super_admin):
        tenant_scope = current_user.get("tenant_id")
    

    total_users, users_list = get_all_users(tenant_ids=[tenant_scope] if tenant_scope is not None else None)

    processed_users = []
    for user in users_list:
    
        processed_users.append({'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin']), 'full_name': user['full_name'] if 'full_name' in user else user['username']})
    return processed_users


@app.get("/suggestions")
async def get_suggestions(term: str, limit: int = 10):
    return get_search_suggestions(term, limit)

@app.get("/lookup/properties/{property_api_name}", response_model=List[LookupItem])
async def get_dynamic_lookup_properties(property_api_name: str, lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    # A basic security check to prevent arbitrary table name injections
    # This could be improved by checking against the property_types table
    if not re.match(r'^[a-zA-Z0-9_]+$', property_api_name):
        raise HTTPException(status_code=400, detail="Invalid property name format.")
    return get_lookup_data_list(property_api_name, lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"]) # Pass user_id

@app.get("/lookup/property_types/{audience_type}")
async def get_property_types_for_audience(
    audience_type: str,
    lang: Optional[str] = None, # Added lang parameter
    current_user: User = Depends(get_current_user) # Added current_user dependency
):
    if audience_type not in ["school", "university", "company", "general", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    return get_property_types_by_audience(audience_type, lang=lang, tenant_id=current_user["tenant_id"], user_id=current_user["id"]) # Pass user_id

@app.get("/lookup/categories", response_model=List[Dict[str, str]])
async def get_categories_for_audience_endpoint(audience_type: str, current_user: User = Depends(get_current_user)):
    if audience_type not in ["school", "university", "company", "vocational", "community", "general", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    
    tenant_id_to_pass = current_user["tenant_id"]
    if current_user.get("is_super_admin") == 1:
        tenant_id_to_pass = None # Bypass for superadmin
        
    return get_unique_categories_for_audience(audience_type, tenant_id=tenant_id_to_pass, user_id=current_user["id"])

@app.get("/lookup/exam-names-all", response_model=List[LookupItem])
async def get_all_exam_names_endpoint():
    # Fetch exam names from the online-exam system
    exam_names = get_all_exam_names()
    # Map them to LookupItem format if necessary, assuming get_all_exam_names returns [{id:X, name:Y}]
    return [LookupItem(id=item['id'], name=item['name']) for item in exam_names]

@app.get("/lookup/course-filter-values", response_model=List[Dict[str, Any]])
async def get_course_filter_values_endpoint(audience_type: str, lang: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if audience_type not in ["school", "university", "company", "vocational", "community", "general", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    return get_course_filter_options(audience_type, lang=lang, tenant_id=current_user["tenant_id"])


@app.get("/tasks", response_model=List[GenerationTask])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = get_generation_tasks_by_user(current_user["id"])
    return tasks

def write_tamsqb_export_file(
    export_dir: Path,
    course_name: str,
    category_name: str,
    course_id: int,
    category_id: int,
    question_details: List[Dict[str, Any]]
):
    file_name = f"{course_name}.txt"
    file_path = export_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"TamsQB Export for Course: {course_name} (ID: {course_id})\n")
        f.write(f"Category: {category_name} (ID: {category_id})\n")
        f.write("-" * 50 + "\n\n")

        for detail in question_details:
            f.write(f"Local Question ID: {detail['local_question_id']}\n")
            f.write(f"Bank Question ID: {detail['bank_question_id']}\n")
            f.write(f"FilterData Entry:\n")
            for key, value in detail['filterdata'].items():
                f.write(f"  {key}: {value}\n")
            f.write("\n" + "-" * 20 + "\n\n")



@app.post("/tamsqb/setup-course-category")
async def setup_tamsqb_course_category(current_user: User = Depends(get_current_user)):
    # Call the function to add the course and main category
    result = add_course_and_category_to_online_exam_db(current_user["username"])
    
    # If the course and category were created successfully, add the defaults
    if result and result.get("status") == "success":
        course_id = result.get("course_id")
        category_id = result.get("category_id")
        course_name = result.get("course_name")
        if course_id and category_id and course_name:
            setup_course_defaults(course_id, category_id, course_name, current_user["username"])
            
    return result

class ExamPushRequest(BaseModel):
    exam_date_time: Optional[str] = None
    selected_question_ids: Optional[List[int]] = None
    exam_name: Optional[str] = None

@app.post("/tamsqb/push-questions-to-bank")
async def push_questions_to_tamsqb_bank(request: ExamPushRequest, current_user: User = Depends(get_current_user)):


    # Determine the appropriate ID for schooldemo12 interactions
    schooldemo12_entity_id = None
    if current_user.get("audience_type") == "student": # Assuming "student" is the audience type for students
        schooldemo12_entity_id = current_user.get("schooldemo12_user_id")
        if schooldemo12_entity_id is None:
            logging.error(f"User '{current_user['username']}' (questions.db ID: {current_user['id']}) is a student but does not have a schooldemo12_user_id. Cannot push questions to TamsQB bank.")
            raise HTTPException(status_code=400, detail="Student user not fully registered with online-exam system.")
    else: # Assume all other audience types are employees/teachers for TamsQB
        from online_exam_db_connector import get_employee_id_by_email # Deferred import
        schooldemo12_entity_id = get_employee_id_by_email(current_user["email"])
        if schooldemo12_entity_id is None:
            # Fallback if employee not found by email (e.g., system admin, or new teacher not yet synced)

            schooldemo12_entity_id = 11 # Default teacher for employee roles if not found by email
            
    teacher_id = schooldemo12_entity_id # This will be the ID used for all schooldemo12 operations

    latest_teacher_link_id = get_teacher_link_id_by_teacher_id(teacher_id)
    if latest_teacher_link_id is None:
        logging.warning(f"No existing teacherLink found for teacher ID {teacher_id}. A new one will be created with course_id=0.")
        teacher_link_details = None
    else:
        teacher_link_details = get_teacher_link_details(latest_teacher_link_id)
        if not teacher_link_details:
            raise HTTPException(status_code=500, detail=f"Could not retrieve details for teacher_link_id {latest_teacher_link_id}.")
    
    online_exam_conn = None
    try:
        from online_exam_db_connector import get_online_exam_db_connection, add_teacher_link

        online_exam_conn = get_online_exam_db_connection()
        online_exam_cursor = online_exam_conn.cursor()

        current_date_formatted = datetime.now().strftime("%d-%m-%Y")
        setup_result = add_course_and_category_to_online_exam_db(current_user["username"])
        if setup_result.get("status") != "success":
            raise HTTPException(status_code=500, detail=f"Failed to set up TamsQB course/category: {setup_result.get('message', 'Unknown error')}")
        
        course_id = setup_result["course_id"]
        category_id = setup_result["category_id"]
        course_name = setup_result["course_name"]
        course_sequential_number = setup_result["course_sequential_number"]

        if teacher_link_details:
             class_id = teacher_link_details["classId"]
             faculty_id = teacher_link_details["facultyId"]
             major_id = teacher_link_details["majorId"]
        else:
             class_id, faculty_id, major_id = 0, 0, 0

        new_teacher_link_id = add_teacher_link(
            teacher_id=teacher_id,
            course_id=course_id,
            class_id=class_id,
            faculty_id=faculty_id,
            major_id=major_id
        )
        if new_teacher_link_id is None:
            raise HTTPException(status_code=500, detail="Failed to create a new teacherLink for the exam course.")
        
        teacher_link_id = new_teacher_link_id
        
        _add_exam_specific_filters(
            online_exam_conn,
            online_exam_cursor,
            course_id,
            current_user["username"],
            current_date_formatted,
            course_sequential_number
        )
        online_exam_conn.commit()

        export_dir = Path(__file__).resolve().parent / "tamsqb_exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        unbanked_questions = get_unbanked_questions_for_user(
            current_user,
            selected_question_ids=request.selected_question_ids # Pass selected IDs
        )
        
        if not unbanked_questions:
            return {"status": "success", "message": "No new questions to add to TamsQB bank.", "exam_id": None}

        questions_added_count = 0
        exported_question_details = []
        exam_questions_payload = []
        total_exam_marks = 0.0
        questions_to_link = []
        objective_ids_for_exam = {} # NEW: Collect objectives for the exam-wide filters

        for question in unbanked_questions:
            insert_result = insert_question_to_bank(
                question_data=question,
                course_id=course_id,
                category_id=category_id,
                username=current_user["username"],
                teacher_id=teacher_id
            )
            
            if insert_result:
                update_question_tamsqb_bank_added_status(question["question_id"], 1)
                questions_added_count += 1
                
                # NEW: Track objective_id for exam-level filters
                obj_id = insert_result.get("objective_id")
                lo_name = question.get("learning_outcome")
                if obj_id and lo_name:
                    objective_ids_for_exam[str(obj_id)] = lo_name

                questions_to_link.append({
                    "local_id": question["question_id"],
                    "bank_id": insert_result["question_id"]
                })
                
                exported_question_details.append({
                    "local_question_id": question["question_id"],
                    "bank_question_id": insert_result["question_id"],
                    "filterdata": insert_result["filterdata"]
                })

                question_mark = float(question.get("mark") or 5.0)
                question_duration = int(question.get("time_seconds") or 120)

                type_mapping = { 
                    "multiple choice": "mch", "multiple_choice": "mch", "mcq": "mch",
                    "yes no": "yn", "yes_no": "yn", "yn": "yn",
                    "accept reject": "ar", "accept_reject": "ar", "ar": "ar",
                    "multi answer": "chbox", "multiple answer": "chbox", "multiple_answer": "chbox", "chbox": "chbox",
                    "text": "text", "fill in the blank": "text", "fill_in_the_blank": "text",
                    "essay": "open", "open-ended": "open", "open": "open",
                    "hand write": "hw", "hand_write": "hw", "hw": "hw",
                    "matching": "match", "match": "match"
                }
                question_type_raw = (question.get("question_type") or "").lower()
                question_type_for_payload = type_mapping.get(question_type_raw, "mch")

                answers_list_for_payload = []
                
                # NEW: Handle chbox (multiple answer) formatting for online-exam frontend compatibility
                correct_indices_for_marks = []
                if question_type_for_payload == "chbox":
                    raw_correct = question.get("correct_option", "")
                    if isinstance(raw_correct, list):
                        correct_indices_for_marks = [int(x) for x in raw_correct]
                    elif isinstance(raw_correct, str):
                        if raw_correct.isdigit():
                            correct_indices_for_marks = [int(raw_correct)]
                        else:
                            letter_to_idx = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
                            correct_indices_for_marks = [letter_to_idx[l] for l in raw_correct.upper() if l in letter_to_idx]
                    
                    num_correct = len(correct_indices_for_marks)
                    mark_per_ans = question_mark / num_correct if num_correct > 0 else 0

                if question_type_for_payload in ["mch", "chbox", "yn", "ar"]:
                    for i in range(1, 5):
                        choice = question.get(f"choice_{i}")
                        if choice:
                            if question_type_for_payload == "chbox":
                                is_corr = i in correct_indices_for_marks
                                answers_list_for_payload.append({
                                    "text": choice,
                                    "mark": mark_per_ans if is_corr else 0
                                })
                            else:
                                answers_list_for_payload.append(choice)
                elif question_type_for_payload in ["open", "text"]:
                    solution_text = question.get("solution", "")
                    if solution_text:
                        answers_list_for_payload.append(solution_text)
                answers_json_for_payload = json.dumps(answers_list_for_payload, ensure_ascii=False)

                correct_option_for_payload = question.get("correct_option", "")
                if question_type_for_payload in ["mch", "yn", "ar"]:
                    if correct_option_for_payload == "A": correct_option_for_payload = "1"
                    elif correct_option_for_payload == "B": correct_option_for_payload = "2"
                    elif correct_option_for_payload == "C": correct_option_for_payload = "3"
                    elif correct_option_for_payload == "D": correct_option_for_payload = "4"
                elif question_type_for_payload == "chbox":
                    if isinstance(correct_option_for_payload, list):
                        correct_option_for_payload = json.dumps(correct_option_for_payload)
                    else:
                        # Handle multiple letters like "AB" or single letters/digits
                        if isinstance(correct_option_for_payload, str):
                            if correct_option_for_payload.isdigit():
                                correct_option_for_payload = json.dumps([int(correct_option_for_payload)])
                            else:
                                # Map letters to indices
                                letter_to_idx = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
                                indices = [letter_to_idx[l] for l in correct_option_for_payload.upper() if l in letter_to_idx]
                                correct_option_for_payload = json.dumps(indices)
                        else:
                            correct_option_for_payload = json.dumps([])
                elif question_type_for_payload in ["open", "text"]:
                    correct_option_for_payload = question.get("solution", "") or question.get("correct_option", "")

                resources_data_for_payload = question.get("resources", {"question":[],"answers":{}})
                resources_json_for_payload = json.dumps(resources_data_for_payload)

                difficulty_level = question.get("difficulty_level", "medium")
                time_in_minutes = round((question.get("time_seconds", 0) / 60))
                filters_data = { "1": str(question.get("mark", 0)), "2": str(time_in_minutes), "32": str(difficulty_level).lower(), "53": str(current_user['username']), "33": "1" }
                
                # Include Learning Outcome (Type 3) in filters if available
                objective_id = insert_result.get("objective_id")
                learning_outcome_name = question.get("learning_outcome")
                if objective_id and learning_outcome_name:
                    filters_data[str(objective_id)] = learning_outcome_name
                
                filters_for_payload = filters_data

                question_payload_item = { # Store the item in a variable first
                    "bankId": insert_result["question_id"], "question_order": len(exam_questions_payload) + 1, "mark": question_mark, "duration": question_duration,
                    "title": question.get("question_text", ""), "type": question_type_for_payload, "answers": answers_json_for_payload,
                    "correct": correct_option_for_payload, "resources": resources_json_for_payload, "modelId": 0, "filters": filters_for_payload,
                    "learning_outcome": learning_outcome_name,
                    "answers_hidden": question.get("hide_answers", False)
                }
                exam_questions_payload.append(question_payload_item) # Append the variable
                total_exam_marks += question_mark
            else:
                logging.warning(f"Failed to insert question {question['question_id']} into TamsQB bank.")

        if exported_question_details:
            write_tamsqb_export_file(
                export_dir=export_dir, course_name=course_name, category_name=setup_result["message"].split("'")[1],
                course_id=course_id, category_id=category_id, question_details=exported_question_details
            )

        exam_creation_message = "No exam created."
        if exam_questions_payload:
            if request.exam_name:
                exam_name = request.exam_name
            else:
                exam_name = f"Auto-Generated Exam for {current_user['username']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if request.exam_date_time:
                exam_date_str = request.exam_date_time
            else:
                future_time = datetime.now() + timedelta(minutes=1)
                exam_date_str = future_time.strftime("%Y-%m-%d %H:%M:%S")

            default_settings = {
                "view":"1", "timeCalculation":"1", "timeCount":"1", "showExamMark":False, "showQuestionsMark":False, "randomQuestions":False, "randomAnswers":False,
                "showSuccessMark":False, "showStudentEvaluate":False, "showCalculator":False, "scientificCalculator":False, "hideFinishedExam":False, "mathEditor":False,
                "models":1, "logoutOnFinish":True, "requireRes":False, "requireOmr":False, "hasSessions":False,
                "queues":{ "select":[], "random":[{"categorySet":[category_id], "filters":objective_ids_for_exam, "model":0, "questions":[q["bankId"] for q in exam_questions_payload], "limit":len(exam_questions_payload)}], "specTable":[]}
            }
            settings_json_string = json.dumps(default_settings)

            exam_duration_minutes = 30
            exam_request_payload = {
                "name": exam_name, "courseId": course_id, "categoryId": category_id, "teacherId": teacher_id, "duration": exam_duration_minutes,
                "facultyID": faculty_id, "majorID": major_id,
                "totalQ": len(exam_questions_payload), "mark": total_exam_marks, "successMark": round(total_exam_marks * 0.6, 2), "date": exam_date_str,
                "status": "draft", "access": 60, "instructions": "This is an automatically generated exam based on your recently banked questions.",
                "settings": settings_json_string, "questions": exam_questions_payload, "link": [teacher_link_id]
            }

            online_exam_base_url = os.getenv('ONLINE_EXAM_API_BASE_URL', "http://localhost:8888/api").rstrip('/') + '/'
            
            # Generate JWT token for the current user using their schooldemo12 teacher ID
            # This ensures the PHP side correctly identifies them and their rules (like exam-can-publish).
            teacher_jwt_payload = {
                "sub": str(teacher_id), # Use the schooldemo12 entity ID (teacher_id)
                "is_admin": current_user.get("is_admin", 0),
                "is_super_admin": current_user.get("is_super_admin", 0),
                "tenant_id": current_user.get("tenant_id", 1),
            }
            teacher_api_token = create_online_exam_access_token(data=teacher_jwt_payload)
            
            # Create the exam via API call
            create_exam_result = await create_exam_in_online_exam_db(exam_request_payload, current_user["username"], online_exam_base_url, teacher_api_token)

            if create_exam_result.get("status") == "success":
                online_exam_id = create_exam_result.get("exam_id")
                exam_creation_message = f"Exam '{exam_name}' created successfully with ID: {online_exam_id}."
                
                # Store the exam in the local database
                local_exam_id = insert_exam(
                    online_exam_id=online_exam_id,
                    user_id=current_user["id"],
                    exam_name=exam_name,
                    exam_date_time=exam_date_str,
                    duration_minutes=exam_duration_minutes
                )

                # Link the questions to this local exam
                for q_to_link in questions_to_link:
                    link_question_to_exam(
                        exam_id=local_exam_id,
                        question_id=q_to_link["local_id"],
                        bank_question_id=q_to_link["bank_id"]
                    )

                try:
                    teacher_link_details = get_teacher_link_details(teacher_link_id)
                    if teacher_link_details:
                        add_student_status_to_online_exam_db(
                            username=current_user["username"], class_id=teacher_link_details["classId"], faculty_id=teacher_link_details["facultyId"],
                            major_id=teacher_link_details["majorId"], teacher_link_id=teacher_link_id,
                            role=current_user.get("role")
                        )
                except Exception as e:
                    logging.error(f"Failed to add student status for user {current_user['username']}: {e}")

                frontend_base_url_only = os.getenv('ONLINE_EXAM_FRONTEND_BASE_URL', "http://localhost:8888").rstrip('/')
                redirect_url = frontend_base_url_only
                return {
                    "status": "success", "message": exam_creation_message, "exam_id": online_exam_id, "exam_name": exam_name,
                    "exam_date_time": exam_date_str, "exam_total_time": exam_request_payload["duration"], "redirect_url": redirect_url
                }
            else:
                exam_creation_message = f"Failed to create exam: {create_exam_result.get('message', 'Unknown error')}."
                raise HTTPException(status_code=500, detail=exam_creation_message)
        else:
            exam_creation_message = "No questions were added to the bank, so no exam was created."

        final_message = f"Successfully added {questions_added_count} questions to TamsQB bank. {exam_creation_message}"
        return {"status": "success", "message": final_message}

    except HTTPException as e:
        raise e
    except Exception as e:
        if online_exam_conn:
            online_exam_conn.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if online_exam_conn:
            online_exam_conn.close()

@app.post("/tamsqb/create-exam")
async def create_exam_endpoint(exam_request: ExamCreateRequest, current_user: User = Depends(get_current_user)):
    logging.debug(f"Entering /tamsqb/create-exam for user: {current_user['username']}")
    try:
        online_exam_base_url = os.getenv('ONLINE_EXAM_API_BASE_URL', "http://localhost:8888/api")

        # Generate JWT token for the current user
        teacher_jwt_payload = {
            "sub": str(current_user["id"]),
            "is_admin": current_user.get("is_admin", 0),
            "is_super_admin": current_user.get("is_super_admin", 0),
            "tenant_id": current_user.get("tenant_id", 1), # Default tenant_id if not present
        }
        teacher_api_token = create_online_exam_access_token(data=teacher_jwt_payload)

        # Call the function in online_exam_db_connector to create the exam
        # This function will handle sending the POST request to the online-exam system
        create_exam_result = await create_exam_in_online_exam_db(exam_request.dict(), current_user["username"], online_exam_base_url, teacher_api_token)

        if create_exam_result.get("status") == "success":
            return {"status": "success", "message": "Exam created successfully", "exam_id": create_exam_result.get("exam_id")}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create exam: {create_exam_result.get('message', 'Unknown error')}")

    except HTTPException as e:
        logging.error(f"HTTPException in /tamsqb/create-exam: {e.detail}")
        raise e
    except Exception as e:
        import traceback
        logging.error(f"Unexpected exception in /tamsqb/create-exam: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/tamsqb/publish-exam/{exam_id}")
async def publish_exam(exam_id: int, current_user: User = Depends(get_current_user)):
    logging.debug(f"Entering /tamsqb/publish-exam/{exam_id} for user: {current_user['username']}")
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        success = publish_exam_status(exam_id)
        if success:
            logging.debug(f"Exam {exam_id} status updated to 'published' in online-exam DB.")
            
            # --- NEW: Log questions to banklog ---
            try:
                log_success = log_questions_for_exam(exam_id)
                if not log_success:
                    logging.warning(f"Failed to log questions to banklog for exam ID {exam_id}.")
            except Exception as log_e:
                 logging.warning(f"An exception occurred while logging to banklog for exam ID {exam_id}: {log_e}")
            # --- END NEW ---

            return {"status": "success", "message": f"Exam {exam_id} published successfully."}
        else:
            return {"status": "success", "message": f"Exam {exam_id} is already published or status could not be updated (no change needed)."}
    except HTTPException as he:
        logging.error(f"HTTPException in /tamsqb/publish-exam: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"Unexpected exception in /tamsqb/publish-exam: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to publish exam: {e}")

@app.post("/tamsqb/reveal-answers-for-finished-exams")
async def reveal_answers_for_finished_exams(current_user: User = Depends(get_current_user)):
    """
    Checks for any exams taken by the user that have now finished
    and reveals the answers for the questions in those exams.
    """
    logging.debug(f"Entering /tamsqb/reveal-answers-for-finished-exams for user: {current_user['username']}")
    
    try:
        finished_exams = get_finished_exams_for_user(current_user["id"])
        if not finished_exams:
            return {"status": "success", "message": "No finished exams found for which to reveal answers."}

        total_questions_updated = 0
        processed_exams = []

        for exam in finished_exams:
            question_ids = get_question_ids_for_exam(exam["id"])
            if question_ids:
                unhide_answers_for_questions(question_ids)
                total_questions_updated += len(question_ids)
                processed_exams.append(exam["exam_name"])

        if total_questions_updated > 0:
            return {
                "status": "success",
                "message": f"Revealed answers for {total_questions_updated} questions across {len(processed_exams)} finished exams.",
                "processed_exams": processed_exams,
                "total_questions_updated": total_questions_updated
            }
        else:
            return {"status": "success", "message": "Found finished exams, but no associated questions needed updating."}

    except Exception as e:
        logging.error(f"Unexpected exception in /tamsqb/reveal-answers-for-finished-exams: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while revealing answers.")

class ExamResponse(BaseModel):
    id: int
    online_exam_id: int
    exam_name: str
    exam_date_time: str
    duration_minutes: int
    created_at: str

class PaginatedExamsResponse(BaseModel):
    total_count: int
    exams: List[ExamResponse]

@app.get("/my-exams", response_model=PaginatedExamsResponse)
async def get_my_exams(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    logging.debug(f"Entering /my-exams for user: {current_user['username']}")
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        total_count = get_total_exams_for_user_count(current_user["id"], start_date, end_date)
        exams = get_exams_for_user(current_user["id"], limit, offset, start_date, end_date)
        
        return {"total_count": total_count, "exams": exams}
    except HTTPException as he:
        logging.error(f"HTTPException in /my-exams: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"Unexpected exception in /my-exams: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching exams.")

async def _generate_report_data(exam_id: int, current_user: User):
    """
    Internal function to fetch and process all data required for an exam report.
    This function is not an endpoint.
    """

    # 1. Check if exam exists and belongs to the user
    exam = get_exam_by_id(exam_id)
    if not exam or exam['user_id'] != current_user['id']:
        raise HTTPException(status_code=404, detail="Exam not found or not authorized.")

    # 2. Fetch question details from local DB
    questions_details = get_exam_questions_and_details(exam_id)
    if not questions_details:
        raise HTTPException(status_code=404, detail="No questions found for this exam.")

    # 3. Fetch student results from schooldemo12 DB
    # NEW: Resolve the actual student ID (handling teacher shadow accounts)
    resolved_student_id = database.resolve_student_id_for_user(current_user['id'], current_user['username'])
    if not resolved_student_id:
        logging.warning(f"REPORT_DEBUG: Could not resolve student ID for user {current_user['username']}. Using user ID as fallback.")
        resolved_student_id = current_user.get('schooldemo12_user_id') or current_user['id']

    student_results = get_student_results_for_exam(exam_id, resolved_student_id)
    logging.info(f"REPORT_DEBUG: Fetched {len(student_results)} results for exam {exam_id} and student {resolved_student_id}")

    # 4. Combine data
    report_data = []
    for q_detail in questions_details:
        question_report_entry = dict(q_detail)
        student_res = next((sr for sr in student_results if sr['bankId'] == q_detail['bank_question_id']), None)

        # Process correct answer
        correct_option_raw = q_detail.get('correct_option')
        question_report_entry['correct_answer_index'] = 'N/A'
        question_report_entry['correct_answer'] = 'N/A'
        
        q_type = (q_detail.get('question_type') or "").lower()
        if q_type in ['multiple choice', 'mch', 'yes_no', 'yn', 'accept_reject', 'ar', 'multiple_answer', 'chbox'] and correct_option_raw:
            choice_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
            # For multiple answer, we take the first correct option for the simple report view
            # In a more advanced view, we'd show all correct options
            option_to_lookup = str(correct_option_raw).strip().upper()[0] if q_type in ['multiple_answer', 'chbox'] else str(correct_option_raw).strip().upper()
            
            correct_idx = choice_map.get(option_to_lookup)
            if correct_idx:
                question_report_entry['correct_answer_index'] = str(correct_idx)
                question_report_entry['correct_answer'] = q_detail.get(f'choice_{correct_idx}', 'N/A')
            else:
                question_report_entry['correct_answer'] = str(correct_option_raw)
        elif correct_option_raw:
            question_report_entry['correct_answer'] = str(correct_option_raw)

        # Process student answer
        if student_res:
            question_report_entry.update(student_res)
            student_answer_choice = None
            raw_idx = student_res.get('student_answer_index')
            
            # 1. Try to resolve as choice index (1-4)
            if raw_idx is not None and str(raw_idx).strip() != "":
                try:
                    # Handle JSON array format like [{"index":1}] or raw string "1"
                    if '[' in str(raw_idx):
                        parsed_idx = json.loads(raw_idx)
                        if isinstance(parsed_idx, list) and len(parsed_idx) > 0:
                            idx = int(parsed_idx[0].get('index', parsed_idx[0]))
                        else:
                            idx = None
                    else:
                        idx = int(raw_idx)
                    
                    if idx is not None and 1 <= idx <= 4:
                        student_answer_choice = q_detail.get(f'choice_{idx}')
                    elif idx is not None:
                        # If index is out of bounds but numeric, use it as is
                        student_answer_choice = f"Option {idx}"
                except (ValueError, TypeError, json.JSONDecodeError, IndexError, KeyError):
                    # Fallback to raw value if parsing fails
                    student_answer_choice = str(raw_idx)
            
            # 2. If still None, try answerText
            if not student_answer_choice or student_answer_choice == 'N/A':
                student_answer_choice = student_res.get('answerText')

            question_report_entry['student_answer_choice'] = student_answer_choice or 'N/A'

            # Determine correctness
            is_correct = False
            if question_report_entry.get('student_mark') is not None and question_report_entry.get('question_mark') is not None:
                is_correct = (question_report_entry['student_mark'] == question_report_entry['question_mark'])
            question_report_entry['is_correct'] = is_correct
        
        report_data.append(question_report_entry)
        
    return {"exam": exam, "report_data": report_data}

@app.get("/exam-report/{exam_id}")
async def get_exam_report(exam_id: int, current_user: User = Depends(get_current_user)):
    try:
        data = await _generate_report_data(exam_id, current_user)
        exam = data["exam"]
        report_data = data["report_data"]

        # Pre-generate image for caching if it doesn't exist
        report_file_path = exam.get('report_image_path')
        if not report_file_path or not Path(report_file_path).exists():
            generated_image_path = generate_report_image(exam, report_data, current_user, load_translations('en'), 'en')
            if generated_image_path:
                update_exam_report_image_path(exam_id, generated_image_path)

        return {
            "report_title": "Result Report",
            "exam_name": exam['exam_name'],
            "username": current_user['username'],
            "exam_date": exam['exam_date_time'],
            "report_generation_date": datetime.now().isoformat(),
            "report_data": report_data
        }
    except HTTPException as he:
        logging.error(f"HTTPException in /exam-report/{exam_id}: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"Unexpected exception in /exam-report/{exam_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating report: {e}")

@app.get("/exam-report-image/{exam_id}")
async def get_exam_report_image(exam_id: int, lang: str = 'en', current_user: User = Depends(get_current_user)):
    try:
        data = await _generate_report_data(exam_id, current_user)
        exam = data["exam"]
        report_data = data["report_data"]
        translations = load_translations(lang)

        # For simplicity, we regenerate the report for the specific language requested
        # Caching could be improved to store language-specific versions
        generated_image_path = generate_report_image(exam, report_data, current_user, translations, lang)
        
        if generated_image_path and Path(generated_image_path).exists():
            # We can update the path, but it will only cache the last requested language
            update_exam_report_image_path(exam_id, generated_image_path)
            return FileResponse(generated_image_path, media_type="image/jpeg", filename=f"exam_report_{exam_id}_{lang}.jpg")
        else:
            raise HTTPException(status_code=500, detail="Failed to generate report image.")

    except HTTPException as he:
        logging.error(f"REPORT_DEBUG: HTTPException in /exam-report-image/{exam_id}: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"REPORT_DEBUG: Unexpected exception in /exam-report-image/{exam_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating report image: {e}")

@app.get("/debug/lookup_tables_info")
async def debug_lookup_tables_info(table_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get schema info
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema_info = cursor.fetchall()
        schema_dict = [{"cid": col['cid'], "name": col['name'], "type": col['type'], "notnull": bool(col['notnull']), "dflt_value": col['dflt_value'], "pk": bool(col['pk'])} for col in schema_info]

        # Check for name_ar column
        has_name_ar = any(col['name'] == 'name_ar' for col in schema_info)
        select_columns = "id, name"
        if has_name_ar:
            select_columns += ", name_ar"

        # Get sample data
        cursor.execute(f"SELECT {select_columns} FROM {table_name} LIMIT 5")
        sample_data = cursor.fetchall()
        sample_data_list = [dict(row) for row in sample_data]

        return {"table_name": table_name, "schema": schema_dict, "sample_data": sample_data_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing table {table_name}: {e}")
    finally:
        conn.close()

@app.get("/exam-report-html/{exam_id}")
async def get_exam_report_html(exam_id: int, lang: str = 'en', current_user: User = Depends(get_current_user)):
    try:
        data = await _generate_report_data(exam_id, current_user)
        translations = load_translations(lang)
        html_content = generate_report_html(data["exam"], data["report_data"], current_user, translations, lang)
        
        headers = {'Content-Disposition': f'attachment; filename="exam_report_{exam_id}.html"'}
        return HTMLResponse(content=html_content, headers=headers)
    except HTTPException as he:
        logging.error(f"REPORT_DEBUG: HTTPException in /exam-report-html/{exam_id}: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        logging.error(f"REPORT_DEBUG: Unexpected exception in /exam-report-html/{exam_id}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating report HTML: {e}")

@app.get("/config")
async def get_config():
    return {
        "BACKEND_BASE_URL": os.getenv("BACKEND_BASE_URL", "http://questai.examforall.com:8300")
    }

# Mount static files first
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Mount the static directory
static_dir = Path(__file__).resolve().parent.parent / 'static'
if static_dir.exists():
    app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')


# Mount the frontend directory at the end
frontend_dir = Path(__file__).resolve().parent.parent / 'frontend'
if frontend_dir.exists():
    app.mount('/', StaticFiles(directory=str(frontend_dir), html=True), name='frontend')
