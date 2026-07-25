# Implementation tickets

Status legend: `todo` | `in_progress` | `done` | `blocked` | `deferred`

**GitHub is the tracker; this file is the spec.**  
Map: [`ISSUE_MAP.md`](ISSUE_MAP.md) · Sync rules: [`ISSUE_SYNC.md`](ISSUE_SYNC.md)

Update **Status** here when dispatching, and mirror via `gh issue` (comment / close / remove `deferred`) per `ISSUE_SYNC.md`.

---

## DG — Design guardian

### DG-1 — Token adoption notes
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#2](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/2) |
| **Agent** | Design guardian |
| **parallel** | no (run first) |
| **Depends on** | — |

**Problem:** Three apps need a clear import/mirror path for `--suite-*` without forking hex.

**Work:**
1. Keep [`design-system/tokens.css`](../design-system/tokens.css) as source of truth.
2. Add `design-system/ADOPTION_NOTES.md` (or a short section in the contract) with exact steps for Website (Tailwind/`globals.css`), Dashboard (`App.css` aliases), QuestAI (`frontend/css/suite-tokens.css` copy or build step).
3. List forbidden patterns (Inter as display, purple themes, shadows beyond suite budget).

**Acceptance:**
- [x] Adoption notes exist and name concrete files per app (`design-system/ADOPTION_NOTES.md`)
- [x] No product UI code required for this ticket

---

## Phase A — Website (`inst-website-6015`)

### A1 — Load suite fonts
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#3](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/3) |
| **Agent** | Website |
| **parallel** | ok with A2 |
| **Depends on** | DG-1 recommended |

**Work:** Load Space Grotesk, Plus Jakarta Sans, IBM Plex Sans Arabic, Cairo (via `next/font` and/or Google Fonts). Wire Tailwind `fontFamily` to suite display/body. Remove Inter as the intended display stack.

**Files:** `src/app/layout.tsx`, `src/app/[lang]/layout.tsx`, `src/app/globals.css`, `tailwind.config.js`

**Acceptance:**
- [x] Computed font on hero/headings is suite display family
- [x] Arabic pages load Arabic-capable family
- [x] QA refresh: `website-home-en-desktop.png`, `website-home-ar-desktop.png`

---

### A2 — Mirror suite tokens into Tailwind / CSS
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#4](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/4) |
| **Agent** | Website |
| **parallel** | ok with A1 |
| **Depends on** | DG-1 |

**Work:** Map `--suite-*` into `:root` / Tailwind theme (`primary`, surfaces, radii, shadows). Prefer referencing `design-system/tokens.css` values (import or copy with comment “synced from design-system”).

**Files:** `globals.css`, `tailwind.config.js`

**Acceptance:**
- [x] `--suite-primary` (or Tailwind color) equals `#2c5282`
- [x] Components can use theme tokens instead of ad-hoc sky/slate where touched later

---

### A3 — Restyle hub to marketing brand
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#5](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/5) |
| **Agent** | Website |
| **parallel** | no |
| **Depends on** | A1, A2 |

**Work:** Restyle [`hub/page.tsx`](../inst-website-6015/src/app/[lang]/hub/page.tsx) to suite gateway density: marketing-aligned surfaces, suite cards, CTA verb “Open” (i18n). Remove blue “Coming Soon!” / Gemini `data-test-id` debug strip. Translate all hub strings EN+AR.

**Acceptance:**
- [x] No Coming Soon full-bleed bar
- [x] Hub EN and AR both translated
- [x] Visual language matches home primary/fonts
- [x] QA refresh: `website-hub-en-desktop.png` (+ add `website-hub-ar-desktop.png`)

---

### A4 — Fix dead nav / footer / CTAs
| Field | Value |
|-------|--------|
| **Status** | in_progress |
| **GitHub** | [#6](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/6) |
| **Agent** | Website |
| **parallel** | ok with A5/A6 after A3 or independently |
| **Depends on** | — |

**Work:** Fix or remove dead `#about`/`#solutions`/`#downloads`/`#contact` nav; footer `href="#"`; inert CTA buttons. Prefer real routes (`/solutions`) or remove entries. Do not leave primary CTAs as no-ops.

**Files:** `Header.tsx`, `Footer.tsx`, `CallToActionSection.tsx`, `HeroSection.tsx` as needed

**Acceptance:**
- [x] No primary-path dead `#` CTAs on home/solutions/header/footer
- [x] QA refresh: `website-home-en-desktop.png`, `website-solutions-en-desktop.png`

---

### A5 — Login chrome + env example
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#7](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/7) |
| **Agent** | Website |
| **parallel** | ok with A4 |
| **Depends on** | A1, A2 recommended |

**Work:** Align login page header/chrome with marketing sticky pattern. Add `.env.example` documenting `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_ONLINE_EXAM_URL`, `NEXT_PUBLIC_DASHBOARD_URL`, `NEXT_PUBLIC_QUESTION_RETRIEVAL_URL`. Optional: replace `alert()` on login errors with inline banner (suite danger color) — preferred but not blocking if timeboxed.

**Files:** `login/page.tsx`, `.env.example`

**Acceptance:**
- [x] Login visually consistent with suite header treatment
- [x] `.env.example` present with the four public URLs
- [x] QA refresh: `website-login-en-desktop.png`

---

### A6 — SSR lang/dir + missing i18n keys
| Field | Value |
|-------|--------|
| **Status** | done |
| **GitHub** | [#8](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/8) |
| **Agent** | Website |
| **parallel** | ok with A4 |
| **Depends on** | A3 for hub keys |

**Work:** Ensure `<html lang>` / `dir` come from `[lang]` (fix root `lang="en"` hardcode). Translate tagline “Knowledge is Power”, login/logout/hub keys, testimonials if still hardcoded.

**Files:** `src/app/layout.tsx`, `src/app/[lang]/layout.tsx`, `public/locales/en/common.json`, `public/locales/ar/common.json`, `Header.tsx`, `TestimonialsSection.tsx`

**Acceptance:**
- [x] View-source / first paint `dir=rtl` on `/ar`
- [x] No English-only chrome on AR home/hub for keys covered in audit
- [x] QA refresh: `website-home-ar-desktop.png`, `website-home-ar-mobile.png`

---

### QA-A — Phase A visual gate
| Field | Value |
|-------|--------|
| **Status** | in_progress |
| **GitHub** | [#9](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/9) |
| **Agent** | Visual QA |
| **Depends on** | A1–A6 |

**Refresh:**  
`website-home-en-desktop.png`, `website-home-ar-desktop.png`, `website-home-en-mobile.png`, `website-home-ar-mobile.png`, `website-hub-en-desktop.png`, `website-hub-ar-desktop.png` (new), `website-login-en-desktop.png`, `website-solutions-en-desktop.png`

**Pass if:** Phase A exit criteria in roadmap + contract §8 for website surfaces.

**Visual QA (2026-07-25):** PASS — production `:6015`; hub captured with dummy `localStorage.access_token` (no redirect on load). Suite fonts + `--suite-primary #2c5282`; no debug Coming Soon bar; no primary `#` CTAs. A1–A6 screenshot boxes checked above. Residual (non-blocking): home “Try Assessment/AI Tools” hrefs resolve to `undefined/…` without env; EN mobile sticky header clips hero H1.

---

## Phase B — Dashboard (`inst-dashboard-6018/frontend`)

### B1 — Retoken App.css + load fonts
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#10](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/10) |
| **Agent** | Dashboard |
| **parallel** | no |
| **Depends on** | QA-A pass, DG-1 |

**Work:** Map `--color-primary` / accent to suite tokens; load suite fonts in `public/index.html` (or CSS `@import`). Stop presenting Inter as brand face.

**Acceptance:**
- [ ] Primary surfaces/header use `#2c5282` family
- [ ] Fonts match contract on login/home
- [ ] QA refresh: `dashboard-login-desktop.png`, `dashboard-home-desktop.png`

---

### B2 — Unify Landing and Home
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#11](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/11) |
| **Agent** | Dashboard |
| **parallel** | no |
| **Depends on** | B1 |

**Work:** Collapse `/` and `/home` into one gateway pattern (module cards + suite chrome). SSO may still land on `/home` but UI should not feel like two products. Keep chart/KPI work minimal.

**Files:** `LandingPage.tsx`, `HomePage.tsx`, `App.tsx`

**Acceptance:**
- [ ] One recognizable gateway layout
- [ ] QA refresh: `dashboard-landing-desktop.png`, `dashboard-home-desktop.png`

---

### B3 — Header brand + nav + footer context
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#12](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/12) |
| **Agent** | Dashboard |
| **parallel** | ok with B4 |
| **Depends on** | B1 |

**Work:** Suite brand lockup (TDM / product name, i18n-aware). Reduce or prioritize mega-nav clutter for gateway pages. Footer module label must match context (not always “Corporate HR…”).

**Files:** `Layout.tsx`, `Layout.css`

**Acceptance:**
- [ ] Brand string not English-only two-line hardcode without i18n
- [ ] Footer not wrong-module on educational home

---

### B4 — Fix Back to Hub URL
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#13](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/13) |
| **Agent** | Dashboard |
| **parallel** | ok with B3 |
| **Depends on** | — |

**Work:** Replace `http://localhost:3700` with env-driven website URL (e.g. `REACT_APP_HUB_URL=http://localhost:6015`). Document in `.env.example` under frontend or parent.

**Acceptance:**
- [ ] No `:3700` hardcode in Layout
- [ ] `.env.example` documents hub URL

---

### B5 — RTL layout + login language switcher
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#14](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/14) |
| **Agent** | Dashboard |
| **parallel** | ok with B6 |
| **Depends on** | B1 |

**Work:** Logical CSS pass on layout header/nav. Add language switcher on Login page.

**Files:** `Layout.css`, `Login.tsx`, `LanguageSwitcher.tsx`

**Acceptance:**
- [ ] Login can switch EN/AR
- [ ] Header does not break badly in `dir=rtl`
- [ ] QA refresh: `dashboard-login-desktop.png`, `dashboard-home-mobile.png`

---

### B6 — Contact + Settings stubs
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#15](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/15) |
| **Agent** | Dashboard |
| **parallel** | ok with B5 |
| **Depends on** | B3 recommended |

**Work:** Remove Contact nav link or add a minimal page. Settings: clear stub message (i18n) instead of blank title-only page.

**Acceptance:**
- [ ] No dead `/contact` navigation
- [ ] Settings communicates “not configured” or similar

---

### QA-B — Phase B visual gate
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#16](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/16) |
| **Agent** | Visual QA |
| **Depends on** | B1–B6 |

**Refresh:**  
`dashboard-login-desktop.png`, `dashboard-landing-desktop.png`, `dashboard-home-desktop.png`, `dashboard-home-mobile.png`

**Pass if:** Phase B exit criteria + suite fonts/primary recognizable vs website/QI.

---

## Phase C — QuestAI (`inst-QI-6016/frontend`)

### C1 — Ship shared suite-tokens.css
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#17](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/17) |
| **Agent** | QuestAI |
| **parallel** | no |
| **Depends on** | QA-B pass, DG-1 |

**Work:** Add `frontend/css/suite-tokens.css` synced from `design-system/tokens.css`. Include on `home.html`, `login.html`, and preferably `index.html`. Reduce duplicate `:root` blocks.

**Acceptance:**
- [ ] Shared file exists and is linked
- [ ] Comment or README note: sync from design-system

---

### C2 — Restyle login to match home
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#18](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/18) |
| **Agent** | QuestAI |
| **parallel** | no |
| **Depends on** | C1 |

**Work:** Bring `login.html` chrome/fonts/primary in line with `home.html` navbar treatment (suite header pattern).

**Acceptance:**
- [ ] Login no longer reads as default Bootstrap-only card
- [ ] QA refresh: `qi-login-desktop.png`, `qi-home-desktop.png`

---

### C3 — Home CTA verbs / suite chrome check
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#19](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/19) |
| **Agent** | QuestAI |
| **parallel** | ok with C2 after C1 |
| **Depends on** | C1 |

**Work:** Align home card CTAs with suite verb “Open” / translated equivalents; ensure lang switcher + brand match contract.

**Acceptance:**
- [ ] Gateway CTAs consistent with website hub language
- [ ] QA refresh: `qi-home-desktop.png`, `qi-home-mobile.png`

---

### C4 — Generate form progressive disclosure
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#20](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/20) |
| **Agent** | QuestAI |
| **parallel** | no |
| **Depends on** | C1–C3 |

**Work:** Multi-step / accordion / wizard shell for Define Request on `index.html` so first viewport is not a full wall of fields. Preserve existing JS submit behavior; do not rewrite to React.

**Acceptance:**
- [ ] First viewport shows a clear step, not every control
- [ ] Existing generate flow still callable after steps
- [ ] QA refresh: `qi-index-desktop.png`

---

### C5 — Admin density (deferred)
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#21](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/21) |
| **Agent** | QuestAI |
| **Depends on** | explicit Orchestrator dispatch after C4 |

**Work:** Later — `admin.html` density/IA. Do not start unless dispatched.

---

### QA-C — Phase C visual gate
| Field | Value |
|-------|--------|
| **Status** | deferred |
| **GitHub** | [#22](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/22) |
| **Agent** | Visual QA |
| **Depends on** | C1–C4 |

**Refresh:**  
`qi-login-desktop.png`, `qi-home-desktop.png`, `qi-home-mobile.png`, `qi-index-desktop.png`

**Pass if:** Phase C exit criteria; suite walk Website → QI home → Dashboard login still coherent.

---

## Engineering Track E (parked — do not mix into A/B/C PRs)

### E1 — Website env + SSO smoke

**GitHub:** [#23](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/23) · **Status:** deferred

Document and verify `NEXT_PUBLIC_*` against running APIs; fix login token path only as needed for smoke — not visual redesign.

### E2 — Dashboard SSO contract

**GitHub:** [#24](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/24) · **Status:** deferred

Align `REACT_APP_API_URL` / `verify-sso` path and response (`access_token`) with backend. Separate from B4 hub URL.

### E3 — Dashboard API base URL consistency

**GitHub:** [#25](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/25) · **Status:** deferred

Remove hardcoded `localhost:2000` chart endpoints; single `REACT_APP_API_BASE_URL`.

### E4 — QuestAI local stack

**GitHub:** [#26](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/26) · **Status:** deferred

`.env`, `questions.db` seed, optional dummy model — for interactive generate demos.

### E5 — Role-based nav (Dashboard)

**GitHub:** [#27](https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues/27) · **Status:** deferred

Gate executive/corporate vs instructor after auth — product/IAM, not design tokens.

---

## Ready-to-paste first dispatch

See also kickoff block in [`ISSUE_SYNC.md`](ISSUE_SYNC.md).

**Orchestrator → Design guardian:**

```
Execute ticket DG-1 (GitHub #2) from orchestration/TICKETS.md.
Follow orchestration/ISSUE_SYNC.md: comment on #2 when starting; PR must include Fixes #2.
```

**Then Orchestrator → Website (can batch A1+A2):**

```
Implement tickets A1 (#3) and A2 (#4) from orchestration/TICKETS.md.
Use the Website agent constraints in orchestration/AGENT_PROMPTS.md.
PR title e.g. [A1][A2] … with Fixes #3 and Fixes #4.
```
