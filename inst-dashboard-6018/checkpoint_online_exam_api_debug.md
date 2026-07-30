## Checkpoint: Online Exam API Debugging

**Date:** November 14, 2025

**Current Status:**
The `questionretrieval` backend is consistently reporting a `500 Internal Server Error` with the message `Network error connecting to Online Exam API` when attempting to create an exam in the `online-exam` application.

**What has been done:**
1.  **`online-exam` frontend authentication bypass:** Temporarily commented out `Auth.resolveRules("exam-can-edit")` in `module.exam.js` (in `online-exam` project) to bypass the login redirect issue. This successfully prevented the redirect.
2.  **`online-exam` API base URL investigation:**
    *   Initially, `ONLINE_EXAM_API_BASE_URL` was set to `http://localhost:8888/admin`.
    *   Analyzed `api.exam.php` and `API.php` (found in `D:\QuestionRetrieval\new-q-bank\TAMS\schooldemo12\system\module\API.php`).
    *   Discovered that `API.php` defines `public static $route = 'api';` and uses `index.php` as the front controller.
    *   Concluded that the correct API base URL should be `http://localhost:8888/index.php/api`.
3.  **User Instruction:** Instructed the user to update their `ONLINE_EXAM_API_BASE_URL` environment variable to `http://localhost:8888/index.php/api`.
4.  **User Confirmation:** User confirmed that `http://localhost:8888/admin` loads in the browser, indicating the `online-exam` web server is running.

**Current Problem:**
The `questionretrieval` backend is still unable to connect to the `online-exam` API, resulting in a `Network error connecting to Online Exam API`. This persists because the user has not yet confirmed if they have applied the suggested change to `ONLINE_EXAM_API_BASE_URL` and provided the corresponding backend logs.

**Next Steps:**
1.  **Await User Confirmation:** Wait for the user to confirm that they have updated the `ONLINE_EXAM_API_BASE_URL` environment variable to `http://localhost:8888/index.php/api`.
2.  **Await Backend Logs:** Request the full backend console output from the `questionretrieval` application *after* the user has applied the environment variable change and re-tested the functionality.
3.  **Analyze New Logs:** Based on the new logs, determine if the network connection issue is resolved or if a new error has emerged.
4.  **Address Authentication (Future):** Once the exam creation is successful, re-address the `online-exam` frontend authentication/authorization (`Auth.resolveRules("exam-can-edit")`) to properly handle cross-application redirects.
