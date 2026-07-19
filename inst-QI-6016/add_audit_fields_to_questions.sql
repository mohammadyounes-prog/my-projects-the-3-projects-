ALTER TABLE questions ADD COLUMN approved_by_user_id INTEGER;
  ALTER TABLE questions ADD COLUMN approved_at TEXT;
  ALTER TABLE questions ADD COLUMN rejected_by_user_id INTEGER;
  ALTER TABLE questions ADD COLUMN rejected_at TEXT;
  ALTER TABLE questions ADD COLUMN edited_by_user_id INTEGER;
  ALTER TABLE questions ADD COLUMN edited_at TEXT;
  ALTER TABLE questions ADD COLUMN deleted_by_user_id INTEGER;
  ALTER TABLE questions ADD COLUMN deleted_at TEXT;