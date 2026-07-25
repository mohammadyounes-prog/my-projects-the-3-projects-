# UX suite implementation — agent orchestration pack

Hand these prompts and tickets to coding agents. **Do not invent design tokens** — use [`../design-system/`](../design-system/).

| File | Purpose |
|------|---------|
| [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) | System/user prompts per agent role |
| [`TICKETS.md`](TICKETS.md) | Implementable tickets (A1–C4, E-track, QA) |
| [`DISPATCH_ORDER.md`](DISPATCH_ORDER.md) | Who runs when; merge gates |

**Source of truth (read before any ticket):**

1. [`../design-system/SUITE_DESIGN_CONTRACT.md`](../design-system/SUITE_DESIGN_CONTRACT.md)
2. [`../design-system/tokens.css`](../design-system/tokens.css)
3. [`../ux-suite-audit.md`](../ux-suite-audit.md)
4. [`../ux-adoption-roadmap.md`](../ux-adoption-roadmap.md)
5. [`../ux-screenshots/`](../ux-screenshots/) (baseline)

**Sequence:** Design guardian (once) → Phase A tickets → Visual QA → Phase B → Visual QA → Phase C → Visual QA.  
**Park:** SSO/API/DB/React rewrite tickets in Engineering Track E — different owner.