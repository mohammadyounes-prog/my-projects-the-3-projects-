# Suite token adoption notes

**Ticket:** DG-1 · **Source of truth:** [`tokens.css`](tokens.css)  
**Contract:** [`SUITE_DESIGN_CONTRACT.md`](SUITE_DESIGN_CONTRACT.md)

This document tells each app **how** to consume `--suite-*` without forking hex.  
Do **not** change product UI in DG-1; implement the mapping in the phase tickets (A2, B1, C1).

---

## Rules (all apps)

1. **`design-system/tokens.css` is the only place that defines suite hex/font stacks.**  
   Apps import it, or mirror a verbatim copy with a sync comment — never invent parallel brand values.
2. **Primary is `#2c5282`** (`--suite-primary`). Do not substitute sky/indigo/purple “AI SaaS” palettes.
3. **Fonts (load Latin + Arabic in every shell):**
   - Display: Space Grotesk + IBM Plex Sans Arabic → `--suite-font-display`
   - Body: Plus Jakarta Sans + Cairo → `--suite-font-body`
4. Prefer `var(--suite-*)` (or a thin local alias that **points at** suite vars). Never redefine a local `--color-primary` with a different hex than `--suite-primary`.
5. Elevation only `--suite-shadow-0` … `--suite-shadow-2`. Radius only `sm` / `md` / `lg`.

---

## Website (`inst-website-6015`) — Tailwind + `globals.css`

**Target tickets:** A1 (fonts), A2 (tokens)

| File | Role |
|------|------|
| `src/app/globals.css` | Import suite tokens into `:root`; keep Tailwind layers |
| `tailwind.config.js` | Map theme `colors` / `fontFamily` / radii / shadows to suite CSS vars |
| `src/app/layout.tsx`, `src/app/[lang]/layout.tsx` | Load fonts (`next/font` and/or Google Fonts) — A1 |

### Preferred import

From the website package root, tokens live two directories up:

```css
/* src/app/globals.css — at top, before @tailwind or after; before local :root overrides */
@import "../../../design-system/tokens.css";
```

If the bundler cannot resolve a path outside the Next app, **mirror** instead:

1. Copy `design-system/tokens.css` → `src/styles/suite-tokens.css` (or keep values only in `globals.css` `:root`).
2. First line of the mirror file must be:

   ```css
   /* SYNCED FROM design-system/tokens.css — do not edit hex here; update the source and re-copy. */
   ```

3. Then `@import` / include that local file.

### After tokens are present — Tailwind mapping (A2)

Replace ad-hoc stacks such as `Inter` and `primary.500: #3b82f6` with suite wiring, for example:

```js
// tailwind.config.js (illustrative — implement in A2)
theme: {
  extend: {
    fontFamily: {
      display: ['var(--suite-font-display)'],
      sans: ['var(--suite-font-body)'],
    },
    colors: {
      primary: {
        DEFAULT: 'var(--suite-primary)',
        dark: 'var(--suite-primary-dark)',
        soft: 'var(--suite-primary-soft)',
      },
      // deprecate parallel --primary-blue once components use theme
    },
    borderRadius: {
      sm: 'var(--suite-radius-sm)',
      md: 'var(--suite-radius-md)',
      lg: 'var(--suite-radius-lg)',
    },
    boxShadow: {
      suite1: 'var(--suite-shadow-1)',
      suite2: 'var(--suite-shadow-2)',
    },
  },
},
```

**Current drift to fix later:** `globals.css` uses `--primary-blue: #2c5282` (OK hex, wrong name); `tailwind.config.js` still sets `sans: Inter` and `primary.500: #3b82f6`.

---

## Dashboard (`inst-dashboard-6018/frontend`) — `App.css` aliases

**Target ticket:** B1

| File | Role |
|------|------|
| `src/App.css` | Replace local `:root` hex with aliases to `--suite-*` |
| `public/index.html` (or CSS `@import`) | Load suite Google Fonts / self-hosted faces |

### Preferred import

```css
/* src/App.css — first line */
@import "../../../design-system/tokens.css";
/* path: frontend/src → repo root design-system (adjust if CRA resolve fails) */
```

If CRA/Webpack blocks imports outside `src/`, either:

- Place a synced copy at `src/styles/suite-tokens.css` with the sync comment above, **or**
- Keep tokens in `App.css` but only as aliases (no second hex source):

```css
/* After suite tokens are loaded */
:root {
  --color-primary: var(--suite-primary);
  --color-accent: var(--suite-accent-sky); /* or suite-primary if accent should match brand */
  --color-bg-app: var(--suite-surface);
  --color-bg-card: var(--suite-surface-raised);
  --color-text-main: var(--suite-text);
  --color-text-muted: var(--suite-text-muted);
  --color-border: var(--suite-border);
  --font-display: var(--suite-font-display);
  --font-body: var(--suite-font-body);
  --font-mono: var(--suite-font-mono);
}
```

Components may keep using `--color-primary` during migration **only if** those names alias suite vars.

**Current drift to fix in B1:** `--color-primary: #1e293b`, `--color-accent: #3b82f6`, `--font-display: Inter`.

---

## QuestAI (`inst-QI-6016/frontend`) — shared `suite-tokens.css`

**Target ticket:** C1

| File | Role |
|------|------|
| `frontend/css/suite-tokens.css` | **Create** — copy or build-sync from `design-system/tokens.css` |
| `home.html`, `login.html`, `index.html` (then other shells) | `<link rel="stylesheet" href="css/suite-tokens.css">` before page styles |
| Inline `:root` blocks in HTML | Remove duplicated palette/font vars once shared file is linked |

### Recommended sync (C1)

1. Create `inst-QI-6016/frontend/css/` entry (folder already has Bootstrap; add suite file beside or under it):

   ```text
   inst-QI-6016/frontend/css/suite-tokens.css
   ```

2. File header:

   ```css
   /* SYNCED FROM design-system/tokens.css — do not edit hex here; update the source and re-copy. */
   ```

3. Copy the full contents of `design-system/tokens.css` (includes QI migration aliases: `--accent-blue`, `--font-display`, etc.).

4. In each page `<head>`, after Bootstrap / before page `<style>`:

   ```html
   <link rel="stylesheet" href="css/suite-tokens.css">
   ```

5. Delete page-local `:root { --accent-blue: #2c5282; … --font-display: … }` blocks so hex is not forked.

**Optional build step:** a small script or Makefile target that `cp design-system/tokens.css inst-QI-6016/frontend/css/suite-tokens.css` and prepends the sync comment. Prefer that over hand-edits when tokens change.

**Current state:** `home.html` (and siblings) already use `#2c5282` and suite fonts inline — good values, wrong duplication. C1 consolidates; no UI restyle required in C1 beyond linking the shared file.

---

## Forbidden patterns

| Forbidden | Why | Use instead |
|-----------|-----|-------------|
| Inter / Roboto / Arial as **display** (or sole brand face) | Breaks suite identity | `--suite-font-display` / `--suite-font-body` |
| Purple / violet / indigo gradient themes | Contract ban; not suite brand | `--suite-primary` `#2c5282` family |
| New brand hex in component CSS (`#3b82f6`, `#7c3aed`, …) | Forks the token source | `var(--suite-*)` or mapped Tailwind theme |
| Parallel token files with different hex than `tokens.css` | Drift | Import or sync-comment copy |
| Shadows beyond `--suite-shadow-2` / multi-layer glow stacks | Elevation budget | `--suite-shadow-0` … `--suite-shadow-2` |
| Extra radius scales outside sm/md/lg | Radius budget | `--suite-radius-sm/md/lg` |
| Inventing new `--suite-*` names in apps | Naming owned by Design guardian | Extend `tokens.css` first, then adopt |

---

## Verification checklist (per adopting ticket)

- [ ] Computed primary on chrome/surfaces is `#2c5282` (or soft/dark variants from tokens only).
- [ ] Display/body computed fonts match Space Grotesk / IBM Plex Sans Arabic and Plus Jakarta Sans / Cairo.
- [ ] No second `:root` hex palette that disagrees with `design-system/tokens.css`.
- [ ] Mirror/copy files (if any) carry the **SYNCED FROM** comment.
- [ ] Visual QA refreshes the screenshots listed on the phase ticket.

---

## Related tickets

| Ticket | App | Work |
|--------|-----|------|
| A1 / A2 | Website | Load fonts; mirror tokens into Tailwind/`globals.css` |
| B1 | Dashboard | Retoken `App.css` + load fonts |
| C1 | QuestAI | Ship `frontend/css/suite-tokens.css` and link pages |
