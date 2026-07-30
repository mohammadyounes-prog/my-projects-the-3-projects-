-- Helpful indexes to speed up queries and filters
CREATE INDEX IF NOT EXISTS idx_questions_tenant_user ON questions(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_questions_date_created ON questions(date_created);
CREATE INDEX IF NOT EXISTS idx_questions_approved_by ON questions(approved_by);
CREATE INDEX IF NOT EXISTS idx_questions_rejected_by ON questions(rejected_by);
CREATE INDEX IF NOT EXISTS idx_questions_edited_by ON questions(edited_by);
CREATE INDEX IF NOT EXISTS idx_questions_deleted_by ON questions(deleted_by);

