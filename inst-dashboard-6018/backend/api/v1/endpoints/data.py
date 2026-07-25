from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from typing import Dict, Any, List, Optional
from ....database.session import get_questai_db, get_online_exam_db_connection
from ....database.utils import get_date_filter_sql
from ....core.config import settings
from .ai_utils import get_gemini_advice

router = APIRouter()

@router.get("/ai-advice", summary="Fetch AI-powered management insights")
async def get_ai_advice(lang: str = "en", sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        kpis = await get_dashboard_kpis(sqlite_db=sqlite_db, lang=lang)
        return {"advice": get_gemini_advice(kpis, lang=lang)}
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-advice-history", summary="Fetch latest AI advice from database")
async def get_ai_advice_history(lang: str = "en", sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        cursor = sqlite_db.cursor()
        column = "advice_ar" if lang == "ar" else "advice_en"
        cursor.execute(f"SELECT {column} FROM ai_advice ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        
        return {"advice": row[0] if row else "No advice available yet."}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not fetch AI advice.")

def _empty_kpi_payload(lang: str = "en", insight: Optional[str] = None) -> Dict[str, Any]:
    """Stable KPI shape for UI when exam MySQL tables are unavailable locally."""
    if insight is None:
        insight = (
            "لا تتوفر بيانات الامتحانات محلياً بعد. تُعرض قيم صفرية."
            if lang == "ar"
            else "No exam result tables available locally yet. Showing zeroed KPIs."
        )
    zero = {"value": 0.0, "target": 90.0, "trend": "stable", "delta": 0.0}
    return {
        "overall_performance": {
            "value": 0.0,
            "target": 100.0,
            "trend": "stable",
            "delta": 0.0,
            "insight": insight,
            "breakdown": {"academic": 0.0, "operational": 0.0, "quality": 0.0},
        },
        "avg_lo_attainment": {**zero},
        "pass_rate": {**zero},
        "exam_quality_index": {**zero, "target": 90.0},
        "question_bank_health": {**zero, "target": 100.0, "value": 0.0},
    }


@router.get("/kpis", summary="Fetch all core dashboard KPIs with historical trends")
async def get_dashboard_kpis(
    start_date: str = None, 
    end_date: str = None,
    lang: str = "en",
    sqlite_db: sqlite3.Connection = Depends(get_questai_db)
):
    try:
        # 1. Fetch Question Map
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT question_id, learning_outcome_id FROM questions")
        q_lo_map = {row['question_id']: row['learning_outcome_id'] for row in sqlite_cursor.fetchall()}
        
        # 2. Get Date Filter for MySQL
        filter_sql, filter_params = get_date_filter_sql(start_date, end_date, "e.date")

        try:
            mysql_conn = get_online_exam_db_connection()
        except Exception as conn_err:
            print(f"WARNING: KPI MySQL unavailable, returning empty KPIs: {conn_err}")
            return _empty_kpi_payload(lang)

        try:
            with mysql_conn.cursor() as cursor:
                query = f"""
                    SELECT sr.examDataId, sr.currentMark, sr.examDataMark, sr.studentId, sr.examId
                    FROM studentresult sr
                    JOIN exam e ON sr.examId = e.id
                    WHERE 1=1 {filter_sql}
                """
                cursor.execute(query, filter_params)
                answers = cursor.fetchall()
                
                cursor.execute("SELECT id, bankId FROM examdata")
                examdata_map = {row['id']: row['bankId'] for row in cursor.fetchall()}
        except Exception as query_err:
            print(f"WARNING: KPI MySQL query failed, returning empty KPIs: {query_err}")
            return _empty_kpi_payload(lang)
        finally:
            mysql_conn.close()

        # 3. Aggregate Metrics & Diagnostic Indices
        lo_attainment = {} 
        total_attempts = 0
        pass_count = 0
        
        for ans in answers:
            examDataId = ans['examDataId']
            bankId = examdata_map.get(examDataId)
            curr = float(ans['currentMark'] or 0)
            total = float(ans['examDataMark'] or 0)
            
            if total > 0:
                total_attempts += 1
                if curr >= (total / 2): pass_count += 1
            
            if bankId in q_lo_map:
                lo_id = q_lo_map[bankId]
                is_correct = 1 if curr >= (total / 2) and total > 0 else 0
                if lo_id not in lo_attainment: lo_attainment[lo_id] = []
                lo_attainment[lo_id].append(is_correct)
        
        # Diagnostics: Academic, Operational, Quality
        academic_idx = (sum([sum(res)/len(res) for res in lo_attainment.values()]) / len(lo_attainment) * 100) if lo_attainment else 0
        operational_idx = (pass_count / total_attempts * 100) if total_attempts > 0 else 0
        quality_idx = 80.0  # Placeholder for Exam Quality
        
        # Composite Performance Index (Weighted average)
        overall_val = (0.5 * academic_idx) + (0.3 * operational_idx) + (0.2 * quality_idx)
        
        # 3.5 Generate Actionable Insights (Diagnostic)
        def get_insight():
            drivers = []
            if lang == "ar":
                if academic_idx < 70: drivers.append("مخرجات التعلم (LO)")
                if operational_idx < 70: drivers.append("نسب النجاح")
                if quality_idx < 70: drivers.append("جودة الاختبارات")
                if not drivers: return "الأداء مستقر. الصحة المؤسسية قوية عبر جميع المقاييس."
                return f"يتطلب إجراء: أعطِ الأولوية للتحسين في: {', '.join(drivers)}."
            else:
                if academic_idx < 70: drivers.append("Academic (LO Attainment)")
                if operational_idx < 70: drivers.append("Operational (Pass Rates)")
                if quality_idx < 70: drivers.append("Quality (Exam Reliability)")
                if not drivers: return "Performance stable. Institutional health is strong across all metrics."
                return f"Action Required: Prioritize improvement in: {', '.join(drivers)}."

        insight = get_insight()
        
        # 4. Return diagnostic object
        return {
            "overall_performance": {
                "value": round(overall_val, 2),
                "target": 100.0,
                "trend": "stable", "delta": 0.0,
                "insight": insight,
                "breakdown": {
                    "academic": round(academic_idx, 2),
                    "operational": round(operational_idx, 2),
                    "quality": round(quality_idx, 2)
                }
            },

            "avg_lo_attainment": {
                "value": round(academic_idx, 2),
                "target": 90.0,
                "trend": "up", "delta": 2.5
            },
            "pass_rate": {
                "value": round(operational_idx, 2),
                "target": 90.0,
                "trend": "up", "delta": 1.5
            },
            "exam_quality_index": {
                "value": round(quality_idx, 2),
                "target": 90.0,
                "trend": "up", "delta": 0.8
            },
            "question_bank_health": {
                "value": 90.0,
                "target": 100.0,
                "trend": "up", "delta": 5.0
            }
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))



@router.get("/at-risk-students", summary="Identify students performing below threshold")
async def get_at_risk_students(threshold: float = 50.0, sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT question_id, learning_outcome_id FROM questions")
        q_lo_map = {row['question_id']: row['learning_outcome_id'] for row in sqlite_cursor.fetchall()}
        sqlite_cursor.execute("SELECT id, name FROM learning_outcomes")
        lo_info = {row['id']: {"name": row['name'], "code": f"LO-{row['id']}"} for row in sqlite_cursor.fetchall()}
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as cursor:
                cursor.execute("SELECT id, name FROM student")
                students = {row['id']: row['name'] for row in cursor.fetchall()}
                cursor.execute("SELECT id, bankId FROM examdata")
                examdata_map = {row['id']: row['bankId'] for row in cursor.fetchall()}
                cursor.execute("SELECT studentId, AVG(currentMark * 100 / NULLIF(examMark, 0)) as avg_score FROM result WHERE status='Complete' GROUP BY studentId")
                performance = {row['studentId']: float(row['avg_score'] or 0) for row in cursor.fetchall()}
                cursor.execute("SELECT studentId, examDataId, currentMark, examDataMark FROM studentresult")
                detailed_results = cursor.fetchall()
        finally: mysql_conn.close()
        at_risk = []
        for sid, score in performance.items():
            if score < threshold:
                student_lo_failures = {}
                for res in [r for r in detailed_results if r['studentId'] == sid]:
                    bank_id = examdata_map.get(res['examDataId'])
                    lo_id = q_lo_map.get(bank_id)
                    if lo_id and not (float(res['currentMark']) >= (float(res['examDataMark']) / 2)):
                        student_lo_failures[lo_id] = student_lo_failures.get(lo_id, 0) + 1
                sorted_failures = sorted(student_lo_failures.items(), key=lambda x: x[1], reverse=True)[:2]
                critical_los = [lo_info[fid]['code'] for fid, count in sorted_failures if fid in lo_info]
                at_risk.append({"id": sid, "name": students.get(sid, "Unknown"), "avg_score": round(score, 1), "critical_los": critical_los})
        return sorted(at_risk, key=lambda x: x['avg_score'])
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

@router.get("/heatmap-data", summary="LO performance per exam heatmap")
async def get_heatmap_data(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT question_id, learning_outcome_id FROM questions")
        q_lo_map = {row['question_id']: row['learning_outcome_id'] for row in sqlite_cursor.fetchall()}
        sqlite_cursor.execute("SELECT id, name FROM learning_outcomes")
        lo_names = {row['id']: row['name'] for row in sqlite_cursor.fetchall()}
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as mysql_cursor:
                mysql_cursor.execute("SELECT id, name FROM exam")
                exam_names = {row['id']: row['name'] for row in mysql_cursor.fetchall()}
                mysql_cursor.execute("SELECT id, bankId FROM examdata")
                examdata_map = {row['id']: row['bankId'] for row in mysql_cursor.fetchall()}
                mysql_cursor.execute("SELECT examId, examDataId, currentMark, examDataMark FROM studentresult")
                answers = mysql_cursor.fetchall()
        finally: mysql_conn.close()
        heatmap_raw = {}
        for ans in answers:
            exam_name = exam_names.get(ans['examId'], 'Unknown Exam')
            bank_id = examdata_map.get(ans['examDataId'])
            lo_id = q_lo_map.get(bank_id)
            if lo_id:
                lo_name = lo_names.get(lo_id, f"LO-{lo_id}")
                if exam_name not in heatmap_raw: heatmap_raw[exam_name] = {}
                if lo_name not in heatmap_raw[exam_name]: heatmap_raw[exam_name][lo_name] = []
                is_correct = 1 if float(ans['currentMark']) >= (float(ans['examDataMark']) / 2) and float(ans['examDataMark']) > 0 else 0
                heatmap_raw[exam_name][lo_name].append(is_correct)
        heatmap_data = []
        for exam, los in heatmap_raw.items():
            for lo, scores in los.items():
                heatmap_data.append({"exam": exam, "lo": lo, "value": round((sum(scores) / len(scores)) * 100, 1)})
        return heatmap_data
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

@router.get("/lo-attainment-trend", summary="LO attainment trend over time")
async def get_lo_trend(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT question_id, learning_outcome_id FROM questions")
        q_lo_map = {row['question_id']: row['learning_outcome_id'] for row in sqlite_cursor.fetchall()}
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as mysql_cursor:
                mysql_cursor.execute("SELECT id, date FROM exam")
                exam_dates = {row['id']: row['date'].strftime('%Y-%m-%d') if row['date'] else 'Unknown' for row in mysql_cursor.fetchall()}
                mysql_cursor.execute("SELECT examId, examDataId, currentMark, examDataMark FROM studentresult")
                answers = mysql_cursor.fetchall()
                mysql_cursor.execute("SELECT id, bankId FROM examdata")
                examdata_map = {row['id']: row['bankId'] for row in mysql_cursor.fetchall()}
        finally: mysql_conn.close()
        trend_data = {}
        for ans in answers:
            date_str = exam_dates.get(ans['examId'], 'Unknown')
            if date_str == 'Unknown': continue
            bankId = examdata_map.get(ans['examDataId'])
            if bankId in q_lo_map:
                is_correct = 1 if float(ans['currentMark']) >= (float(ans['examDataMark']) / 2) and float(ans['examDataMark']) > 0 else 0
                if date_str not in trend_data: trend_data[date_str] = []
                trend_data[date_str].append(is_correct)
        result = []
        for date_str in sorted(trend_data.keys()):
            scores = trend_data[date_str]
            avg = (sum(scores) / len(scores) * 100) if scores else 0
            result.append({"date": date_str, "attainment": round(avg, 1)})
        return result
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

@router.get("/lo-attainment", summary="Detailed LO attainment breakdown")
async def get_lo_breakdown(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("SELECT question_id, learning_outcome_id FROM questions")
        q_lo_map = {row['question_id']: row['learning_outcome_id'] for row in sqlite_cursor.fetchall()}
        sqlite_cursor.execute("SELECT id, name FROM learning_outcomes")
        lo_info = {row['id']: {"name": row['name'], "code": f"LO-{row['id']}"} for row in sqlite_cursor.fetchall()}
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as mysql_cursor:
                mysql_cursor.execute("SELECT id, bankId FROM examdata")
                examdata_map = {row['id']: row['bankId'] for row in mysql_cursor.fetchall()}
                mysql_cursor.execute("SELECT examDataId, currentMark, examDataMark, studentId FROM studentresult")
                answers = mysql_cursor.fetchall()
        finally: mysql_conn.close()
        lo_stats = {}
        for ans in answers:
            bankId = examdata_map.get(ans['examDataId'])
            lo_id = q_lo_map.get(bankId)
            if lo_id:
                if lo_id not in lo_stats: lo_stats[lo_id] = {"scores": [], "students": set()}
                is_correct = 1 if float(ans['currentMark']) >= (float(ans['examDataMark']) / 2) and float(ans['examDataMark']) > 0 else 0
                lo_stats[lo_id]["scores"].append(is_correct)
                lo_stats[lo_id]["students"].add(ans['studentId'])
        breakdown = []
        for lo_id, data in lo_stats.items():
            info = lo_info.get(lo_id, {"name": "Unknown LO", "code": f"LO-{lo_id}"})
            total_attempts = len(data["scores"])
            attainment = (sum(data["scores"]) / total_attempts * 100) if total_attempts > 0 else 0
            breakdown.append({"id": lo_id, "code": info["code"], "name": info["name"], "attainment": round(attainment, 1), "total_attempts": total_attempts, "unique_students": len(data["students"])})
        return sorted(breakdown, key=lambda x: x['attainment'], reverse=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

@router.get("/exam-quality", summary="Analyze exam difficulty and discrimination")
async def get_exam_quality(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as mysql_cursor:
                # Get exam results
                mysql_cursor.execute("SELECT examId, studentId, currentMark, examDataMark FROM studentresult")
                results = mysql_cursor.fetchall()
                mysql_cursor.execute("SELECT id, name FROM exam")
                exam_names = {row['id']: row['name'] for row in mysql_cursor.fetchall()}
        finally: mysql_conn.close()
        
        # Group by exam
        exam_scores = {}
        for r in results:
            eid = r['examId']
            if eid not in exam_scores: exam_scores[eid] = []
            score = (float(r['currentMark']) / float(r['examDataMark'])) if float(r['examDataMark']) > 0 else 0
            exam_scores[eid].append(score)
            
        quality = []
        for eid, scores in exam_scores.items():
            if not scores: continue
            difficulty = sum(scores) / len(scores)
            
            # Simple discrimination: Contrast high and low 25% performers
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            if n > 4:
                low = sorted_scores[:n//4]
                high = sorted_scores[-n//4:]
                discrimination = (sum(high) / len(high)) - (sum(low) / len(low))
            else:
                discrimination = 0
                
            quality.append({
                "exam": exam_names.get(eid, f"Exam {eid}"),
                "difficulty": round(difficulty, 2),
                "discrimination": round(discrimination, 2)
            })
        return quality
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))

import json

@router.get("/distractor-analysis", summary="Analyze distractor effectiveness")
async def get_distractor_analysis(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        mysql_conn = get_online_exam_db_connection()
        try:
            with mysql_conn.cursor() as mysql_cursor:
                # The schema shows 'answers' and 'correct' are the columns in examdata
                query = """
                    SELECT sr.answer, sr.currentMark, sr.examDataMark, ed.answers AS correct_options
                    FROM studentresult sr
                    JOIN examdata ed ON sr.examDataId = ed.id
                    WHERE sr.answer IS NOT NULL
                """
                mysql_cursor.execute(query)
                results = mysql_cursor.fetchall()
        finally: mysql_conn.close()
        
        analysis = {}
        for r in results:
            try:
                # Parse JSON answer string
                student_answer_data = json.loads(r['answer'])
                # 'correct_options' is also JSON
                correct_options_data = json.loads(r['correct_options'])
                
                if isinstance(student_answer_data, list) and len(student_answer_data) > 0:
                    option_idx = str(student_answer_data[0].get('index'))
                    option_text = student_answer_data[0].get('text', 'Unknown')
                    
                    is_correct = float(r['currentMark']) >= (float(r['examDataMark']) / 2)
                    if not is_correct:
                        # Aggregate by index, but keep text for display
                        key = f"{option_idx}|{option_text}"
                        analysis[key] = analysis.get(key, 0) + 1
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        
        # Return structured data
        return [{"option": k.split('|')[0], "text": k.split('|')[1], "count": v} for k, v in analysis.items()]
    except Exception as e:
        import traceback; traceback.print_exc()
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))


import statistics

@router.get("/exams/{exam_id}/statistics", summary="Calculate class statistics for a given exam")
async def get_exam_statistics(exam_id: int):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT currentMark, examDataMark
                FROM studentresult 
                WHERE examId = %s AND examDataMark > 0
            """, (exam_id,))
            results = cursor.fetchall()
            
            if not results:
                return {"message": "No results found for this exam."}
            
            scores = [(float(r['currentMark']) / float(r['examDataMark'])) * 100 for r in results]
            
            avg = statistics.mean(scores)
            med = statistics.median(scores)
            stdev = statistics.stdev(scores) if len(scores) > 1 else 0
            
            # Histogram (bins of 10%)
            bins = [0] * 10
            for s in scores:
                idx = min(int(s / 10), 9)
                bins[idx] += 1
            histogram = [{"range": f"{i*10}-{i*10+10}", "count": bins[i]} for i in range(10)]
            
            return {
                "average": round(avg, 2),
                "median": round(med, 2),
                "standard_deviation": round(stdev, 2),
                "count": len(scores),
                "histogram": histogram
            }
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()


@router.get("/exams/results-detail", summary="Fetch detailed student results for an exam including absent students")
async def get_exam_results_detail(exam_id: int):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            # Query for all results related to this exam directly from studentresult
            query = """
                SELECT 
                    sr.studentId, 
                    s.xId as studentXId, 
                    s.name as studentName, 
                    sr.currentMark as mark, 
                    sr.takeTime, 
                    sr.status
                FROM studentresult sr
                JOIN student s ON sr.studentId = s.id
                WHERE sr.examId = %s
                GROUP BY sr.studentId
            """
            cursor.execute(query, (exam_id,))
            results = cursor.fetchall()
            
            # Enrich with question counts (Answered, True, False, Not Corrected)
            for res in results:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN answer IS NOT NULL THEN 1 ELSE 0 END) as answered,
                        SUM(CASE WHEN currentMark >= (examDataMark/2) AND examDataMark > 0 THEN 1 ELSE 0 END) as true_ans,
                        SUM(CASE WHEN currentMark < (examDataMark/2) AND examDataMark > 0 THEN 1 ELSE 0 END) as false_ans
                    FROM studentresult 
                    WHERE examId = %s AND studentId = %s
                """, (exam_id, res['studentId']))
                counts = cursor.fetchone()
                res['answered'] = counts['answered'] or 0
                res['true_ans'] = counts['true_ans'] or 0
                res['false_ans'] = counts['false_ans'] or 0
                res['not_corrected'] = (counts['total'] or 0) - (counts['answered'] or 0)
                res['startTime'] = None # Placeholder since it's not in studentresult
                res['studentOrder'] = 0 # Placeholder
            
            return results
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()

@router.get("/exams/grid", summary="Fetch exam list with metadata for the grid view")
async def get_exam_grid(
    username: str = None,
    faculty_id: int = None,
    major_id: int = None,
    course_id: int = None,
    class_id: int = None,
    from_date: str = None,
    to_date: str = None
):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            # Join with teacherlink using teacherLinkId, not teacherId
            query = """
                SELECT DISTINCT SUBSTRING_INDEX(e.name, ' - ', 1) as name, 
                       f.name as grade, 
                       c.name as material, 
                       cl.name as division, 
                       e.date, 
                       e.status, 
                       e.id
                FROM exam e
                LEFT JOIN teacherlink tl ON e.teacherLinkId = tl.id
                LEFT JOIN faculty f ON tl.facultyId = f.id
                LEFT JOIN course c ON tl.courseId = c.id
                LEFT JOIN class cl ON tl.classId = cl.id
                WHERE 1=1
            """
            params = []
            if username:
                cursor.execute("SELECT id FROM employee WHERE name = %s", (username,))
                emp = cursor.fetchone()
                if emp:
                    # Filter by the teacherId in the teacherlink table linked via teacherLinkId
                    query += " AND tl.teacherId = %s"
                    params.append(emp['id'])
            
            if faculty_id:
                query += " AND tl.facultyId = %s"
                params.append(faculty_id)
            if major_id:
                query += " AND tl.majorId = %s"
                params.append(major_id)
            if course_id:
                query += " AND tl.courseId = %s"
                params.append(course_id)
            if class_id:
                query += " AND tl.classId = %s"
                params.append(class_id)
            if from_date:
                query += " AND DATE(e.date) >= %s"
                params.append(from_date)
            if to_date:
                query += " AND DATE(e.date) <= %s"
                params.append(to_date)
            
            cursor.execute(query, params)
            exams = cursor.fetchall()
            
            # Enrich with count data
            for exam in exams:
                cursor.execute("SELECT COUNT(DISTINCT studentId) as applicants FROM studentresult WHERE examId = %s", (exam['id'],))
                exam['applicants'] = cursor.fetchone()['applicants']
                cursor.execute("SELECT COUNT(DISTINCT id) as examinees FROM result WHERE examId = %s", (exam['id'],))
                exam['examinees'] = cursor.fetchone()['examinees']
                
            return exams
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()

@router.get("/{table}/list", summary="Fetch list of items for filters with relational filtering")
async def get_list(
    table: str, 
    username: str = None, 
    faculty_id: int = None, 
    major_id: int = None, 
    course_id: int = None, 
    class_id: int = None
):
    valid_tables = ["faculty", "major", "course", "class", "exam"]
    if table not in valid_tables:
        raise HTTPException(status_code=404, detail="Invalid table")
    
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            params = []
            where_clauses = []
            # 1. Instructor Filtering
            if username:
                cursor.execute("SELECT id FROM employee WHERE name = %s", (username,))
                emp = cursor.fetchone()
                if emp:
                    emp_id = emp['id']
                    cursor.execute("SELECT facultyId, majorId, courseId, classId FROM teacherlink WHERE teacherId = %s", (emp_id,))
                    links = cursor.fetchall()
                    if links:
                        link_col = f"{table}Id"
                        ids = list(set(str(l[link_col]) for l in links if l.get(link_col)))
                        if ids:
                            where_clauses.append(f"id IN ({','.join(ids)})")
                        else:
                            # Instructor has no links to this specific table, force empty result
                            where_clauses.append("id IN (-1)")

            # 2. Hierarchical Filter pass-through
            if faculty_id and table == "major":
                where_clauses.append("id IN (SELECT majorId FROM teacherlink WHERE facultyId = %s)")
                params.append(faculty_id)
            elif major_id and table == "course":
                where_clauses.append("id IN (SELECT courseId FROM teacherlink WHERE majorId = %s)")
                params.append(major_id)
            elif course_id and table == "class":
                where_clauses.append("id IN (SELECT classId FROM teacherlink WHERE courseId = %s)")
                params.append(course_id)
            elif class_id and table == "exam":
                # Exams link to classes via examdata(examId) -> ???
                # Actually, based on teacherlink, let's filter exams directly by teacherId if possible,
                # but for class-based filter: check exam table for teacherId match.
                where_clauses.append("teacherId IN (SELECT teacherId FROM teacherlink WHERE classId = %s)")
                params.append(class_id)
            
            query = f"SELECT id, name FROM {table}"
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()

@router.get("/bank-coverage", summary="LO coverage in the question bank")
async def get_bank_coverage(sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    try:
        sqlite_cursor = sqlite_db.cursor()
        sqlite_cursor.execute("""
            SELECT lo.name as lo, COUNT(q.question_id) as count
            FROM learning_outcomes lo
            LEFT JOIN questions q ON lo.id = q.learning_outcome_id
            GROUP BY lo.id
        """)
        rows = sqlite_cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executive-stats", summary="Fetch high-level strategic data for the Executive Dashboard")
async def get_executive_stats(lang: str = "en", sqlite_db: sqlite3.Connection = Depends(get_questai_db)):
    # 1. Calculate Prep Hours Saved (from SQLite)
    sqlite_cursor = sqlite_db.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) as q_count FROM questions")
    total_questions = sqlite_cursor.fetchone()['q_count']
    hours_saved = int(total_questions * 0.25)
    
    # 2. Fetch Performance Metrics from MySQL (schooldemo12)
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            # Accreditation Readiness: Average performance across all exams
            cursor.execute("SELECT AVG(currentMark * 100 / NULLIF(examDataMark, 0)) as avg_perf FROM studentresult")
            acc_readiness = cursor.fetchone()['avg_perf'] or 0.0
            
            # Intervention Efficiency
            intervention_gain = 12.0 
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()
    
    if lang == "ar":
        return {
            "prep_hours_saved": {"value": hours_saved, "unit": "ساعة", "description": "مكاسب الكفاءة عبر إنشاء الاختبارات المؤتمت بواسطة الذكاء الاصطناعي."},
            "accreditation_readiness": {"value": round(acc_readiness, 1), "unit": "%", "description": "إتقان مخرجات التعلم المعينة لامتثال برنامج ABET."},
            "intervention_efficiency": {"value": intervention_gain, "unit": "% زيادة", "description": "تحسن نتائج الطلاب المعرضين للخطر بعد التوجيه."}
        }
    else:
        return {
            "prep_hours_saved": {"value": hours_saved, "unit": "hrs", "description": "Efficiency gain via AI-automated exam generation."},
            "accreditation_readiness": {"value": round(acc_readiness, 1), "unit": "%", "description": "Mapped LO mastery for ABET program compliance."},
            "intervention_efficiency": {"value": intervention_gain, "unit": "% gain", "description": "Improvement in at-risk student outcomes after coaching."}
        }
\


@router.get("/exams/trend", summary="Fetch average mark trends for filtered exams")
async def get_exams_trend(
    username: str = None,
    course_id: str = None,
    from_date: str = None,
    to_date: str = None
):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            # Build base query with filters
            query = """
                SELECT e.name as exam_name, e.date, AVG(sr.currentMark / NULLIF(sr.examDataMark, 0) * 100) as avg_mark
                FROM studentresult sr
                JOIN exam e ON sr.examId = e.id
                WHERE sr.examDataMark > 0
            """
            params = []
            
            # Simple filter building
            if course_id: query += " AND e.courseId = %s"; params.append(course_id)
            if from_date: query += " AND e.date >= %s"; params.append(from_date)
            if to_date: query += " AND e.date <= %s"; params.append(to_date)
            
            query += " GROUP BY e.id ORDER BY e.date ASC"
            
            cursor.execute(query, params)
            trend_data = cursor.fetchall()
            
            return [{"date": str(row['date']), "exam": row['exam_name'], "avg": round(float(row['avg_mark'] or 0), 2)} for row in trend_data]
    finally:
        mysql_conn.close()


@router.get("/students/risk-summary", summary="Get engagement and risk summary for all students")
async def get_student_risk_summary(course_id: str = None):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            # Query: Calculate student performance (average mark) and attendance (participation)
            query = """
                SELECT s.id, s.name, 
                       AVG(sr.currentMark / NULLIF(sr.examDataMark, 0) * 100) as avg_mark,
                       COUNT(sr.examId) as exam_count
                FROM student s
                JOIN studentresult sr ON s.id = sr.studentId
                GROUP BY s.id
            """
            cursor.execute(query)
            students = cursor.fetchall()
            
            risk_summary = {"stable": 0, "at_risk": 0, "critical": 0}
            
            for s in students:
                mark = float(s['avg_mark'] or 0)
                if mark < 50 or s['exam_count'] < 2:
                    risk_summary["critical"] += 1
                elif mark < 70:
                    risk_summary["at_risk"] += 1
                else:
                    risk_summary["stable"] += 1
            
            return risk_summary
    finally:
        mysql_conn.close()

@router.get('/exams/student-result-details', summary='Fetch detailed student results for a specific student exam')
async def get_student_result_details(exam_id: int, student_id: int):
    mysql_conn = get_online_exam_db_connection()
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute('SELECT s.name as studentName, s.xId as studentXId, r.currentMark as mark FROM result r JOIN student s ON r.studentId = s.id WHERE r.examId = %s AND r.studentId = %s', (exam_id, student_id))
            summary = cursor.fetchone()
            if not summary: raise HTTPException(status_code=404, detail='No result found')
            try:
                cursor.execute("""
                    SELECT
                        b.title as questionText,
                        b.answers,
                        ed.correct as correctIndex,
                        sr.examDataMark as questionMark,
                        sr.currentMark as studentMark,
                        sr.answer as studentAnswerJson
                    FROM studentresult sr
                    JOIN examdata ed ON sr.examDataId = ed.id
                    JOIN bank b ON ed.bankId = b.id
                    WHERE sr.examId = %s AND sr.studentId = %s
                """, (exam_id, student_id))
                raw_details = cursor.fetchall()
                
                details = []
                for d in raw_details:
                    ans_idx = None
                    ans_text = None
                    try:
                        import json
                        parsed_ans = json.loads(d['studentAnswerJson'])
                        if isinstance(parsed_ans, list) and len(parsed_ans) > 0:
                            ans_idx = parsed_ans[0].get('index')
                            ans_text = parsed_ans[0].get('text')
                    except Exception:
                        pass
                    
                    details.append({
                        **d,
                        'answerIndex': ans_idx,
                        'answerText': ans_text,
                        'status': 'correct' if d['studentMark'] >= d['questionMark'] else 'wrong'
                    })
            except Exception as e:
                print(f"DEBUG SQL ERROR: {e}")
                raise e
            true_ans = sum(1 for d in details if d['status'] == 'correct')
            false_ans = sum(1 for d in details if d['status'] == 'wrong')
            not_corrected = sum(1 for d in details if d['status'] == 'notCorrected')
            unanswered = sum(1 for d in details if d['answerText'] is None or d['answerText'] == '')
            return {'summary': {**summary, 'true_ans': true_ans, 'false_ans': false_ans, 'not_corrected': not_corrected, 'unanswered': unanswered}, 'details': details}
    except Exception as e:
        import traceback; traceback.print_exc(); raise HTTPException(status_code=500, detail=str(e))
    finally:
        mysql_conn.close()
