# Production image: official ERPNext + the garage_management app.
# Build from the repo root:  docker build -f deploy/Dockerfile -t garage-erp:$(git rev-parse --short HEAD) .
ARG ERPNEXT_VERSION=v16.50.0
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER frappe
WORKDIR /home/frappe/frappe-bench

COPY --chown=frappe:0 apps/garage_management apps/garage_management

RUN env/bin/pip install --no-cache-dir --no-deps -e apps/garage_management \
 && (sed -i -e '$a\' sites/apps.txt; grep -qx garage_management sites/apps.txt || echo garage_management >> sites/apps.txt) \
 && bench build --app garage_management \
 && find apps/garage_management -name __pycache__ -prune -exec rm -rf {} + \
 && chmod -R g=u apps/garage_management
