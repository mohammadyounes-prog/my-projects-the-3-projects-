# D:\QuestionRetrieval\new-q-bank\backend\dashboard.py

import pymysql
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from auth_utils import get_current_admin_user, User

# --- Database Connection ---
MYSQL_HOST = os.getenv("ONLINE_EXAM_MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("ONLINE_EXAM_MYSQL_PORT", 3307))
MYSQL_DB = os.getenv("ONLINE_EXAM_MYSQL_DB", "schooldemo12")
MYSQL_USER = os.getenv("ONLINE_EXAM_MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("ONLINE_EXAM_MYSQL_PASSWORD", "root")

def get_online_exam_db_connection():
    """Establishes a connection to the online-exam project's MySQL database."""
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.Error as e:
        print(f"ERROR: Could not connect to online-exam MySQL database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {e}"
        )

# --- Database Functions ---

def get_total_students_count() -> int:
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student")
        result = cursor.fetchone()
        return result['COUNT(*)'] if result else 0
    finally:
        if conn:
            conn.close()

def get_total_exams_count() -> int:
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exam")
        result = cursor.fetchone()
        return result['COUNT(*)'] if result else 0
    finally:
        if conn:
            conn.close()

def get_latest_exams(limit: int = 5) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, date, totalQ, mark FROM exam ORDER BY date DESC LIMIT %s", (limit,))
        return cursor.fetchall()
    finally:
        if conn:
            conn.close()

def get_student_performance_summary() -> List[Dict[str, Any]]:
    """
    Calculates and returns a summary of each student's performance.
    """
    conn = None
    try:
        conn = get_online_exam_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                s.name AS student_name,
                COUNT(r.id) AS total_exams,
                AVG(r.currentMark) AS average_score
            FROM
                result AS r
            JOIN
                student AS s ON r.studentId = s.id
            WHERE
                r.status = 'Complete'
            GROUP BY
                s.id, s.name
            ORDER BY
                s.name;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            row['average_score'] = float(row['average_score']) if row['average_score'] is not None else 0.0
        return results
    finally:
        if conn:
            conn.close()

# --- API Router ---

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_admin_user)):
    """
    Provides a summary of key metrics for the online-exam dashboard.
    """
    if not (current_user.get("is_admin") or current_user.get("is_super_admin")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this dashboard.")

    total_students = get_total_students_count()
    total_exams = get_total_exams_count()
    latest_exams = get_latest_exams(limit=5)
    student_performance = get_student_performance_summary()

    return {
        "total_students": total_students,
        "total_exams": total_exams,
        "latest_exams": latest_exams,
        "student_performance_summary": student_performance
    }

@router.post("/generate-advice")
async def generate_advice(context: Dict[str, Any]):
    """
    Generates strategic advice based on dashboard data using Gemini.
    """
    import logging
    import traceback
    from gemini_api import generate_solution_with_gemini
    from config import GOOGLE_API_KEY
    
    logger = logging.getLogger(__name__)
    
    try:
        # Construct a comprehensive prompt for the AI based on the dashboard context provided
        prompt = f"Act as an expert educational strategist. Based on the following dashboard metrics and insights, provide a short, actionable, and strategic advice for improving institutional performance:\n\n{str(context)}\n\nLimit the advice to 3 key bullet points."
        
        # We use a helper function from gemini_api (repurposed here as a simple prompt-to-text call)
        advice = generate_solution_with_gemini(
            question_text=prompt,
            question_type="Strategic Advice",
            difficulty_level="N/A",
            cognitive_level="N/A",
            learning_outcome="N/A",
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        if isinstance(advice, dict) and "error" in advice:
            logger.error(f"AI generation error: {advice.get('error')}")
            raise HTTPException(status_code=500, detail=f"AI generation failed: {advice['error']}")
            
        return {"advice": advice}
        
    except Exception as e:
        logger.error(f"Error in generate_advice: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error in generate_advice: {str(e)}")
