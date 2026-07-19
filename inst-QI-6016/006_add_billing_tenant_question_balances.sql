CREATE TABLE IF NOT EXISTS billing_tenant_question_balances (
  tenant_id INTEGER NOT NULL REFERENCES tenants(id),
  audience_type TEXT NOT NULL,
  balance INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT,
  PRIMARY KEY (tenant_id, audience_type)
);
