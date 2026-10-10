#!/bin/bash
# Runs as root. Prepares the persistent disk, then hands over to supervisord.
set -euo pipefail
DATA="${DATA_DIR:-/data}"
BENCH=/home/frappe/frappe-bench
mkdir -p "$DATA/mysql" "$DATA/sites" "$DATA/redis"

# static assets built into the image are served from sites/assets
ln -sfn "$BENCH/assets" "$BENCH/sites/assets"
# (the image declares "sites" as a Docker volume, so it stays as is; only the site folder itself lives on the disk - see bootstrap-site.sh)
# database + redis state
if [ ! -d "$DATA/mysql/mysql" ]; then
  mariadb-install-db --user=mysql --datadir="$DATA/mysql" --auth-root-authentication-method=normal >/dev/null
fi
chown -R mysql:mysql "$DATA/mysql"
chown frappe:root "$DATA"
chown -R frappe:root "$DATA/sites" "$DATA/redis"
[ -f "$DATA/.dbroot" ] || openssl rand -hex 16 > "$DATA/.dbroot"
chown frappe:root "$DATA/.dbroot"; chmod 600 "$DATA/.dbroot"

export PORT="${PORT:-10000}"
exec /usr/bin/supervisord -n -c /etc/supervisor/garage.conf
