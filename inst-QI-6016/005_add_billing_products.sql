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
