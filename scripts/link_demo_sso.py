#!/usr/bin/env python3
"""Link QuestAI demo user to MySQL employee id=1 for SSO."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "inst-QI-6016" / "questions.db"
EMPLOYEE_ID = 1


def main() -> int:
    if not DB.exists():
        print(f"Missing {DB} — run: python scripts/seed_local_demo.py (from inst-QI-6016)", file=sys.stderr)
        return 1
    conn = sqlite3.connect(DB)
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(users)")}
        if "schooldemo12_user_id" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN schooldemo12_user_id INTEGER")
        cur = conn.execute(
            "UPDATE users SET schooldemo12_user_id = ?, email = COALESCE(email, 'demo@localhost') WHERE username = 'demo'",
            (EMPLOYEE_ID,),
        )
        if cur.rowcount == 0:
            print("No demo user found — seed QuestAI first.", file=sys.stderr)
            return 1
        conn.commit()
        row = conn.execute(
            "SELECT id, username, email, schooldemo12_user_id FROM users WHERE username = 'demo'"
        ).fetchone()
        print(f"Linked demo user: id={row[0]} username={row[1]} email={row[2]} schooldemo12_user_id={row[3]}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
