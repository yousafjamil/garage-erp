# Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Garage DocTypes vanish after a restart/migrate | `sites/apps.txt` lost `garage_management`. Dev: the `configurator` service must mount the app (already in `compose.garage.yaml`). Prod: the image's `apps.txt` contains it. Re-add and `migrate`. |
| Python change has no effect | Gunicorn doesn't auto-reload: `./dc restart backend queue-short queue-long scheduler`. |
| PDF fails with `HostNotFoundError` | `host_name` not reachable from the container. Dev: `bench set-config host_name http://frontend:8080`. Prod: set it to `https://<your-domain>`. |
| Queued emails stay *Not Sent* | The scheduler sends them each minute; check it is running (`docker compose ps`), Email Account is the default outgoing, and "Email Queue" errors. |
| "Workflow State transition not allowed" | A new Repair Job must start in *Draft*; later states change only through the Actions menu. |
| "customer has not approved the quotation" | Submit the quotation, then *Customer Decision → Customer Approved*. A Garage Manager/Owner can tick *Override rules* on the job. |
| "must be submitted and fully paid before delivery" | Submit the invoice and record the payment (Create → Payment on the invoice), or use the override. |
| Search doesn't find a new record type | `bench execute frappe.utils.global_search.rebuild_for_doctype --args '["Garage Vehicle"]'` |
| Site down on VPS | `deploy/prod.sh ps`, `deploy/prod.sh logs --tail 100 backend`; HTTPS issues: `logs proxy` (DNS must point at the VPS, ports 80/443 open). |
| Disk filling up | `docker image prune -f`; old backups are pruned by `backup.sh` (KEEP_DAYS). |
