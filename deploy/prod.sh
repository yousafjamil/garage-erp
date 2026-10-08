#!/usr/bin/env bash
# Production wrapper for docker compose. Usage:  deploy/prod.sh up -d | ps | logs -f backend | exec backend bench ...
# Env: ENV_FILE (default deploy/.env.prod), COMPOSE_PROJECT_NAME (default garage), USE_HTTPS=0 for local rehearsal.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/deploy/.env.prod}"
ENV_FILE="$(cd "$(dirname "$ENV_FILE")" 2>/dev/null && pwd)/$(basename "$ENV_FILE")"
[ -f "$ENV_FILE" ] || { echo "Missing $ENV_FILE (copy deploy/.env.prod.example)"; exit 1; }
FILES=(-f compose.yaml -f overrides/compose.mariadb.yaml -f overrides/compose.redis.yaml)
if [ "${USE_HTTPS:-1}" = "1" ]; then FILES+=(-f overrides/compose.https.yaml); else FILES+=(-f overrides/compose.noproxy.yaml); fi
cd "$ROOT/frappe_docker"
exec docker compose --project-name "${COMPOSE_PROJECT_NAME:-garage}" --env-file "$ENV_FILE" "${FILES[@]}" "$@"
