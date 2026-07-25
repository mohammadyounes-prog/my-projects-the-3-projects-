# TDM / LMS Suite design contract

**Status:** Source of truth for visual unity across Website (`6015`), QuestAI (`6016`), Dashboard (`6018`/`6019`).  
**Companion files:** [`tokens.css`](tokens.css), audit [`../ux-suite-audit.md`](../ux-suite-audit.md), roadmap [`../ux-adoption-roadmap.md`](../ux-adoption-roadmap.md).

## 1. Brand

| Rule | Spec |
|------|------|
| Suite name (marketing) | **TDM Systems** |
| Product names in chrome | Website hub / QuestAI / Dashboard (or Educational Analytics) — never invent a fourth brand |
| Tagline | Translate “Knowledge is Power”; do not hardcode English-only in chrome |
| Brand-first test | First viewport must still read as this suite after removing the nav |
| Avoid | Inter/Roboto as display face; purple gradients; generic “AI SaaS” purple |

**Locked color primary:** `#2c5282` (already shared by website + QuestAI). Dashboard realigns here.

**Locked fonts:**
- Display: Space Grotesk + IBM Plex Sans Arabic  
- Body: Plus Jakarta Sans + Cairo  

Load both Latin and Arabic families in every app shell.

## 2. Tokens

All products map UI to [`tokens.css`](tokens.css) names (`--suite-*`). Framework mapping:

| App | How to adopt |
|-----|----------------|
| Website | Extend `tailwind.config.js` theme colors/fonts from suite tokens; import or mirror in `globals.css` |
| Dashboard | Replace `--color-primary` / `--color-accent` in `App.css` with suite aliases; purge one-off hex where practical |
| QuestAI | Extract page-local `:root` into a shared include of `tokens.css` (or copy into `frontend/css/suite-tokens.css`) |

**Elevation budget:** only `--suite-shadow-0` … `--suite-shadow-2`. No multi-layer glow stacks.

**Radius budget:** `sm` / `md` / `lg` only.

## 3. Shared chrome

One header pattern on authenticated / product surfaces:

```
[Brand mark + suite/product name] …… [Lang EN|AR] [User] [Logout]
```

| Element | Spec |
|---------|------|
| Height | `--suite-header-height` (~3.5rem) |
| Background | `--suite-header-bg` (primary) on product apps; marketing website may use white sticky bar with primary accents |
| Brand lockup | Single line preferred; if two-line, must be i18n-aware and not English-only |
| Lang switcher | Always present on login + authenticated chrome |
| Logout | Confirm modal with Logout / Back to Hub / Cancel — Hub URL = website origin (env), never hardcoded `:3700` |
| Footer | Module-specific label must match current context (not always “Corporate…”) |

**Hub / module cards**
- Same card radius (`--suite-radius-lg`), icon treatment, and CTA verb **“Open”** (translated).
- Available vs upcoming: upcoming muted, no fake “Open”; no debug “Coming Soon!” full-bleed bars.

**Feedback**
- Ban `alert()` for auth/SSO errors in new work.
- Spec: non-blocking toast or inline banner using `--suite-danger` / `--suite-success`.

## 4. Density by surface type

| Surface type | Density | Example |
|--------------|---------|---------|
| Marketing | Airy, one job per section | Website home, solutions |
| Gateway | Medium, few CTAs | Website hub, QI home, Dashboard home |
| Workbench | Progressive disclosure | QI generate form → wizard steps |
| Analytics | Dense charts OK; still use suite chrome | Dashboard executive views |

## 5. i18n / RTL contract

1. Every chrome string is a translation key (EN + AR parity).
2. Hub is fully translated (currently English-only — defect).
3. Set `<html lang>` and `dir` from locale before paint (website root layout must not hardcode `lang="en"`).
4. Prefer logical CSS: `margin-inline`, `padding-inline`, `inset-inline`, `text-start` / `text-end`.
5. Login pages include language switcher.
6. Testimonials, taglines, footers — no hardcoded English in AR.

## 6. Motion (suite set — use these three)

1. **Header entrance** — `.suite-motion-header`  
2. **Page fade** — `.suite-motion-page`  
3. **Card hover / rise** — `.suite-motion-card` + `.suite-card-hover`  

No additional decorative motion on marketing first viewport beyond these.

## 7. Out of scope (engineering tracks)

- SSO / API env contract fixes  
- QuestAI rewrite to React/Vue  
- Role-based IAM / nav gating implementation details (design may reserve space; auth is separate)  
- Admin mega-console full redesign  
- Full interactive local stacks (DBs, LLM keys)

## 8. Definition of done (visual unity)

A reviewer can open website home → hub → QI home → dashboard login/home and confirm:

1. Same primary blue and display/body fonts  
2. Recognizable header pattern and lang switch  
3. EN ↔ AR including RTL layout on gateway pages  
4. No Coming Soon debug chrome or obvious dead `#` CTAs on primary paths  
