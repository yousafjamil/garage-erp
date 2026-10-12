# Running on Render (single service)

ERPNext cannot run on Render's **Free** plan (about 512 MB RAM and no persistent disk: it would run out of memory and lose its data
on every restart). It runs on **one paid web service with a persistent disk**, using `render/Dockerfile`, which packs everything into one
container: MariaDB 11.8, Redis, web server, background worker, scheduler, real-time service and nginx (supervised by supervisord).
Measured locally with a 2 GB limit: about 750 MB in use, all tests passing.

## Free plan: demo mode (works, but nothing is kept)
`render.free.yaml` (or the same four settings by hand) runs a ready-made **demo**: sample customers, cars and jobs at every stage are baked
into the image (`render/seed`), so a start only loads about 1 MB of data and needs no install. Measured with a hard 512 MB limit
(x86 and ARM): ready in about 20 s, 320 MB idle, about 430 MB after generating invoice/quotation/job-card PDFs and four reports, no kills.
Settings on the service: `LITE=1`, `DEMO_SEED=1`, `SITE_NAME=garage.local`, `ADMIN_PASSWORD=Garage@Demo2026`, Dockerfile path
`./render/Dockerfile`, context `.`, health check `/healthz`, **no disk**.
- Logins (password `Garage@Demo2026`): `Administrator`, `manager.demo@example.com`, `reception.demo@example.com`, `technician.demo@example.com`.
- **All changes are lost** whenever the service restarts or spins down (free services sleep after ~15 minutes idle; the next visit takes about a minute).
- Background jobs, scheduled emails and reminders do not run (LITE). One or two people at a time; leave generous gaps between PDFs.
- To refresh the sample data: `./dc exec backend bench --site garage.localhost execute garage_management.demo.seed.load` on a clean site, back it up,
  and replace `render/seed/demo-database.sql.gz` (the site must be named `garage.local`).

## Create it (paid, keeps data)
1. Render dashboard → **New → Blueprint** → pick the `garage-erp` repo (it reads `render.yaml`), or edit your existing service:
   - **Dockerfile Path** `./render/Dockerfile`, **Docker Build Context Directory** `.`
   - **Instance type**: *Standard* (2 GB RAM) or larger. (Check Render's pricing page for the current price.)
   - **Disks → Add disk**: mount path `/data`, 10 GB. (Disks require a paid instance.)
   - **Environment**: `ADMIN_PASSWORD` = the password you want for the `Administrator` login; `SITE_NAME` = `garage.local` (any name; leave as is).
   - **Health Check Path** `/healthz`. Turn **Auto-Deploy** off if you do not want every push to redeploy.
2. Deploy. The **first start takes several minutes** (it creates the database and installs the apps; watch the Logs for `[bootstrap] ready`).
3. Open the service URL (https://<name>.onrender.com), log in as **Administrator** with `ADMIN_PASSWORD`, and run the **Setup Wizard**
   (English, United Arab Emirates, AED, Asia/Dubai, company *Candle Auto Repair Workshop*, abbreviation *CARW*, chart *U.A.E*, no demo data).
4. In Render press **Manual Deploy → Restart** (or redeploy) once: on every start the app migrates itself and applies the garage details
   (address, letterhead, roles, workflow, reports). Then set Tax ID (TRN), SMTP (Email Account) and create users with Role Profiles.

## Small instance ("LITE" mode, 512 MB)
Set the environment variable `LITE=1` to run a stripped-down profile: one web worker, small database buffers, **no background worker, scheduler,
real-time updates or daily backup**, and it skips the migration at start (a migration needs more memory than 512 MB). Measured here with a hard
512 MB limit: boots cleanly, about 380 MB idle and about 440 MB after browsing a few pages. **There is almost no headroom**: generating a PDF
(its own process) or a big report can push it over and the process is killed and restarted. Scheduled emails, notifications and queued jobs do
not run. Treat it as a minimum for 1-2 users, not as a recommendation. After updating the code, run one deploy with `FORCE_MIGRATE=1` on a larger
instance (or temporarily without `LITE`) so the database is migrated. The **Free plan cannot be used even in LITE mode**: it has no disk, so every
restart or 15-minute idle spin-down would erase the data.

## What lives where
| Data | Location |
|---|---|
| Database (MariaDB) | `/data/mysql` |
| Site files, uploads, site config | `/data/sites/<SITE_NAME>` |
| Redis queue | `/data/redis` |
| Daily backups (7 days) | `/data/sites/<SITE_NAME>/private/backups` |

## Notes and limits
- **Everything is one container**, so the service restarts briefly on every deploy and is a single point of failure. Fine for a small garage.
- **Back up off-server**: use *System → Backups* in the app (download), and/or Render disk snapshots. Test a restore (`bench restore`) before relying on it.
- **Memory**: 2 GB is comfortable. A 1 GB instance may work for one or two users but is not recommended.
- **Email** needs SMTP details in *Email Account*; Render blocks nothing special, but use an app password (e.g. Gmail) and keep it out of the repo.
- **Updates**: push to `main`; with Auto-Deploy on, Render rebuilds and the container migrates on start. Take a backup first.
- Local test of exactly this image: `docker build --platform linux/amd64 -f render/Dockerfile -t garage-erp-render .` then
  `docker run -p 10000:10000 -v garage-data:/data -e PORT=10000 -e ADMIN_PASSWORD=... garage-erp-render`.
