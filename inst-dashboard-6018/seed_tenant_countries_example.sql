-- Optional: Seed tenant_countries mapping for tenant_id = 1 to all countries
-- Run only if you want every country enabled for tenant 1 by default.

BEGIN TRANSACTION;

INSERT OR IGNORE INTO tenant_countries(tenant_id, country_id)
SELECT 1 AS tenant_id, country_id FROM countries;

COMMIT;

