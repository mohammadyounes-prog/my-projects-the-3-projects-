import os
from pathlib import Path
from typing import List, Dict, Any
import logging
import imgkit # Import imgkit

# Directory to save generated reports
REPORT_DIR = Path(__file__).resolve().parent / "generated_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True) # Ensure directory exists

# Path to wkhtmltoimage executable if not in PATH
# On Windows, it might be something like: r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
# On Linux, often: '/usr/local/bin/wkhtmltoimage' or '/usr/bin/wkhtmltoimage'
# You might need to adjust this depending on your wkhtmltoimage installation.
# If wkhtmltoimage is in your system's PATH, this can be set to None or just 'wkhtmltoimage'.
# Path to wkhtmltopdf executable (for PDF generation)
# On Windows, it might be something like: r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# On Linux, often: '/usr/local/bin/wkhtmltopdf' or '/usr/bin/wkhtmltopdf'
# You might need to adjust this depending on your wkhtmltopdf installation.
# If wkhtmltopdf is in your system's PATH, this can be set to None or just 'wkhtmltopdf'.
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# Configure imgkit (for PDF generation)
if WKHTMLTOPDF_PATH and WKHTMLTOPDF_PATH != 'wkhtmltopdf':
    # The config function internally expects 'wkhtmltoimage' parameter name for the executable path,
    # even when configuring for wkhtmltopdf functionality.
    _config_obj = imgkit.config() # Call the function to get a Config object
    _config_obj.wkhtmltopdf = WKHTMLTOPDF_PATH
    CONFIG_PDF = _config_obj  
else:
    CONFIG_PDF = None # imgkit will try to find wkhtmltopdf in PATH

# Separate configuration for image generation, if still needed by report_generator.py
WKHTMLTOIMAGE_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe' # Keeping original for image
if WKHTMLTOIMAGE_PATH and WKHTMLTOIMAGE_PATH != 'wkhtmltoimage':
    _config_image_obj = imgkit.config()
    _config_image_obj.wkhtmltoimage = WKHTMLTOIMAGE_PATH
    CONFIG_IMAGE = _config_image_obj
else:
    CONFIG_IMAGE = None

import datetime

def _generate_base_html(exam: Dict, report_data: List[Dict], user: Dict, translations: Dict, lang: str = 'en') -> str:
    """
    Internal function to generate the common HTML structure for a report.
    """
    exam_id = exam['id']
    user_id = user['id']
    direction = "rtl" if lang == "ar" else "ltr"
    
    def t(key, default_text):
        keys = key.split('.')
        val = translations
        for k in keys:
            val = val.get(k)
            if val is None:
                return default_text
        return val

    # --- Generate HTML content ---
    html_content = f"""
    <!DOCTYPE html>
    <html dir="{direction}" lang="{lang}">
    <head>
        <title>{t('examDetailReport.defaultTitle', 'Exam Result Report')}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; color: #333; text-align: { 'right' if lang == 'ar' else 'left' }; background-color: #f4f7f6; }}
            .container {{ width: 1100px; margin: 0 auto; border: 1px solid #ddd; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); background-color: #fff; border-radius: 8px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 25px; }}
            .header-info {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef; }}
            .header-info p {{ margin: 0; min-width: 250px; font-size: 0.95em; }}
            .label {{ font-weight: 700; color: #7f8c8d; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #34495e; color: #fff; text-align: inherit; padding: 12px 10px; font-size: 0.9em; }}
            td {{ padding: 12px 10px; border-bottom: 1px solid #eee; vertical-align: top; font-size: 0.9em; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .status-correct {{ color: #27ae60; font-weight: 700; }}
            .status-incorrect {{ color: #e74c3c; font-weight: 700; }}
            .choice-list {{ margin: 0; padding: 0; list-style: none; font-size: 0.85em; color: #7f8c8d; }}
            .choice-list li {{ margin-bottom: 2px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{t('examDetailReport.defaultTitle', 'Exam Result Report')}</h1>
            <div class="header-info">
                <p><span class="label">{t('examDetailReport.examName', 'Exam Name')}:</span> {exam.get('exam_name', 'N/A')}</p>
                <p><span class="label">{t('examDetailReport.username', 'Username')}:</span> {user.get('username', 'N/A')}</p>
                <p><span class="label">{t('examDetailReport.examDate', 'Exam Date')}:</span> {exam.get('exam_date_time', 'N/A')}</p>
                <p><span class="label">{t('examDetailReport.reportGenerated', 'Report Generated')}:</span> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 30px;">#</th>
                        <th>{t('examDetailReport.question', 'Question')}</th>
                        <th>{t('examDetailReport.learningOutcome', 'Learning Outcome')}</th>
                        <th>{t('examDetailReport.correctAnswer', 'Correct Answer')}</th>
                        <th>{t('examDetailReport.yourAnswer', 'Your Answer')}</th>
                        <th style="width: 80px;">{t('examDetailReport.status', 'Status')}</th>
                        <th style="width: 80px;">{t('examDetailReport.score', 'Score')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    rows_html = ""
    for i, q_report in enumerate(report_data):
        question_text = q_report.get('question_text', 'N/A')
        
        status_class = "status-incorrect" if not q_report.get('is_correct') else "status-correct"
        status_display = t('examDetailReport.correct', 'Correct') if q_report.get('is_correct') else t('examDetailReport.incorrect', 'Incorrect')
        
        rows_html += f"""
            <tr>
                <td>{i+1}</td>
                <td>
                    <div style="font-weight: 600; margin-bottom: 8px;">{question_text}</div>
                </td>
                <td>{q_report.get('learning_outcome_name', 'N/A')}</td>
                <td>{q_report.get('correct_answer', 'N/A')}</td>
                <td>{q_report.get('student_answer_choice', 'N/A')}</td>
                <td class="{status_class}">{status_display}</td>
                <td>{q_report.get('student_mark', 'N/A')} / {q_report.get('question_mark', 'N/A')}</td>
            </tr>
        """
    
    html_content += rows_html + """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_report_image(exam: Dict, report_data: List[Dict], user: Dict, translations: Dict, lang: str = 'en') -> str:
    """
    Generates a JPG image of the exam report from HTML content.
    """
    exam_id = exam['id']
    user_id = user['id']
    logging.info(f"REPORT_GEN_DEBUG: Generating report image using imgkit for exam_id: {exam_id}, user_id: {user_id}")

    image_filename = f"report_exam_{exam_id}_user_{user_id}.jpg"
    image_path = REPORT_DIR / image_filename

    html_content = _generate_base_html(exam, report_data, user, translations, lang)

    try:
        logging.debug(f"REPORT_GEN_DEBUG: Attempting to convert HTML to image. WKHTMLTOIMAGE_PATH: {WKHTMLTOIMAGE_PATH}")
        options = {
            'quality': 90,
            'enable-local-file-access': None,
            'width': 1000,
            'encoding': "UTF-8",
            'no-stop-slow-scripts': None,
        }
        
        if CONFIG:
            success = imgkit.from_string(html_content, str(image_path), options=options, config=CONFIG)
        else:
            success = imgkit.from_string(html_content, str(image_path), options=options)

        if success:
            logging.info(f"REPORT_GEN_DEBUG: Report image generated successfully at: {image_path}")
            return str(image_path)
        else:
            logging.error(f"REPORT_GEN_DEBUG: imgkit.from_string returned False. Check wkhtmltoimage installation.")
            raise Exception("imgkit failed to generate image.")

    except Exception as e:
        logging.error(f"REPORT_GEN_DEBUG: Error generating report image with imgkit: {e}", exc_info=True)
        if "No wkhtmltoimage executable found" in str(e) or "Failed to execute" in str(e):
            logging.error("REPORT_GEN_DEBUG: wkhtmltoimage not found. Configure path in report_generator.py.")
        return ""

def generate_report_html(exam: Dict, report_data: List[Dict], user: Dict, translations: Dict, lang: str = 'en') -> str:
    """
    Generates HTML content for the exam report.
    """
    logging.info(f"REPORT_GEN_DEBUG: Generating report HTML for exam_id: {exam['id']}, user_id: {user['id']}")
    return _generate_base_html(exam, report_data, user, translations, lang)
