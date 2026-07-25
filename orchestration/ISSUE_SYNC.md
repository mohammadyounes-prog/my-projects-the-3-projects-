# Orchestrator ↔ GitHub Issues sync

**Ownership split (keep it clean):**

| Source of truth | Role |
|-----------------|------|
| [`TICKETS.md`](TICKETS.md) | Spec: work, acceptance, depends-on, parallel rules |
| GitHub Issues | Tracker: status, assignee, PR links, discussion |
| [`ISSUE_MAP.md`](ISSUE_MAP.md) | 1:1 Ticket ID → `#issue` number |

Do **not** fork ticket text into long issue-only specs. If the work changes, edit `TICKETS.md` first, then update the issue body if needed.

---

## Labels

| Label | Meaning |
|-------|---------|
| `orchestrator` | Managed by the UX suite orchestrator |
| `phase-a` / `phase-b` / `phase-c` | Implementation wave |
| `design` | Design guardian / tokens |
| `qa` | Visual QA gate |
| `eng-track` | Parked SSO/API/DB — never mix into A/B/C UI PRs |
| `deferred` | Not ready to dispatch (B/C/E until prior gate passes) |
| `agent-*` | Intended implementer role |

## Milestones

1. Suite UX — Phase A (Website) — **dispatch now**
2. Suite UX — Phase B (Dashboard) — after QA-A PASS
3. Suite UX — Phase C (QuestAI) — after QA-B PASS
4. Suite UX — Engineering Track E — separate owner / explicit dispatch

---

## Orchestrator sync protocol

### On session start

1. `git pull` on `master`.
2. Read [`ISSUE_MAP.md`](ISSUE_MAP.md) + [`DISPATCH_ORDER.md`](DISPATCH_ORDER.md).
3. Refresh GitHub state:

```bash
gh issue list --label orchestrator --state open --limit 50
gh issue list --label phase-a --state open
gh issue list --milestone "Suite UX — Phase A (Website)" --state all
```

4. Treat GitHub **open/closed** as progress; treat `TICKETS.md` **Status** field as the mirror (update both when dispatching).

### When dispatching a ticket

1. Look up issue number in `ISSUE_MAP.md` (e.g. A3 → `#5`).
2. If labeled `deferred` and the prior gate has passed, remove `deferred`:

```bash
gh issue edit <N> --remove-label deferred
```

3. Set issue in progress (comment + optional assignee):

```bash
gh issue comment <N> --body "Orchestrator dispatch: starting with <agent role>. Branch: ux/<ticket-id>-short-slug"
```

4. Update `TICKETS.md` status → `in_progress`.
5. Hand the implementer **both** the ticket ID and issue URL, using [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md).

### When opening a PR

- Branch: `ux/<ticket-id>-short-slug` (e.g. `ux/a3-hub-restyle`)
- Title: `[A3] Restyle website hub to marketing brand`
- Body must include:

```markdown
Fixes #<issue-number>

Ticket: A3 (orchestration/TICKETS.md)
```

- One ticket per PR (exception: A1+A2 may share a PR if explicitly batched — then `Fixes #3` and `Fixes #4`).

### When PR merges

1. Confirm issue auto-closed via `Fixes #N`.
2. Set `TICKETS.md` status → `done`.
3. If a QA gate issue: require PASS comment before closing; close only on PASS.

```bash
gh issue comment <QA-N> --body "Visual QA: PASS (or FAIL + defect list mapped to ticket IDs)"
# On PASS:
gh issue close <QA-N> --reason completed
# On FAIL: leave open; re-dispatch failing tickets
```

### Phase gates

| Gate issue | Unlocks |
|------------|---------|
| QA-A `#9` PASS | Remove `deferred` from Phase B issues `#10`–`#16` |
| QA-B `#16` PASS | Remove `deferred` from Phase C issues `#17`–`#22` (not C5 unless intended) |
| QA-C `#22` PASS | Suite visual unity done; E-track still optional |

Unlock example:

```bash
for n in 10 11 12 13 14 15 16; do gh issue edit $n --remove-label deferred; done
```

### Engineering track (E1–E5)

- Stay `deferred` + `eng-track` until a human/orchestrator explicitly prioritizes them.
- Never combine E-* commits into A/B/C PRs.
- Agent prompt: Engineering track in `AGENT_PROMPTS.md`.

### Conflict / drift rules

- Spec conflict → prefer `TICKETS.md` + design contract; update issue text to match.
- Brand conflict → Design guardian + `qi-home-desktop.png` win.
- Missing map entry → recreate issue or add row to `ISSUE_MAP.md` in the same PR as the fix.
- Do not create duplicate issues for the same Ticket ID; search first:

```bash
gh issue list --search "[A3]" --state all
```

---

## Ready-to-paste orchestrator kickoff (new session)

```
You are the UX suite Orchestrator.

Read:
- orchestration/ISSUE_SYNC.md (this sync protocol)
- orchestration/ISSUE_MAP.md
- orchestration/DISPATCH_ORDER.md
- orchestration/AGENT_PROMPTS.md
- orchestration/TICKETS.md
- design-system/SUITE_DESIGN_CONTRACT.md

GitHub is the tracker; TICKETS.md is the spec.

Current dispatch order:
1. DG-1 (#2)
2. A1 (#3) + A2 (#4) (parallel OK)
3. A3–A6 then QA-A (#9)

Use gh to comment/edit issues when dispatching. PRs must include Fixes #<n>.
Do not start Phase B/C while those issues still have label deferred (until QA-A/QA-B pass).
Do not invent design tokens.
```
