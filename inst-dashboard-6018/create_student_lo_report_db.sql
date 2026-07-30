CREATE TABLE IF NOT EXISTS student_lo_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    question_number INTEGER,
    question_text TEXT,
    questions_answers TEXT,
    student_answer TEXT,
    correct_answer TEXT,
    student_mark REAL,
    max_mark REAL,
    is_correct TEXT,
    exam_data_id INTEGER,
    objective TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);