# QuestAI local stack (`inst-QI-6016`)

Run the API + static frontend locally so interactive **generate** demos work without production secrets. Prefer the **dummy** generation model (no live LLM key).

For the **full three-app suite** (website + dashboard + QuestAI + MySQL SSO), from the monorepo root:

```bash
docker compose -f docker-compose.local.yml up -d   # MySQL :3307 / schooldemo12
./scripts/run-local.sh start                       # or start each process manually
# Login everywhere: demo / demo123
```

**Port note:** Suite docs historically use Auth API `:8000`. If something else already owns `:8000` (e.g. SurrealDB), local env uses **`:8001`** — keep `inst-QI-6016/backend/.env` `PORT`, website `NEXT_PUBLIC_API_URL`, and `frontend/config.js` in sync.

## Suite ports

| App | Port | Notes |
|-----|------|--------|
| Website hub | **6015** | `NEXT_PUBLIC_QUESTION_RETRIEVAL_URL` → QuestAI |
| QuestAI frontend | **6016** | `python -m http.server` in `frontend/` |
| QuestAI API | **8001** (or **8000**) | `python run_server.py` |
| Dashboard API | **6018** | `uvicorn backend.main:app` |
| Dashboard UI | **6019** | `npx serve -s build -l 6019` |
| MySQL SSO | **3307** | `docker-compose.local.yml` → `schooldemo12` |

## One-time setup

From the monorepo root (or `inst-QI-6016`):

```bash
cd inst-QI-6016
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# Edit backend/.env if needed (SECRET_KEY, PORT, ONLINE_EXAM_MYSQL_*)
```

## Seed the database

Creates `questions.db` (gitignored), lookup rows, a demo tenant/teacher, and a **dummy** generation model. Safe to re-run.

```bash
cd inst-QI-6016
source .venv/bin/activate
python scripts/seed_local_demo.py
# After MySQL is up, link demo → employee id 1 for SSO:
python ../scripts/link_demo_sso.py
```

**Demo login** (after seed):

| Field | Value |
|-------|--------|
| Username | `demo` |
| Password | `demo123` |

Select model **Dummy Generator** (`model_api_name`: `dummy`) in the generate UI. The backend already short-circuits dummy models and returns fake questions — no `GOOGLE_API_KEY` / `OPENAI_API_KEY` required.

## Start API

```bash
cd inst-QI-6016
source .venv/bin/activate
python run_server.py
```

Listens on `PORT` / `BACKEND_BASE_URL` from `backend/.env`.

## Serve frontend (`:6016`)

In a second terminal:

```bash
cd inst-QI-6016/frontend
python3 -m http.server 6016
```

Open http://localhost:6016 (login → generate). Frontend `config.js` defaults local API to `http://127.0.0.1:8001`.

## Notes

- Do **not** commit `backend/.env` or `questions.db` (root `.gitignore` ignores `.env` and `*.db`).
- Real Gemini/OpenAI models need keys in `.env` (or per-row `api_key` in `generation_models`).
- `USE_DUMMY_PAYMENT_GATEWAY=true` (default) keeps billing demos offline.
- Online-exam **UI** (`:8080`) is not in this monorepo; MySQL SSO tables are enough for website hub → Dashboard/QuestAI handoff.
