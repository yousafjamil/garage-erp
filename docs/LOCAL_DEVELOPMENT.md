# Local development (Mac)

Requirements: Docker Desktop (Compose v2), Git. Tested on macOS 26 / Apple M1, Docker 29. Containers run as
`linux/amd64` (same as the VPS), so the first start is slower under emulation.

## Start
```bash
cd garage-erp
cp frappe_docker/example.env frappe_docker/.env     # then set DB_PASSWORD, HTTP_PUBLISH_PORT=8090, FRAPPE_SITE_NAME_HEADER=garage.localhost
./dc up -d                                          # MariaDB, Redis, backend, workers, scheduler, nginx, mailpit
```
First time only — create the site and install both apps:
```bash
./dc exec backend bench new-site garage.localhost --mariadb-user-host-login-scope=% \
   --db-root-password <DB_PASSWORD> --admin-password <choose> --install-app erpnext --set-default
./dc exec backend bench --site garage.localhost install-app garage_management
./dc exec backend bench --site garage.localhost set-config developer_mode 1
./dc exec backend bench --site garage.localhost set-config host_name http://frontend:8080   # lets PDF generation fetch CSS/logo
```
Open <http://localhost:8090> (Administrator). Run the Setup Wizard (English, United Arab Emirates, AED, Asia/Dubai,
company *Candle Auto Repair Workshop*, abbreviation *CARW*, chart *U.A.E*), then:
```bash
./dc exec backend bench --site garage.localhost migrate                                        # applies garage setup (accounts, VAT default, items, roles, workflow, dashboard…)
./dc exec backend bench --site garage.localhost execute garage_management.setup.company.apply  # address, letterhead, company contact details
./dc exec backend bench --site garage.localhost execute garage_management.setup.dev.configure_dev_mailpit
```
Outgoing mail in dev goes to Mailpit: <http://localhost:8026>.

## Everyday
- Code lives in `apps/garage_management` and is bind-mounted: JS/HTML edits are live; **Python edits need**
  `./dc restart backend queue-short queue-long scheduler`.
- After changing DocType JSON or setup code: `./dc exec backend bench --site garage.localhost migrate`.
- `setup/install.py::setup_all` runs on every `migrate` and is idempotent (it never overwrites the workflow or
  existing records). Change garage defaults there, not by hand.

## Tests
```bash
./dc exec backend bench --site garage.localhost execute garage_management.tests.e2e_scenario.run         # full job scenario, prints E2E OK/FAIL
./dc exec backend bench --site garage.localhost execute garage_management.tests.permissions_check.run    # role matrix
./dc exec backend bench --site garage.localhost execute garage_management.tests.pdf_check.run            # renders all PDFs + sends a quotation to Mailpit
```
These create real test documents — run them on a dev/rehearsal site only.

## Git
Work on `main`, commit per change. To undo something: `git revert <commit>` (or `git checkout <commit> -- <path>`).
