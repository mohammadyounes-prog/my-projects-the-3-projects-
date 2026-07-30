-- Add moderation columns to questions table
ALTER TABLE questions ADD COLUMN approved_by INTEGER;
ALTER TABLE questions ADD COLUMN approved_at TEXT;
ALTER TABLE questions ADD COLUMN rejected_by INTEGER;
ALTER TABLE questions ADD COLUMN rejected_at TEXT;
ALTER TABLE questions ADD COLUMN edited_by INTEGER;
ALTER TABLE questions ADD COLUMN edited_at TEXT;
ALTER TABLE questions ADD COLUMN deleted_by INTEGER;
ALTER TABLE questions ADD COLUMN deleted_at TEXT;

-- Create question_actions history table
CREATE TABLE IF NOT EXISTS question_actions (
  id INTEGER PRIMARY KEY,
  question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  tenant_id INTEGER NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('created','edited','approved','rejected','deleted','restored')),
  actor_user_id INTEGER NOT NULL,
  details TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_question_actions_qid ON question_actions(question_id);
CREATE INDEX IF NOT EXISTS idx_question_actions_tenant_qid ON question_actions(tenant_id, question_id);
CREATE INDEX IF NOT EXISTS idx_question_actions_action ON question_actions(action);
CREATE INDEX IF NOT EXISTS idx_question_actions_created_at ON question_actions(created_at);

