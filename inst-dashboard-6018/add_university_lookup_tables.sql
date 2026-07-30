-- Create university_courses table
CREATE TABLE IF NOT EXISTS university_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Create university_materials table
CREATE TABLE IF NOT EXISTS university_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Create university_semesters table
CREATE TABLE IF NOT EXISTS university_semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
