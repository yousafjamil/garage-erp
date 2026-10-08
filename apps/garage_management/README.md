# garage_management

Frappe app that adds the garage workflow to ERPNext v16. Does not modify ERPNext/Frappe.

**DocTypes:** Garage Vehicle, Vehicle Check-In, Vehicle Inspection (+ Inspection Item), Repair Job (+ Repair Job Service/Part).
**Workflow:** *Repair Job Workflow* (Draft → Checked In → Inspection → Waiting for Quotation → Waiting for Customer Approval → Approved → In Repair → Quality Check → Ready for Delivery → Completed / Cancelled).
**Rules (in `repair_job.py`):** repair/quality/delivery need an approved quotation; delivery needs a submitted, fully paid invoice; Garage Manager/Owner may override; technicians see only their own jobs.
**API (`api/repair_job.py`):** `make_quotation`, `record_approval`, `make_invoice` (Quotation → Sales Order → Sales Invoice with stock update).
**Custom fields:** `vehicle`, `plate_number`, `repair_job` on Quotation/Sales Order/Sales Invoice; approval fields on Quotation.
**Reports:** Vehicle Service History, Jobs by Status, Technician Performance, Parts Used, Services Performed, Low Stock Parts.
**Setup code (`setup/`)** — idempotent, runs on install and every `migrate`: roles & role profiles, account defaults, payment methods, default VAT template, item groups & example items, custom fields, workflow, print formats (`print_formats/`), dashboard/workspace, notifications, search config, menu simplification for a small garage.
**One-off:** `setup/company.py::apply` (garage address/letterhead); `setup/dev.py` (Mailpit, dev only).
**Tests (`tests/`):** `e2e_scenario.run`, `permissions_check.run`, `pdf_check.run`.

No tax rates or credentials are hard-coded: VAT comes from ERPNext tax templates, email from the Email Account.
Install on a bench: `bench get-app <repo-path>/apps/garage_management && bench --site <site> install-app garage_management`.
