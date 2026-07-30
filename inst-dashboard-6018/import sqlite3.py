import sqlite3, os

DB = r'backend\app.db'  # change if your DB file is elsewhere

def run_sql(path):
 if not os.path.exists(path):
  print(f'Skipping missing {path}')
  return
  with open(path, 'r', encoding='utf-8') as f:
  sql = f.read()
  con = sqlite3.connect(DB)
  try:
  con.executescript(sql)
  con.commit()
  print(f'Applied {path}')
  finally:
  con.close()

  if name == 'main':
  for p in ['create_countries_tables.sql', 'seed_countries.sql', 'seed_tenant_countries_example.sql']:
  run_sql(p)
  # Verify
  con = sqlite3.connect(DB)
  cur = con.cursor()
  try:
  tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'")]
  countries = cur.execute("select count(*) from countries").fetchone()[0] if 'countries' in tables else 0
  mappings = cur.execute("select count() from tenant_countries").fetchone()[0] if 'tenant_countries' in tables else 0
  print('Tables:', tables)
  print('Countries count:', countries)
  print('Tenant-country mappings:', mappings)
  finally:
  con.close()
  print('Done.')
