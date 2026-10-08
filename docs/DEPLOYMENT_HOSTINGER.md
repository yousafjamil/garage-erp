# Production deployment — Hostinger VPS

Architecture: `Internet → Traefik (HTTPS, Let's Encrypt) → nginx → ERPNext (gunicorn) + workers + scheduler + websocket → MariaDB + Redis`,
all in Docker Compose on one VPS. MariaDB and Redis are **not** published to the internet.

## 0. What you need
- A Hostinger **VPS** (KVM, not shared hosting), Ubuntu 22.04/24.04. For a small garage: **2 vCPU, 4 GB RAM (8 GB comfortable), 40+ GB SSD**. Add 2 GB swap if 4 GB.
- A domain/subdomain (e.g. `erp.yourgarage.com`) with an **A record → VPS IP**.
- The repo URL (https://github.com/yousafjamil/garage-erp) and, if it is private, a read-only deploy key/token.
- SMTP details for outgoing mail (e.g. Gmail app password, Zoho, or Hostinger mail) — entered in the UI, never in code.
- An off-server backup target for `rclone` (Google Drive, Backblaze B2, S3, …).
> Confirm current requirements against https://docs.frappe.io before installing; versions are pinned in `deploy/.env.prod` (`ERPNEXT_VERSION`).

## 1. Prepare the server (once)
```bash
ssh root@<VPS-IP>
apt-get update && apt-get install -y git
git clone https://github.com/yousafjamil/garage-erp.git /opt/garage-erp
# put your SSH public key in /home/deploy/.ssh/authorized_keys FIRST (see script header), then:
bash /opt/garage-erp/deploy/bootstrap-vps.sh deploy
```
This installs Docker, enables the firewall (22/80/443 only), fail2ban, automatic security updates and, once your key is
installed, disables SSH password and root login. Then `ssh deploy@<VPS-IP>`; `sudo chown -R deploy /opt/garage-erp`.

## 2. Configure secrets (never commit)
```bash
cd /opt/garage-erp
cp deploy/.env.prod.example deploy/.env.prod && chmod 600 deploy/.env.prod
nano deploy/.env.prod     # DB_PASSWORD (openssl rand -base64 24 | tr -d '/+='), SITE_NAME, SITES_RULE, LETSENCRYPT_EMAIL
```
| Variable | Meaning |
|---|---|
| `ERPNEXT_VERSION` | pinned ERPNext/Frappe release (v16.50.0) |
| `CUSTOM_IMAGE` / `CUSTOM_TAG` | locally built image `garage-erp:<git sha>` (set by `deploy.sh`) |
| `DB_PASSWORD` | MariaDB root password (internal network only) |
| `SITE_NAME` / `SITES_RULE` | public hostname, e.g. `erp.yourgarage.com` / ``Host(`erp.yourgarage.com`)`` |
| `LETSENCRYPT_EMAIL` | certificate expiry contact |
| `GUNICORN_WORKERS/THREADS` | 2/4 is enough for a small garage |

## 3. First start
```bash
deploy/deploy.sh --first-run            # builds the image (ERPNext + garage_management), starts the stack + HTTPS
source <(grep -E '^(SITE_NAME|DB_PASSWORD)=' deploy/.env.prod)
deploy/prod.sh exec backend bench new-site "$SITE_NAME" --mariadb-user-host-login-scope=% \
   --db-root-password "$DB_PASSWORD" --admin-password '<strong password>' \
   --install-app erpnext --install-app garage_management --set-default
deploy/prod.sh exec backend bench --site "$SITE_NAME" set-config host_name "https://$SITE_NAME"
```
Open `https://<your domain>` (certificate is issued automatically; DNS must already point to the VPS), sign in as
`Administrator`, run the **Setup Wizard** (English, United Arab Emirates, AED, Asia/Dubai, company *Candle Auto Repair Workshop*,
abbreviation *CARW*, chart *U.A.E*, no demo data), then:
```bash
deploy/prod.sh exec backend bench --site "$SITE_NAME" migrate
deploy/prod.sh exec backend bench --site "$SITE_NAME" execute garage_management.setup.company.apply
```
In the UI: set **Company → Tax ID (TRN)**; **Settings → Email Account** (outgoing SMTP, default outgoing); create users with
Role Profiles; ask the accountant to confirm VAT/accounts (see USER_GUIDE). Disable `Administrator`'s everyday use.

## 4. Security checklist
- Firewall allows only 22/80/443; `docker compose ps` must show no published 3306/6379.
- SSH: key login only, no root login (bootstrap script). Strong unique passwords; enable 2FA for owner/accountant (*Settings → System Settings → Enable Two Factor Auth*).
- Secrets only in `deploy/.env.prod` (chmod 600, git-ignored) and the ERPNext UI. The DB password also protects backups — store it in a password manager.
- Keep the server patched (unattended-upgrades) and update ERPNext deliberately (section 6).
- ERPNext permissions: use Role Profiles; give staff the minimum profile.

## 5. Backups (do not skip)
```bash
rclone config                                   # create a remote, e.g. "gdrive" or "b2"
crontab -e
30 2 * * *  RCLONE_REMOTE=gdrive:garage-erp-backups /opt/garage-erp/deploy/backup.sh >> /var/log/garage-backup.log 2>&1
```
`backup.sh` makes a full backup (database, public + private files, `site_config` with the encryption key), copies it to
`/var/backups/garage`, keeps 14 days, and copies it off-server with rclone. **Test a restore** (a backup is only real once restored):
```bash
deploy/restore.sh <prefix>      # e.g. 20261007_023000-erp_yourgarage_com  (asks you to type YES)
```
This was tested locally: data was deleted/changed and the restore brought it back (13 check-ins, 10 job services, company details).
Repeat the test on the VPS after go-live, ideally on a copy.

## 6. Updating
- **Custom app / config changes:** push to GitHub from the Mac → on the VPS `cd /opt/garage-erp && git pull && deploy/deploy.sh`
  (backup → build → restart → migrate). Roll back: `git checkout <old-commit> && deploy/deploy.sh`, or `deploy/restore.sh` if data changed.
- **ERPNext upgrade:** change `ERPNEXT_VERSION` (and the Dockerfile ARG) to the new release, read its release notes, test on the Mac rehearsal first
  (`deploy/prod.sh` with `deploy/.env.rehearsal`, see below), then `deploy/deploy.sh`.
- **Local rehearsal of production** (no HTTPS): `ENV_FILE=deploy/.env.rehearsal USE_HTTPS=0 COMPOSE_PROJECT_NAME=garageprod deploy/prod.sh up -d`.

## 7. Operations
`deploy/prod.sh ps | logs -f backend | restart` · site shell: `deploy/prod.sh exec backend bench --site $SITE_NAME console` ·
health: `curl -s https://<domain>/api/method/ping`.
