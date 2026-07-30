# Checkpoint: Core Billing Logic Implementation

This file summarizes the work completed on the new, isolated billing feature.

## Summary of Changes:

1.  **New Database Tables Created:**
    *   A new migration file, `005_add_billing_products.sql`, was created to define a table for managing purchasable bundles and subscriptions, each tied to a specific `audience_type`.
    *   A new migration file, `006_add_billing_tenant_question_balances.sql`, was created to define a table for tracking a tenant's question balance for each distinct audience type.

2.  **Database Migration:**
    *   The `run_migrations.py` script was updated to include the two new migration files.
    *   The script was executed, successfully creating the `billing_products` and `billing_tenant_question_balances` tables in the database.

3.  **Backend Logic Implemented:**
    *   The primary question generation endpoint (`/generate` in `backend/main.py`) was replaced with a new version.
    *   This new version now performs the core billing logic:
        *   It checks the `billing_tenant_question_balances` table for the correct tenant and audience type.
        *   It raises a `402 Payment Required` error if the balance is insufficient.
        *   Upon successful question generation, it deducts the number of questions from the balance and creates a `debit` entry in the `billing_events` table.
        *   All database operations are handled within a single transaction to ensure data integrity.

## Next Steps:

The next logical step is to build the UI for an administrator to manage the new `billing_products` table (create, edit, and view bundles/subscriptions).

---

## Step 1: Admin UI for Billing Products - DONE

- **Backend:** Added a full set of CRUD (Create, Read, Update, Delete) API endpoints to `backend/admin_billing.py` to manage the `billing_products` table.
- **Frontend:** Modified `admin.html` to include a new "Billing Products" section.
  - Added a table to list all products.
  - Added a modal with a form for creating and editing products, including fields for audience type, product type (bundle/subscription), price, and question quota.
  - Implemented the JavaScript logic to connect the UI to the new backend endpoints.
