-- Adds tenant_id to generation_tasks for multi-tenant tracking
ALTER TABLE generation_tasks ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);

