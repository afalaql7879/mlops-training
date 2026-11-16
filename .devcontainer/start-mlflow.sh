#!/usr/bin/env bash
# Start a local MLflow tracking server in the background.
# Runs on every codespace start (postStartCommand). Runs, metrics and artifacts
# (DVC data versions, data quality reports) are kept in .mlflow/ in the
# workspace, so they survive stopping and restarting the codespace.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STORE="$ROOT/.mlflow"
LOG="$STORE/server.log"
PORT="${MLFLOW_PORT:-5000}"

mkdir -p "$STORE/artifacts"

if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
  echo "MLflow is already running on port $PORT."
  exit 0
fi

export MLFLOW_DISABLE_AGENT_HINT=1
nohup mlflow server \
  --host 0.0.0.0 \
  --port "$PORT" \
  --backend-store-uri "sqlite:///$STORE/mlflow.db" \
  --artifacts-destination "$STORE/artifacts" \
  --allowed-hosts "localhost:*,127.0.0.1:*,*.app.github.dev" \
  --cors-allowed-origins "https://*.app.github.dev" \
  >"$LOG" 2>&1 &

for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
    echo "MLflow is running on http://localhost:$PORT (log: $LOG)."
    exit 0
  fi
  sleep 1
done

echo "MLflow did not start within 60 seconds. See $LOG." >&2
exit 1
