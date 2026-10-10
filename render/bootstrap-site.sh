#!/bin/bash
# First boot: create the site and install the apps. Every boot: migrate (applies updates) and re-apply the garage details.
set -uo pipefail
DATA="${DATA_DIR:-/data}"
SITE="${SITE_NAME:-garage.local}"
BENCH=/home/frappe/frappe-bench
cd "$BENCH"
rm -f "$DATA/.ready"   # web/worker wait for this until migrations are done
ROOTPW="$(cat "$DATA/.dbroot")"
echo "[bootstrap] waiting for MariaDB..."
until mariadb-admin ping -h127.0.0.1 --silent 2>/dev/null; do sleep 2; done
if [ ! -f "$DATA/.dbroot_set" ]; then
  mariadb -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$ROOTPW'; FLUSH PRIVILEGES;" && touch "$DATA/.dbroot_set"
fi
URL="${RENDER_EXTERNAL_URL:-http://localhost:${PORT:-10000}}"
cat > "$BENCH/sites/common_site_config.json" <<JSON
{"db_host":"127.0.0.1","db_port":3306,"redis_cache":"redis://127.0.0.1:6379","redis_queue":"redis://127.0.0.1:6380",
 "redis_socketio":"redis://127.0.0.1:6380","socketio_port":9000,"default_site":"$SITE","host_name":"$URL"}
JSON
# the site folder (files, uploads, site_config with DB credentials) is kept on the persistent disk
if [ -d "$DATA/sites/$SITE" ] && [ ! -e "$BENCH/sites/$SITE" ]; then
  ln -s "$DATA/sites/$SITE" "$BENCH/sites/$SITE"
fi
if [ ! -d "$BENCH/sites/$SITE" ]; then
  echo "[bootstrap] creating site $SITE (first boot, several minutes)..."
  bench new-site "$SITE" --db-root-username root --db-root-password "$ROOTPW" \
    --admin-password "${ADMIN_PASSWORD:?set ADMIN_PASSWORD}" --install-app erpnext --install-app garage_management --set-default </dev/null \
    || { echo "[bootstrap] new-site FAILED"; exit 1; }
  mv "$BENCH/sites/$SITE" "$DATA/sites/$SITE" && ln -s "$DATA/sites/$SITE" "$BENCH/sites/$SITE"
fi
echo "[bootstrap] migrating..."
bench --site "$SITE" migrate
bench --site "$SITE" enable-scheduler
bench --site "$SITE" execute garage_management.setup.company.apply || echo "[bootstrap] company details are applied after the Setup Wizard + restart"
touch "$DATA/.ready"
echo "[bootstrap] ready"
