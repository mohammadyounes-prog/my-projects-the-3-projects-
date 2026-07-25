# QuestAI local stack (`inst-QI-6016`)

Run the API + static frontend locally so interactive **generate** demos work without production secrets. Prefer the **dummy** generation model (no live LLM key).

## Suite ports

| App | Port | Notes |
|-----|------|--------|
| Website hub | **6015** | `NEXT_PUBLIC_QUESTION_RETRIEVAL_URL` → QuestAI |
| QuestAI frontend | **6016** | `python -m http.server` in `frontend/` |
| QuestAI API | **8000** | `python run_server.py` (matches website `NEXT_PUBLIC_API_URL`) |

## One-time setup

From the monorepo root (or `inst-QI-6016`):

```bash
cd inst-QI-6016
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# Edit backend/.env if needed (SECRET_KEY, optional real API keys)
```

## Seed the database

Creates `questions.db` (gitignored), lookup rows, a demo tenant/teacher, and a **dummy** generation model. Safe to re-run.

```bash
cd inst-QI-6016
source .venv/bin/activate
python scripts/seed_local_demo.py
```

Equivalent low-level steps (seed script covers these):

```bash
python setup_database.py          # base schema + lookup seed
# then seed_local_demo.py adds tenants/users/generation_models
```

**Demo login** (after seed):

| Field | Value |
|-------|--------|
| Username | `demo` |
| Password | `demo123` |

Select model **Dummy Generator** (`model_api_name`: `dummy`) in the generate UI. The backend already short-circuits dummy models and returns fake questions — no `GOOGLE_API_KEY` / `OPENAI_API_KEY` required.

## Start API (`:8000`)

```bash
cd inst-QI-6016
source .venv/bin/activate
python run_server.py
```

Listens on `PORT` / `BACKEND_BASE_URL` from `backend/.env` (default **8000**).

## Serve frontend (`:6016`)

In a second terminal:

```bash
cd inst-QI-6016/frontend
python3 -m http.server 6016
```

Open http://localhost:6016 (login → generate). Frontend defaults to API `http://127.0.0.1:8000`.

## Notes

- Do **not** commit `backend/.env` or `questions.db` (root `.gitignore` ignores `.env` and `*.db`).
- Real Gemini/OpenAI models need keys in `.env` (or per-row `api_key` in `generation_models`).
- `USE_DUMMY_PAYMENT_GATEWAY=true` (default) keeps billing demos offline.
- Online-exam MySQL/SSO env vars are optional for generate-only demos.
