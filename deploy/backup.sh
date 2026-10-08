#!/usr/bin/env bash
# Full backup (database + public + private files + site_config) to BACKUP_DIR, pruned after KEEP_DAYS,
# optionally copied off-server with rclone (set RCLONE_REMOTE, e.g. "b2:garage-backups/erp").
# Cron example (daily 02:30):  30 2 * * *  /opt/garage-erp/deploy/backup.sh >> /var/log/garage-backup.log 2>&1
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/deploy/.env.prod}"
SITE_NAME="$(grep -E '^SITE_NAME=' "$ENV_FILE" | cut -d= -f2)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/garage}"
KEEP_DAYS="${KEEP_DAYS:-14}"
DC="$ROOT/deploy/prod.sh"
SRC="/home/frappe/frappe-bench/sites/$SITE_NAME/private/backups"

mkdir -p "$BACKUP_DIR/$SITE_NAME" "$BACKUP_DIR/config"
echo "[$(date '+%F %T')] backup start: $SITE_NAME"
"$DC" exec -T backend bench --site "$SITE_NAME" backup --with-files
"$DC" cp "backend:$SRC/." "$BACKUP_DIR/$SITE_NAME/"
# keep the server config next to the data (contains DB password): readable by owner only
install -m 600 "$ENV_FILE" "$BACKUP_DIR/config/env.prod.$(date +%F)"
"$DC" exec -T backend find "$SRC" -type f -mtime +"$KEEP_DAYS" -delete
find "$BACKUP_DIR" -type f -mtime +"$KEEP_DAYS" -delete
if [ -n "${RCLONE_REMOTE:-}" ]; then
  rclone copy "$BACKUP_DIR" "$RCLONE_REMOTE" --log-level INFO
  echo "[$(date '+%F %T')] off-site copy done -> $RCLONE_REMOTE"
else
  echo "WARNING: RCLONE_REMOTE not set - backups exist only on this server"
fi
echo "[$(date '+%F %T')] backup done. Latest:"; ls -1t "$BACKUP_DIR/$SITE_NAME" | head -4
