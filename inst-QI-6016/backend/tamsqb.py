from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from auth_utils import User, get_current_user
from tamsqb_api import get_courses_for_user, get_questions_for_course

router = APIRouter()

@router.get("/courses", response_model=List[Dict[str, Any]])
async def get_user_courses(current_user: User = Depends(get_current_user)):
    """
    Retrieves a list of courses associated with the current user.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    courses = get_courses_for_user(current_user["username"])
    if not courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found for this user.")
    return courses

@router.get("/questions/{course_id}", response_model=List[Dict[str, Any]])
async def get_course_questions(course_id: int, current_user: User = Depends(get_current_user)):
    """
    Retrieves a list of questions for a specific course.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    questions = get_questions_for_course(course_id)
    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No questions found for course ID: {course_id}")
    return questions
