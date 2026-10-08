#!/usr/bin/env bash
# Deploy the current git checkout: backup -> build image -> restart -> migrate.  Run on the VPS from the repo root.
#   First time:  deploy/deploy.sh --first-run   (also creates the site; see docs/DEPLOYMENT.md)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/deploy/.env.prod}"
SITE_NAME="$(grep -E '^SITE_NAME=' "$ENV_FILE" | cut -d= -f2)"
TAG="$(git -C "$ROOT" rev-parse --short HEAD)"
DC="$ROOT/deploy/prod.sh"
cd "$ROOT"
[ "${1:-}" = "--first-run" ] || "$ROOT/deploy/backup.sh"
docker build --platform linux/amd64 -f deploy/Dockerfile -t "garage-erp:$TAG" .
sed -i "s/^CUSTOM_TAG=.*/CUSTOM_TAG=$TAG/" "$ENV_FILE"
"$DC" up -d
sleep 20
if [ "${1:-}" != "--first-run" ]; then
  "$DC" exec -T backend bench --site "$SITE_NAME" migrate
  "$DC" exec -T backend bench --site "$SITE_NAME" clear-cache
fi
echo "Deployed garage-erp:$TAG"
docker image prune -f >/dev/null
