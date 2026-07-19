-- create_property_types_table.sql
CREATE TABLE IF NOT EXISTS property_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    api_name TEXT NOT NULL UNIQUE,
    audience_type TEXT NOT NULL
);

-- Populate with existing company properties to start
INSERT INTO property_types (name, api_name, audience_type) VALUES
('Education', 'companies', 'company'),
('Department', 'departments', 'company'),
('Job Role', 'job_roles', 'company');
