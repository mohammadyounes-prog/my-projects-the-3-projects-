-- Description: Adds tenant_id to users and questions tables for multi-tenancy.

  ALTER TABLE users ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);
  ALTER TABLE questions ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);