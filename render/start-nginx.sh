#!/bin/bash
# Frappe's nginx config (same template the official image uses) listening on $PORT, plus a /healthz check for Render.
set -e
export BACKEND=127.0.0.1:8000 SOCKETIO=127.0.0.1:9000 NGINX_LISTEN_PORT="${PORT:-10000}"
export UPSTREAM_REAL_IP_ADDRESS=127.0.0.1 UPSTREAM_REAL_IP_HEADER=X-Forwarded-For UPSTREAM_REAL_IP_RECURSIVE=off
export FRAPPE_SITE_NAME_HEADER="${SITE_NAME:-garage.local}" PROXY_READ_TIMEOUT=300 CLIENT_MAX_BODY_SIZE=50m
cat > /tmp/inject.txt <<'EOS'
  error_page 502 503 504 =200 @starting;
  location @starting {
    default_type text/html;
    add_header Cache-Control "no-store";
    return 200 '<!doctype html><meta charset=utf-8><meta http-equiv=refresh content=4><title>Starting</title><body style="font-family:sans-serif;text-align:center;margin-top:18vh;color:#333"><h2>The garage system is starting...</h2><p>This page refreshes by itself. It usually takes about a minute.</p></body>';
  }
  location = /healthz { access_log off; return 200 "ok"; }
EOS
envsubst '${BACKEND} ${SOCKETIO} ${NGINX_LISTEN_PORT} ${UPSTREAM_REAL_IP_ADDRESS} ${UPSTREAM_REAL_IP_HEADER} ${UPSTREAM_REAL_IP_RECURSIVE} ${FRAPPE_SITE_NAME_HEADER} ${PROXY_READ_TIMEOUT} ${CLIENT_MAX_BODY_SIZE}' \
  < /templates/nginx/frappe.conf.template \
  | awk 'BEGIN{d=0} {print} /^server \{/ && !d {while((getline l < "/tmp/inject.txt")>0) print l; d=1}' > /etc/nginx/conf.d/frappe.conf
# run nginx workers as the user that owns the files (the official image runs nginx as "frappe")
exec nginx -g "user frappe root; daemon off;"
