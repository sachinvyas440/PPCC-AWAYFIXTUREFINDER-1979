# Fixture List Watcher

Automatically checks https://thefixturelist.org.uk/?page_id=209&acadp_category=home_fixture_offered
every 5 minutes and sends a free push notification to your phone the moment a
new "Home fixture offered" listing appears — so you can message them about an
away fixture before anyone else does.

Cost: £0. Runs on GitHub's free Actions tier + ntfy.sh's free notification service.

## One-time setup (about 10 minutes)

### 1. Get a notification topic (no signup required)
1. Install the **ntfy** app: [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) /
   [iOS](https://apps.apple.com/us/app/ntfy/id1625396347) — or just use https://ntfy.sh in a browser tab on your phone.
2. Pick a random, hard-to-guess topic name, e.g. `ppcc-fixtures-x7q2m` (anyone who knows
   the exact topic name could subscribe to it too, so don't use anything obvious).
3. In the app, tap "+" and subscribe to that topic name.
4. Send yourself a test notification by visiting:
   `https://ntfy.sh/ppcc-fixtures-x7q2m` and using the "Publish message" button on that page,
   or running: `curl -d "test" https://ntfy.sh/ppcc-fixtures-x7q2m`
   Confirm it lands on your phone.

### 2. Create a free GitHub account (if you don't have one)
https://github.com/signup

### 3. Create a new repository
- Click "New repository", make it **Private** (so your topic name secret isn't exposed),
  name it whatever you like (e.g. `fixturelist-watcher`).
- Upload the three files from this folder, preserving the path:
  - `check.py` → repo root
  - `.github/workflows/check.yml` → exactly that path
  - (this `README.md` is optional, just for your reference)

  Easiest way: on the repo page, click "Add file" → "Upload files", drag in `check.py`
  and this `README.md`, commit. Then click "Add file" → "Create new file", type
  `.github/workflows/check.yml` as the filename (GitHub will auto-create the folders),
  paste the workflow contents, commit.

### 4. Add your ntfy topic as a secret
- In your repo: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `NTFY_TOPIC`
- Value: `ppcc-fixtures-x7q2m` (whatever you picked in step 1)
- Save.

### 5. Turn it on
- Go to the **Actions** tab in your repo. GitHub sometimes asks you to confirm you want
  Actions enabled for a new repo — click "I understand my workflows, go ahead and enable them".
- Click into "Check Fixture List" → "Run workflow" to trigger the first run manually.
  This first run just records what's currently on the site as a baseline (it won't
  notify you about existing listings, only new ones from now on).
- After that, it runs automatically every 5 minutes, forever, for free.

## How it works
- Every 5 minutes, GitHub spins up a tiny temporary Linux machine, runs `check.py`,
  and shuts it down — there's no server for you to maintain.
- `check.py` fetches the "Home fixture offered" category page and compares the
  listings it finds against `state.json` (committed in your repo from the last run).
- If there's anything new, it fires a push notification via ntfy.sh straight to your phone,
  including the listing title and a link back to the site.
- `state.json` then gets updated and committed so the next run knows what's "old news".

## Notes / things to be aware of
- GitHub's free tier allows up to 2,000 Actions minutes/month for private repos — this
  job takes a few seconds per run, so checking every 5 minutes uses a tiny fraction of that.
- GitHub does **not guarantee** the cron fires exactly on time — under high platform load
  it can occasionally run a few minutes late. There's no free way to get a harder real-time
  guarantee than this.
- If thefixturelist.org.uk ever changes its page markup, the listing-detection regex in
  `check.py` may need a small tweak — if notifications stop coming through, that's the
  first thing to check (the script has a fallback pattern, but it's not bulletproof).
- Because the page text is fetched in England-hosted GitHub runners with a standard
  browser User-Agent, this should work without any login — the listings page is public.
