# Garage ERP — Candle Auto Repair Workshop & Pak Mohmand General Transport

One simple web app for **two businesses**, built on **ERPNext v16 / Frappe v16** plus one small custom app, `garage_management`.
Currency AED, UAE VAT 5 %. Each business has its own **Quotation, Tax Invoice, Job Card, Statement and Receipt**, numbered separately,
printed on its own letterhead and looking like the supplied sample documents.

```
Job Card → Quotation → Tax Invoice → Payment (oldest invoice first) → Monthly Statement (balance carried forward)
```

Menu (7 items): **Home · Job Cards · Quotations · Invoices · Statements · Payments · Customers**.

Every quotation/invoice has its own free-text lines, vehicle / reference, LPO reference and note; the company wording is only an editable default.

## Repository layout
```
apps/garage_management/   custom app (Job Card + Statement DocTypes, print formats, setup code, demo data, tests)
frappe_docker/            official frappe/frappe_docker (vendored, unmodified)
compose.garage.yaml       dev override: mounts the app into the containers
dc                        dev wrapper:  ./dc ps | ./dc exec backend bench ...
deploy/                   production (Hostinger VPS later)
render/ render*.yaml      free Render demo (baked sample data) / paid single service
docs/                     guides
```

## Documentation
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) — daily use
- [docs/PRINT_FORMATS.md](docs/PRINT_FORMATS.md) — documents and letterheads
- [docs/RENDER.md](docs/RENDER.md) — Render (free demo / paid)
- [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md), [docs/DEPLOYMENT_HOSTINGER.md](docs/DEPLOYMENT_HOSTINGER.md), [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Tests
`./dc exec -T backend bench --site garage.localhost execute garage_management.tests.simple_scenario.run` — end-to-end for both businesses (15 checks).
