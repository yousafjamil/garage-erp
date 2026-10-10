# All-in-one image for a SINGLE Render web service (paid instance with a persistent disk):
# ERPNext + garage_management + MariaDB + Redis + workers + scheduler + socket.io + nginx, supervised by supervisord.
# Build from the repo root:  docker build --platform linux/amd64 -f render/Dockerfile -t garage-erp-render .
ARG ERPNEXT_VERSION=v16.50.0
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends mariadb-server redis-server supervisor gettext-base procps openssl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /var/log/supervisor /run/mysqld && chown mysql:mysql /run/mysqld

USER frappe
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:0 apps/garage_management apps/garage_management
RUN env/bin/pip install --no-cache-dir --no-deps -e apps/garage_management \
 && (sed -i -e '$a\' sites/apps.txt; grep -qx garage_management sites/apps.txt || echo garage_management >> sites/apps.txt) \
 && ln -sfn /home/frappe/frappe-bench/apps/garage_management/garage_management/public /home/frappe/frappe-bench/assets/garage_management \
 && find apps/garage_management -name __pycache__ -prune -exec rm -rf {} + \
 && chmod -R g=u apps/garage_management

USER root
COPY render/entrypoint.sh render/bootstrap-site.sh render/start-nginx.sh /usr/local/bin/
COPY render/supervisord.conf /etc/supervisor/garage.conf
RUN chmod 755 /usr/local/bin/entrypoint.sh /usr/local/bin/bootstrap-site.sh /usr/local/bin/start-nginx.sh
ENV DATA_DIR=/data
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
