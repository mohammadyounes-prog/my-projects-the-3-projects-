# UX suite implementation — agent orchestration pack

Hand these prompts and tickets to coding agents. **Do not invent design tokens** — use [`../design-system/`](../design-system/).

| File | Purpose |
|------|---------|
| [`ISSUE_SYNC.md`](ISSUE_SYNC.md) | **Orchestrator ↔ GitHub sync protocol** (labels, gates, `Fixes #N`) |
| [`ISSUE_MAP.md`](ISSUE_MAP.md) | Ticket ID → GitHub issue number |
| [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) | System/user prompts per agent role |
| [`TICKETS.md`](TICKETS.md) | Spec (work + acceptance); status mirrored to GH |
| [`DISPATCH_ORDER.md`](DISPATCH_ORDER.md) | Who runs when; merge gates |

**Source of truth (read before any ticket):**

1. [`../design-system/SUITE_DESIGN_CONTRACT.md`](../design-system/SUITE_DESIGN_CONTRACT.md)
2. [`../design-system/tokens.css`](../design-system/tokens.css)
3. [`../ux-suite-audit.md`](../ux-suite-audit.md)
4. [`../ux-adoption-roadmap.md`](../ux-adoption-roadmap.md)
5. [`../ux-screenshots/`](../ux-screenshots/) (baseline)

**Tracking split:** `TICKETS.md` = spec · GitHub Issues = tracker · `ISSUE_MAP.md` = join table.

**Sequence:** Design guardian (DG-1 `#2`) → Phase A (`#3`–`#9`) → Visual QA → unlock Phase B → …  
**Park:** B/C/E issues carry `deferred` until gates pass / explicit dispatch.

**Issues board:** https://github.com/mohammadyounes-prog/my-projects-the-3-projects-/issues?q=label%3Aorchestrator