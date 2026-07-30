-- Add school_type_id to questions table
ALTER TABLE questions ADD COLUMN school_type_id INTEGER;

-- Add subject_id to questions table
ALTER TABLE questions ADD COLUMN subject_id INTEGER;

-- Add year_id to questions table
ALTER TABLE questions ADD COLUMN year_id INTEGER;

-- Add question_type_id to questions table
ALTER TABLE questions ADD COLUMN question_type_id INTEGER;

-- Add major_id to questions table
ALTER TABLE questions ADD COLUMN major_id INTEGER;

-- Add course_id to questions table
ALTER TABLE questions ADD COLUMN course_id INTEGER;

-- Add material_id to questions table
ALTER TABLE questions ADD COLUMN material_id INTEGER;

-- Add semester_id to questions table
ALTER TABLE questions ADD COLUMN semester_id INTEGER;

-- Add company_id to questions table
ALTER TABLE questions ADD COLUMN company_id INTEGER;

-- Add department_id to questions table
ALTER TABLE questions ADD COLUMN department_id INTEGER;

-- Add job_role_id to questions table
ALTER TABLE questions ADD COLUMN job_role_id INTEGER;
