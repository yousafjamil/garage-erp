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
# the PDF engine fetches the page assets from host_name: in demo mode use the container's own address (no outside round trip)
[ "${DEMO_SEED:-0}" = "1" ] && URL="http://127.0.0.1:${PORT:-10000}"
cat > "$BENCH/sites/common_site_config.json" <<JSON
{"db_host":"127.0.0.1","db_port":3306,"redis_cache":"redis://127.0.0.1:6379","redis_queue":"redis://127.0.0.1:6380",
 "redis_socketio":"redis://127.0.0.1:6380","socketio_port":9000,"default_site":"$SITE","host_name":"$URL"}
JSON
# DEMO_SEED=1: restore the ready-made demo database baked into the image (about 1 MB) instead of running the heavy first-time install.
# Used for the free 512 MB tier, where the install itself would be killed for lack of memory. Data is NOT kept across restarts there.
if [ "${DEMO_SEED:-0}" = "1" ] && [ ! -d "$BENCH/sites/$SITE" ] && [ -f /seed/demo-database.sql.gz ]; then
  echo "[bootstrap] restoring the demo database..."
  DBN=_demo; DBPW="$(openssl rand -hex 12)"
  mariadb -uroot -p"$ROOTPW" -e "DROP DATABASE IF EXISTS \`$DBN\`; CREATE DATABASE \`$DBN\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS '$DBN'@'localhost' IDENTIFIED BY '$DBPW'; ALTER USER '$DBN'@'localhost' IDENTIFIED BY '$DBPW'; GRANT ALL PRIVILEGES ON \`$DBN\`.* TO '$DBN'@'localhost'; FLUSH PRIVILEGES;"
  gunzip -c /seed/demo-database.sql.gz | mariadb -uroot -p"$ROOTPW" "$DBN"
  mkdir -p "$BENCH/sites/$SITE"/{public/files,private/files,private/backups,locks,logs}
  KEY="$(env/bin/python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
  cat > "$BENCH/sites/$SITE/site_config.json" <<JSON
{"db_name":"$DBN","db_user":"$DBN","db_password":"$DBPW","db_type":"mariadb","encryption_key":"$KEY","host_name":"$URL"}
JSON
  if [ -n "${ADMIN_PASSWORD:-}" ]; then bench --site "$SITE" set-admin-password "$ADMIN_PASSWORD" || true; fi
  # the baked data may predate the latest Home page / menu: rebuild just those (cheap) so no new seed is needed for UI tweaks
  bench --site "$SITE" execute garage_management.setup.install.refresh_ui || true
  echo "[bootstrap] demo database restored"
fi
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
if [ "${LITE:-0}" = "1" ] && [ "${FORCE_MIGRATE:-0}" != "1" ]; then
  # 512 MB instances cannot fit "bench migrate" (it gets OOM-killed). Set FORCE_MIGRATE=1 once, on a bigger instance, after updating the code.
  echo "[bootstrap] LITE mode: skipping migrate"; touch "$DATA/.ready"; echo "[bootstrap] ready"; exit 0
fi
echo "[bootstrap] migrating..."
bench --site "$SITE" migrate
bench --site "$SITE" enable-scheduler
bench --site "$SITE" execute garage_management.setup.install.setup_all || echo "[bootstrap] business setup is applied after the Setup Wizard + restart"
touch "$DATA/.ready"
echo "[bootstrap] ready"
