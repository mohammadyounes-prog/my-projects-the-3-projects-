# Checkpoint: Admin/Superadmin Logic Refactoring - Part 2

## Summary

This checkpoint marks the completion of the main refactoring effort to separate admin and superadmin logic in the backend.

## Changes Made

1.  **Refactored Question List Endpoint (`GET /questions`):**
    *   The logic in `backend/main.py` was clarified to use a single `if/elif/else` block to determine the correct `user_id` and `tenant_id` filters for superadmins, regular admins, and regular users.

2.  **Refactored Tenant Creation Endpoint (`POST /admin/tenants`):**
    *   The logic in `backend/admin.py` was simplified to remove redundant checks and clarify how a tenant's `parent_id` is assigned based on the creator's role.

3.  **Reviewed User List Endpoint (`GET /admin/users`):**
    *   This endpoint was already following the desired pattern of clean separation and did not require changes.

## Next Steps

The core backend logic is now refactored. I will await further instructions or testing results.