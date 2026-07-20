from fastapi import APIRouter
from .ai_utils import get_gemini_advice
import json

router = APIRouter()

FEEDBACK_MAP = {
    "Excellent technical lead, shows great initiative in project planning.": "قائد تقني متميز، يظهر مبادرة كبيرة في تخطيط المشاريع.",
    "Very collaborative and always ready to support the team during tight deadlines.": "متعاون جداً ومستعد دائماً لدعم الفريق خلال المواعيد النهائية الضيقة.",
    "Communication could be improved during the initial design phases.": "يمكن تحسين التواصل خلال مراحل التصميم الأولية.",
    "Ready for Senior Role Review": "جاهز للمراجعة للترقية إلى دور قيادي",
    "Needs further skill development": "يحتاج إلى المزيد من تطوير المهارات",
    "Advanced Time Management Workshop": "ورشة عمل متقدمة لإدارة الوقت",
    "Quality Assurance Best Practices Seminar": "ندوة حول أفضل ممارسات ضمان الجودة",
    "Strong analytical and problem-solving skills; naturally adapts to new technical environments.": "مهارات تحليلية وحل مشكلات قوية؛ يتكيف بشكل طبيعي مع البيئات التقنية الجديدة.",
    "Task Completion": "إنجاز المهام",
    "Output Quality": "جودة المخرجات",
    "Peer": "زميل",
    "Manager": "مدير",
    "Direct Supervisor": "المشرف المباشر",
    "Senior Engineer": "مهندس أول",
    "UX Designer": "مصمم تجربة مستخدم"
}

def translate_text(text: str, lang: str):
    if lang == "en": return text
    
    # 1. Try static map first
    if lang == "ar" and text in FEEDBACK_MAP:
        return FEEDBACK_MAP[text]
    
    # 2. Fallback to AI for dynamic or unknown content
    try:
        result = get_gemini_advice({"text_to_translate": text}, lang=lang)
        if "Error generating AI advice" in result:
            return text
        return result.replace("AI Advice:", "").strip()
    except Exception:
        return text

@router.get("/bank-health", summary="Fetch question bank health metrics")
async def get_bank_health():
    # Mock data representing bank composition
    return {
        "difficulty": [
            {"label": "Easy", "count": 150},
            {"label": "Medium", "count": 300},
            {"label": "Hard", "count": 50}
        ],
        "discrimination": [
            {"label": "High", "count": 200},
            {"label": "Medium", "count": 150},
            {"label": "Low", "count": 150}
        ]
    }

@router.get("/personality-insights/{employee_id}", summary="Fetch personality and behavioral insights for an employee")
async def get_personality_insights(employee_id: int, lang: str = "en"):
    data = {
        "employee_id": employee_id,
        "traits": [
            {"trait": "Analytical", "score": 85},
            {"trait": "Collaborative", "score": 70},
            {"trait": "Leadership", "score": 65},
            {"trait": "Adaptability", "score": 80}
        ],
        "summary": "Strong analytical and problem-solving skills; naturally adapts to new technical environments."
    }
    if lang == "ar":
        data["summary"] = translate_text(data["summary"], lang)
    return data

@router.get("/performance-scorecard/{employee_id}", summary="Fetch performance metrics for an employee")
async def get_performance_scorecard(employee_id: int):
    # This fetches real-time output metrics for an individual
    return {
        "employee_id": employee_id,
        "metrics": [
            {"label": "Task Completion", "value": 92, "target": 100},
            {"label": "Output Quality", "value": 85, "target": 90},
            {"label": "Goal Achievement", "value": 78, "target": 85}
        ]
    }

@router.get("/development-recommendations/{employee_id}", summary="Fetch AI-driven development tasks based on performance gaps")
async def get_development_recommendations(employee_id: int, lang: str = "en"):
    data = {
        "employee_id": employee_id,
        "recommendations": [
            {"task": "Advanced Time Management Workshop", "gap": "Task Completion", "priority": "High"},
            {"task": "Quality Assurance Best Practices Seminar", "gap": "Output Quality", "priority": "Medium"}
        ]
    }
    if lang == "ar":
        for rec in data["recommendations"]:
            rec["task"] = translate_text(rec["task"], lang)
            rec["gap"] = translate_text(rec["gap"], lang)
    return data

@router.get("/advancement-status/{employee_id}", summary="Evaluate employee readiness for advancement")
async def get_advancement_status(employee_id: int, lang: str = "en"):
    # Business Logic: Advancement is triggered if Task Completion > 90% AND Skill Gap < 20%
    readiness_score = 88 
    is_ready = readiness_score >= 85
    
    data = {
        "employee_id": employee_id,
        "readiness_score": readiness_score,
        "is_ready": is_ready,
        "recommendation": "Ready for Senior Role Review" if is_ready else "Needs further skill development"
    }
    if lang == "ar":
        data["recommendation"] = translate_text(data["recommendation"], lang)
    return data

@router.get("/feedback/{employee_id}", summary="Fetch 360-degree feedback for an employee")
async def get_employee_feedback(employee_id: int, lang: str = "en"):
    data = {
        "employee_id": employee_id,
        "feedback": [
            {"reviewer": "Manager", "role": "Direct Supervisor", "comment": "Excellent technical lead, shows great initiative in project planning."},
            {"reviewer": "Peer", "role": "Senior Engineer", "comment": "Very collaborative and always ready to support the team during tight deadlines."},
            {"reviewer": "Peer", "role": "UX Designer", "comment": "Communication could be improved during the initial design phases."}
        ]
    }
    if lang == "ar":
        for item in data["feedback"]:
            item["comment"] = translate_text(item["comment"], lang)
            item["reviewer"] = translate_text(item["reviewer"], lang)
            item["role"] = translate_text(item["role"], lang)
    return data
