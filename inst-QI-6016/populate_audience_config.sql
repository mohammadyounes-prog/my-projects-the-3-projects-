-- Default fields for 'school'
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'school_type', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'subject', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'year', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'university', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'major', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'company', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'department', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('school', 'job_role', 0);

-- Default fields for 'university'
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'school_type', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'subject', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'year', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'university', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'major', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'company', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'department', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('university', 'job_role', 0);

-- Default fields for 'company'
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'school_type', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'subject', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'year', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'university', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'major', 0);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'company', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'department', 1);
INSERT OR IGNORE INTO audience_field_config (audience_type, field_name, is_enabled) VALUES ('company', 'job_role', 1);
