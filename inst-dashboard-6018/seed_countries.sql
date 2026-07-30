-- Seed countries table with IDs formed by first 3 letters (A-Z only) + serial number starting at 1
-- The list mirrors backend/main.py /lookup/countries

BEGIN TRANSACTION;

WITH raw_names(name) AS (
  VALUES
    ('Afghanistan'), ('Albania'), ('Algeria'), ('Andorra'), ('Angola'), ('Antigua and Barbuda'), ('Argentina'), ('Armenia'),
    ('Australia'), ('Austria'), ('Azerbaijan'), ('Bahamas'), ('Bahrain'), ('Bangladesh'), ('Barbados'), ('Belarus'), ('Belgium'),
    ('Belize'), ('Benin'), ('Bhutan'), ('Bolivia'), ('Bosnia and Herzegovina'), ('Botswana'), ('Brazil'), ('Brunei'), ('Bulgaria'),
    ('Burkina Faso'), ('Burundi'), ('Cabo Verde'), ('Cambodia'), ('Cameroon'), ('Canada'), ('Central African Republic'), ('Chad'),
    ('Chile'), ('China'), ('Colombia'), ('Comoros'), ('Congo (Brazzaville)'), ('Congo (Kinshasa)'), ('Costa Rica'), ('Croatia'),
    ('Cuba'), ('Cyprus'), ('Czechia'), ('Denmark'), ('Djibouti'), ('Dominica'), ('Dominican Republic'), ('Ecuador'), ('Egypt')
    -- Extend with full list from backend if needed
), ordered AS (
  SELECT name, ROW_NUMBER() OVER (ORDER BY name) AS rn FROM raw_names
), prepped AS (
  SELECT name,
         UPPER(SUBSTR(REPLACE(REPLACE(REPLACE(REPLACE(name, ' ', ''), '(', ''), ')', ''), '-', ''), 1, 3)) AS pref,
         rn
  FROM ordered
)
INSERT OR IGNORE INTO countries(country_id, name)
SELECT pref || CAST(rn AS TEXT) AS country_id, name FROM prepped;

COMMIT;

