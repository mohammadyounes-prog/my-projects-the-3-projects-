
CREATE TABLE generation_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_api_name TEXT NOT NULL UNIQUE,
    generation_method TEXT NOT NULL,
    tenant_id INTEGER,
    is_default BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
