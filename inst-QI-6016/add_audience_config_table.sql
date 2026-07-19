CREATE TABLE audience_field_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audience_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE(audience_type, field_name)
);