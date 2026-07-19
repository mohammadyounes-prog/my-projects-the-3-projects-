import sqlite3
import os
from pathlib import Path

DB_FILE = "questions.db"
DB_PATH = os.getenv('DB_PATH', str(Path(__file__).resolve().parent / DB_FILE))

sql_statements = """
-- Create currencies table
CREATE TABLE IF NOT EXISTS currencies (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  decimal_places INTEGER NOT NULL DEFAULT 2,
  is_active INTEGER NOT NULL DEFAULT 1
);

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create countries and tenant_countries tables
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

-- Create billing_products table
CREATE TABLE IF NOT EXISTS billing_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_type TEXT NOT NULL CHECK(product_type IN ('bundle', 'subscription')),
  audience_type TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  price_cents INTEGER NOT NULL,
  currency_code TEXT NOT NULL REFERENCES currencies(code),
  questions_quota INTEGER NOT NULL,
  duration_days INTEGER, -- NULL for one-time bundles, number of days for subscriptions
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create billing_events table
CREATE TABLE IF NOT EXISTS billing_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  task_id INTEGER,
  model TEXT,
  quantity_questions INTEGER NOT NULL DEFAULT 0,
  unit_credits INTEGER NOT NULL DEFAULT 1,
  total_credits INTEGER NOT NULL DEFAULT 0,
  currency TEXT,
  unit_price_cents INTEGER,
  total_price_cents INTEGER,
  event_type TEXT NOT NULL CHECK(event_type IN ('debit','credit','subscription','overage','refund')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  metadata TEXT
);

-- Add column to billing_products
ALTER TABLE billing_products ADD COLUMN tenant_id INTEGER;
"""

def apply_schema_fix():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"Applying schema fix to database at: {DB_PATH}")
        cursor.executescript(sql_statements)
        conn.commit()
        print("Schema fix applied successfully.")
    except sqlite3.Error as e:
        print(f"Error applying schema fix: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_schema_fix()