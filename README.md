# Garage ERP — Candle Auto Repair Workshop

A garage management system built on **ERPNext v16 / Frappe v16** (open-source ERP) plus one small custom Frappe app,
`garage_management`. Sized for a small garage (a handful of users). Currency AED, UAE VAT.

```
Customer → Vehicle → Check-In → Inspection → Repair Job → Quotation → Customer Approval
        → Repair → Quality Check → Invoice → Payment → Delivery → Vehicle Service History
```

| Need | Where it lives |
|---|---|
| Customers, items (services/parts), stock, suppliers, purchasing, quotations, invoices, payments, VAT, email, PDFs, accounting, reports | **Standard ERPNext** (configured, not modified) |
| Vehicles, check-in, inspection, repair job (workflow), approval gate, job→quotation→invoice, service history, dashboard | **`apps/garage_management`** (custom app) |

ERPNext core is never edited, so upgrades stay simple.

## Repository layout
```
apps/garage_management/   custom Frappe app (DocTypes, workflow, reports, print formats, setup code, tests)
frappe_docker/            official frappe/frappe_docker (vendored, unmodified)
compose.garage.yaml       dev override: mounts the app into the containers
dc                        dev wrapper:  ./dc ps | ./dc exec backend bench ...
deploy/                   production: Dockerfile, prod.sh, deploy.sh, backup.sh, restore.sh, bootstrap-vps.sh
docs/                     guides (see below)
```

## Documentation
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) — daily garage workflow, roles, adding users
- [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) — run and develop on a Mac
- [docs/DEPLOYMENT_HOSTINGER.md](docs/DEPLOYMENT_HOSTINGER.md) — production on a Hostinger VPS, security, backups, updates
- [docs/ERPNEXT_MAPPING.md](docs/ERPNEXT_MAPPING.md) — what is standard ERPNext vs custom, and why
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [apps/garage_management/README.md](apps/garage_management/README.md) — the custom app

## Status
All phases through production rehearsal are done and tested locally (end-to-end 24/24, role permissions 44/44,
backup→restore verified on a production-style stack). The only step left is the real VPS deployment
(needs the VPS and domain) — follow `docs/DEPLOYMENT_HOSTINGER.md`.
