# PostgreSQL evaluation (October 2026)

**Result: not viable with ERPNext v16.50.0. Stay on MariaDB.**

Prototype: official `frappe_docker` Postgres override (postgres:15), custom image with `garage_management`, fresh site,
Setup Wizard, garage setup, then the standard end-to-end scenario (`tests/e2e_scenario.py`).

| Step | Postgres result |
|---|---|
| Install ERPNext + garage_management, DocTypes, workflow, print formats, dashboard, roles | works (after small fixes below) |
| Setup Wizard in the browser | works |
| Stock Entry / any stock ledger write | **fails** — `erpnext/stock/doctype/stock_closing_entry/stock_closing_entry.py` (`get_closing_entry_for_closed_period`): `GroupingError: column "tabPeriod Closing Voucher.creation" must appear in the GROUP BY clause` |
| Any General Ledger posting (every invoice / payment) | **fails** — `erpnext/accounts/general_ledger.py::validate_against_pcv`, same error |
| Website search indexer (background job) | errors (`t1.name must appear in GROUP BY`) — non-fatal |

The failing SQL is in ERPNext core and relies on MariaDB's permissive `GROUP BY`. Without these two paths no invoice can be
posted, so the garage workflow cannot complete. Fixing it means patching ERPNext (several places, re-done at every upgrade),
which contradicts the "do not modify core / stay upgradeable" rule. Hostinger VPS + MariaDB (tested: end-to-end 24/24,
permissions 44/44, backup/restore) remains the supported path. Re-evaluate only if a future ERPNext release declares Postgres support.

Also: Render has no shared disk between services and no managed MariaDB, so it is not a fit even with Postgres (see chat notes).

## Fixes that came out of this work (kept; they also apply to MariaDB)
- `make_property_setter(..., validate_fields_for_doctype=False)` — avoids Frappe re-validating every field of core doctypes.
- Role Profile setup releases stale "queued" lock files left by a failed earlier run.
- Branding step waits until the Setup Wizard is complete (System Settings needs language/time zone) — this would have broken a first install on **any** database.
