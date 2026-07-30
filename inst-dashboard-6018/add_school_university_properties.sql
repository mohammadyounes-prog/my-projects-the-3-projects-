-- add_school_university_properties.sql
INSERT INTO property_types (name, api_name, audience_type) VALUES
('School Type', 'school_types', 'school'),
('Subject', 'school_subjects', 'school'),
('Year', 'school_years', 'school'),
('Major', 'university_majors', 'university'),
('Course', 'university_courses', 'university'),
('Material', 'university_materials', 'university'),
('Semester', 'university_semesters', 'university');
