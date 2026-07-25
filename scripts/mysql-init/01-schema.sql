-- Minimal schema for local suite login + SSO (not a full TAMS dump).
USE schooldemo12;

CREATE TABLE IF NOT EXISTS employee (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  pass VARCHAR(255) NULL,
  rules TEXT NULL,
  position VARCHAR(100) NULL,
  data TEXT NULL,
  workGroup INT NULL,
  username VARCHAR(255) NULL,
  api_token VARCHAR(255) NULL,
  UNIQUE KEY uq_employee_email (email)
);

CREATE TABLE IF NOT EXISTS sso_sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  token VARCHAR(64) NOT NULL,
  user_id INT NOT NULL,
  expires_at DATETIME NOT NULL,
  UNIQUE KEY uq_sso_token (token),
  KEY idx_sso_expires (expires_at)
);

-- Demo instructor used by SSO handoff (password hash unused for SQLite demo path).
INSERT INTO employee (id, name, email, pass, position, username, workGroup)
VALUES (1, 'Demo Teacher', 'demo@localhost', 'unused-local', 'teacher', 'demo', 3)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  email = VALUES(email),
  username = VALUES(username);
