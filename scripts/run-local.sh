#!/usr/bin/env bash
# Start the local UX suite (MySQL SSO + QI API + Dashboard API + three frontends).
# Usage (from repo root):
#   ./scripts/run-local.sh          # start everything in background
#   ./scripts/run-local.sh stop     # stop suite processes we started
#   ./scripts/run-local.sh status   # show listeners
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/.local-run"
PID_FILE="$LOG_DIR/pids"
mkdir -p "$LOG_DIR"

QI_VENV="$ROOT/inst-QI-6016/.venv"
DASH_VENV="$ROOT/inst-dashboard-6018/.venv"

# Auth API port — keep in sync with inst-QI-6016/backend/.env and website .env.local
QI_API_PORT=8001

red() { printf '\033[31m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
info() { printf '→ %s\n' "$*"; }

port_in_use() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

wait_http() {
  local url="$1" name="$2" tries="${3:-40}"
  local i
  for i in $(seq 1 "$tries"); do
    if curl -sf -o /dev/null "$url"; then
      green "OK  $name ($url)"
      return 0
    fi
    sleep 0.5
  done
  red "FAIL $name did not become ready: $url"
  return 1
}

ensure_mysql() {
  info "MySQL (suite-mysql-local on :3307)"
  docker compose -f "$ROOT/docker-compose.local.yml" up -d
  local i h
  for i in $(seq 1 40); do
    h="$(docker inspect --format='{{.State.Health.Status}}' suite-mysql-local 2>/dev/null || echo starting)"
    [[ "$h" == "healthy" ]] && break
    sleep 1
  done
  if [[ "$(docker inspect --format='{{.State.Health.Status}}' suite-mysql-local)" != "healthy" ]]; then
    red "MySQL not healthy"
    exit 1
  fi
  green "OK  MySQL healthy"
}

ensure_venv_qi() {
  if [[ ! -x "$QI_VENV/bin/python" ]]; then
    info "Creating QuestAI venv"
    python3 -m venv "$QI_VENV"
    "$QI_VENV/bin/pip" install -q -r "$ROOT/inst-QI-6016/backend/requirements.txt"
  fi
}

ensure_venv_dash() {
  if [[ ! -x "$DASH_VENV/bin/python" ]]; then
    info "Creating Dashboard venv"
    python3 -m venv "$DASH_VENV"
    "$DASH_VENV/bin/pip" install -q -r "$ROOT/inst-dashboard-6018/backend/requirements.txt"
  fi
}

seed() {
  info "Seeding QuestAI SQLite + linking SSO employee"
  (
    cd "$ROOT/inst-QI-6016"
    # shellcheck disable=SC1091
    source .venv/bin/activate
    python scripts/seed_local_demo.py
  )
  "$QI_VENV/bin/python" "$ROOT/scripts/link_demo_sso.py"
}

start_bg() {
  local name="$1"
  shift
  local log="$LOG_DIR/$name.log"
  info "Starting $name → $log"
  nohup "$@" >"$log" 2>&1 &
  echo "$name $!" >>"$PID_FILE"
}

cmd_start() {
  : >"$PID_FILE"
  ensure_mysql
  ensure_venv_qi
  ensure_venv_dash
  seed

  if port_in_use "$QI_API_PORT"; then
    info "Port $QI_API_PORT already in use — assuming QI API is up"
  else
    start_bg qi-api bash -lc "cd '$ROOT/inst-QI-6016' && source .venv/bin/activate && python run_server.py"
  fi

  if port_in_use 6018; then
    info "Port 6018 already in use — assuming Dashboard API is up"
  else
    start_bg dash-api bash -lc "cd '$ROOT/inst-dashboard-6018' && source .venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 6018"
  fi

  if port_in_use 6016; then
    info "Port 6016 already in use — assuming QuestAI UI is up"
  else
    start_bg qi-ui bash -lc "cd '$ROOT/inst-QI-6016/frontend' && python3 -m http.server 6016"
  fi

  if port_in_use 6019; then
    info "Port 6019 already in use — assuming Dashboard UI is up"
  else
    start_bg dash-ui bash -lc "cd '$ROOT/inst-dashboard-6018/frontend' && npx --yes serve -s build -l 6019"
  fi

  if port_in_use 6015; then
    info "Port 6015 already in use — assuming Website is up"
  else
    start_bg website bash -lc "cd '$ROOT/inst-website-6015' && npm run dev"
  fi

  info "Waiting for health checks…"
  wait_http "http://127.0.0.1:${QI_API_PORT}/docs" "QuestAI API"
  wait_http "http://127.0.0.1:6018/health" "Dashboard API"
  wait_http "http://127.0.0.1:6016/login.html" "QuestAI UI"
  wait_http "http://127.0.0.1:6019" "Dashboard UI"
  wait_http "http://127.0.0.1:6015/en" "Website" 60

  cat <<EOF

$(green "Local suite is up")
  Website:    http://localhost:6015/en/login
  QuestAI:    http://localhost:6016/login.html
  Dashboard:  http://localhost:6019/login
  QI API:     http://localhost:${QI_API_PORT}
  Dash API:   http://localhost:6018
  MySQL SSO:  127.0.0.1:3307 / schooldemo12

  Login:  demo / demo123

  Logs:   $LOG_DIR/
  Stop:   ./scripts/run-local.sh stop

  Note: Online exam UI (:8080) is not in this repo — Assessment hub link needs that external app.
EOF
}

cmd_stop() {
  if [[ -f "$PID_FILE" ]]; then
    while read -r name pid; do
      [[ -z "${pid:-}" ]] && continue
      if kill "$pid" 2>/dev/null; then
        info "Stopped $name (pid $pid)"
      fi
    done <"$PID_FILE"
    rm -f "$PID_FILE"
  fi
  # Also stop by port for orphans we started
  for p in 6015 6016 6018 6019 "$QI_API_PORT"; do
    if port_in_use "$p"; then
      # only kill if listening process is ours (python/node/serve) — best-effort
      pids="$(lsof -t -nP -iTCP:"$p" -sTCP:LISTEN 2>/dev/null || true)"
      if [[ -n "$pids" ]]; then
        info "Killing listeners on :$p ($pids)"
        # shellcheck disable=SC2086
        kill $pids 2>/dev/null || true
      fi
    fi
  done
  info "Leaving MySQL container running (docker compose -f docker-compose.local.yml down to stop it)"
}

cmd_status() {
  for p in 3307 "$QI_API_PORT" 6015 6016 6018 6019 8080; do
    if port_in_use "$p"; then
      green ":$p LISTEN"
      lsof -nP -iTCP:"$p" -sTCP:LISTEN 2>/dev/null | tail -n +2 || true
    else
      printf ':%s free\n' "$p"
    fi
  done
  docker ps --filter name=suite-mysql-local --format 'MySQL {{.Status}}' 2>/dev/null || true
}

case "${1:-start}" in
  start) cmd_start ;;
  stop) cmd_stop ;;
  status) cmd_status ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
