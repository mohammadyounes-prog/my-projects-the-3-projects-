# inst-website-6015 (LMS marketing + hub)

Next.js app for the TDM/LMS suite landing site, login, and SSO hub.

## Getting Started

```bash
cp .env.example .env.local   # optional — defaults match .env.example
npm install
npm run dev                  # http://localhost:6015
```

## Public env (`NEXT_PUBLIC_*`)

| Variable | Default | Hits |
|----------|---------|------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Auth SSO API (`/token`, generate-sso-token) |
| `NEXT_PUBLIC_ONLINE_EXAM_URL` | `http://localhost:8080` | Assessment admin (`/admin`) |
| `NEXT_PUBLIC_DASHBOARD_URL` | `http://localhost:6019` | Dashboard CRA (`/login`) |
| `NEXT_PUBLIC_QUESTION_RETRIEVAL_URL` | `http://localhost:6016` | QuestAI (`/home.html`) |

Defaults are centralized in `src/lib/publicEnv.ts` so missing env never yields `undefined/...` links.

## Scripts

```bash
npm run build
npm run start   # :6015
npm run lint
```
