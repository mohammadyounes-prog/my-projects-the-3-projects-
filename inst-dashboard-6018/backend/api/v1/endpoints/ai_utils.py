import google.generativeai as genai
import datetime
from ....core.config import settings
from ....database.session import get_questai_db_connection

def save_advice_to_db(advice_en: str, advice_ar: str):
    try:
        db = get_questai_db_connection()
        cursor = db.cursor()
        
        # Check for similar content in the last 60 minutes
        cursor.execute("SELECT advice_en FROM ai_advice WHERE created_at > datetime('now', '-60 minutes') ORDER BY created_at DESC LIMIT 1")
        last_row = cursor.fetchone()
        
        if last_row and last_row[0] == advice_en:
            print("Duplicate advice detected, skipping.")
            db.close()
            return

        cursor.execute("INSERT INTO ai_advice (advice_en, advice_ar, created_at) VALUES (?, ?, ?)", (advice_en, advice_ar, datetime.datetime.now()))
        db.commit()
        db.close()
    except Exception as e:
        print(f"Failed to save advice to DB: {e}")

def get_gemini_advice(dashboard_data: dict, lang: str = "en"):
    if not settings.GOOGLE_API_KEY:
        return "AI advice is currently unavailable: No API key configured."
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    # Generate English
    prompt_en = f"Analyze: {dashboard_data}. Provide concise executive summary and 3 recommendations in English."
    try:
        resp_en = model.generate_content(prompt_en)
        advice_en = resp_en.text
        
        # Translate to Arabic
        prompt_ar = f"Translate the following executive summary into professional Arabic: {advice_en}"
        resp_ar = model.generate_content(prompt_ar)
        advice_ar = resp_ar.text
        
        save_advice_to_db(advice_en, advice_ar)
        return advice_ar if lang == "ar" else advice_en
    except Exception as e:
        return f"Error: {str(e)}"
