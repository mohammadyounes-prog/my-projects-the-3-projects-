# Checkpoint: Admin/Superadmin Logic Refactoring - Part 1

## Summary

This checkpoint marks the first step in refactoring the backend API to cleanly separate the logic for regular admins (`is_admin`) and superadmins (`is_super_admin`), as requested.

## Changes Made

1.  **Refactored Tenant List Endpoint (`GET /admin/tenants`):**
    *   A new function, `get_tenant_hierarchy`, was created in `backend/database.py` to encapsulate the complex recursive query for fetching a regular admin's tenants (their own tenant and all its descendants).
    *   The main `read_tenants` endpoint in `backend/admin.py` was simplified to a clean `if/else` block that calls either `get_all_tenants()` for superadmins or the new `get_tenant_hierarchy()` for regular admins.

## Next Steps

Continue refactoring other endpoints (e.g., for user management, model management) to apply the same clear separation of logic.
