-- Create university_majors table
CREATE TABLE IF NOT EXISTS university_majors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
