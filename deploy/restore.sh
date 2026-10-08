#!/usr/bin/env bash
# Restore a backup set into the running stack.  Usage: deploy/restore.sh <backup-prefix>
#   e.g.  deploy/restore.sh 20261007_020158-erp_example_com      (files must be in BACKUP_DIR/<site>/)
# WARNING: overwrites the current database and files of the site.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/deploy/.env.prod}"
SITE_NAME="$(grep -E '^SITE_NAME=' "$ENV_FILE" | cut -d= -f2)"
DB_PASSWORD="$(grep -E '^DB_PASSWORD=' "$ENV_FILE" | cut -d= -f2)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/garage}"
PREFIX="${1:?usage: restore.sh <backup-prefix>}"
DC="$ROOT/deploy/prod.sh"
D="$BACKUP_DIR/$SITE_NAME"
for f in database.sql.gz files.tar private-files.tar; do [ -f "$D/$PREFIX-$f" ] || { echo "missing $D/$PREFIX-$f"; exit 1; }; done
read -r -p "Overwrite site $SITE_NAME with backup $PREFIX ? type YES: " ok; [ "$ok" = "YES" ] || exit 1
"$DC" exec -T backend mkdir -p /tmp/restore
"$DC" cp "$D/." backend:/tmp/restore/
"$DC" exec -T backend bench --site "$SITE_NAME" restore "/tmp/restore/$PREFIX-database.sql.gz" \
  --with-public-files "/tmp/restore/$PREFIX-files.tar" --with-private-files "/tmp/restore/$PREFIX-private-files.tar" \
  --db-root-password "$DB_PASSWORD" --force
"$DC" exec -T backend bench --site "$SITE_NAME" migrate
"$DC" exec -T backend bench --site "$SITE_NAME" clear-cache
echo "Restore finished. Check the site, then run:  deploy/prod.sh restart"
