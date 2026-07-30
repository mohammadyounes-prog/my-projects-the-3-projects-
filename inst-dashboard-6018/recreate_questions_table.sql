-- Drop the existing questions table if it exists
DROP TABLE IF EXISTS questions;

-- Create the new questions table with the correct schema
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_creator VARCHAR(100),
    date_created DATE NOT NULL,
    question_text TEXT NOT NULL,
    choice_1 TEXT,
    choice_2 TEXT,
    choice_3 TEXT,
    choice_4 TEXT,
    correct_option TEXT NOT NULL,
    mark INTEGER NOT NULL DEFAULT 0,
    time_seconds INTEGER NOT NULL DEFAULT 0,
    discriminating_factor REAL,
    status TEXT DEFAULT 'pending',
    user_id INTEGER,
    task_id INTEGER,
    difficulty_level_id INTEGER, -- Now nullable
    cognitive_level_id INTEGER, -- Now nullable
    learning_outcome_id INTEGER, -- Now nullable
    question_type_id INTEGER, -- Now nullable
    school_type_id INTEGER, -- Now nullable
    subject_id INTEGER, -- Now nullable
    year_id INTEGER, -- Now nullable
    major_id INTEGER, -- Now nullable
    course_id INTEGER, -- Now nullable
    material_id INTEGER, -- Now nullable
    semester_id INTEGER, -- Now nullable
    company_id INTEGER, -- Now nullable
    department_id INTEGER, -- Now nullable
    job_role_id INTEGER, -- Now nullable
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES generation_tasks(task_id),
    FOREIGN KEY (difficulty_level_id) REFERENCES difficulty_levels(id),
    FOREIGN KEY (cognitive_level_id) REFERENCES cognitive_levels(id),
    FOREIGN KEY (learning_outcome_id) REFERENCES learning_outcomes(id),
    FOREIGN KEY (question_type_id) REFERENCES question_types(id),
    FOREIGN KEY (school_type_id) REFERENCES school_types(id),
    FOREIGN KEY (subject_id) REFERENCES school_subjects(id),
    FOREIGN KEY (year_id) REFERENCES school_years(id),
    FOREIGN KEY (major_id) REFERENCES university_majors(id),
    FOREIGN KEY (course_id) REFERENCES university_courses(id),
    FOREIGN KEY (material_id) REFERENCES university_materials(id),
    FOREIGN KEY (semester_id) REFERENCES university_semesters(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_role_id) REFERENCES job_roles(id)
);
