# Session 4 Checkpoint

## Goal
Fix the integration between the `questionretrieval` and `online-exam` projects.

## Problem
The `questionretrieval` backend returns a `500 Internal Server Error` when the "push questions to bank" button is clicked in the frontend.

## Diagnosis
- The error is caused by the `online-exam` API returning a permission error: `{"status":false,"error":"you need rules exam-can-add"}`.
- This happens because the user with `teacherId = 11` in the `online-exam` database does not have the `exam-can-add` permission.

## Fix
The following SQL command was provided to be executed on the `schooldemo12` database to grant the necessary permission:
```sql
UPDATE employee 
SET 
    rules = CONCAT(rules, ',exam-can-add') 
WHERE 
    id = 11 
    AND rules NOT LIKE '%exam-can-add%';
```

## Current Status
- Waiting for the user to confirm that the SQL command has been executed successfully.
- Waiting for the user to re-test the "push questions to bank" functionality and report the result.
- The user reported difficulty copying text from the command line.
