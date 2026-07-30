-- Create normalized countries and tenant_countries tables
-- countries: country_id (e.g., AFG1), name unique
-- tenant_countries: mapping between tenants and countries

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS countries (
  country_id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tenant_countries (
  tenant_id INTEGER NOT NULL,
  country_id TEXT NOT NULL,
  PRIMARY KEY (tenant_id, country_id),
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY (country_id) REFERENCES countries(country_id) ON DELETE CASCADE
);

COMMIT;

