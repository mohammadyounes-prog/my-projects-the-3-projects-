CREATE TABLE IF NOT EXISTS audience_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audience_type TEXT NOT NULL, -- 'school', 'university', or 'company'
    field_name TEXT NOT NULL,    -- e.g., 'employee_age'
    display_name TEXT NOT NULL,  -- e.g., 'Employee Age'
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE(audience_type, field_name)
);

CREATE TABLE IF NOT EXISTS audience_field_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    option_value TEXT NOT NULL,
    FOREIGN KEY (field_id) REFERENCES audience_fields(id) ON DELETE CASCADE
);
