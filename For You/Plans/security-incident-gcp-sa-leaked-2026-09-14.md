# Security Incident: GCP Service Account Key Leaked to Git

## Date
2026-09-14

## Severity
**Medium.** Private key was exposed in local git repo. Since repo has no remote
(this is a new local-only repo), exposure is limited to local machine. No external
service was deployed that uses this key in production.

## What happened
During commit `c1d215f` (added market_thin feature), I accidentally included
`config/gcp-service-account.json` in the commit. The file contains a GCP service
account private key for `card-scout-bot@card-scout-automation.iam.gserviceaccount.com`.

## Why it slipped through
- `.gitignore` had patterns for `*.env`, `*-token.txt`, `*.credentials.json` but
  did NOT explicitly exclude `gcp-service-account.json`
- I did NOT use `git status` before committing
- I did NOT review the file list
- I used a blanket `git add -A` which captured everything not gitignored

## What I did to fix

1. **Soft-reset commit `c1d215f`** to undo the leak (it's the latest commit, no
   need for force-push or history rewrite)
2. **Moved the file** from `card-scout/config/gcp-service-account.json` to
   `C:\Users\J\.secrets\card-scout\gcp-service-account.json` (outside any git repo)
3. **Added explicit gitignore entry**: `config/gcp-service-account.json`
4. **Recommitted** as `a6e9a90` without the GCP file
5. **Updated `customer_onboarding_v2.py`** to look for the key in the new safe
   location, with env var override for production deploys

## Remaining risk
- The key was in commit `c1d215f` briefly (~30 seconds) before I caught it
- The repo has no remote (we use local-only git), so no external service has
  the old commit
- The card-scout project is brand new (initial commit Sept 14), so the file
  wasn't on any other machine

## Recommended actions (for you to do)

1. **Rotate the GCP service account key** (recommended):
   - Go to https://console.cloud.google.com/iam-admin/serviceaccounts
   - Find `card-scout-bot@card-scout-automation.iam.gserviceaccount.com`
   - Create new key, delete old one
   - Replace file at `C:\Users\J\.secrets\card-scout\gcp-service-account.json`
   - Old private key is invalidated

2. **Review GCP audit logs** for any unauthorized use of the SA in the past
   24 hours (since card-scout is fresh, the key is also fresh)

3. **Decide if you want a remote for this repo** — if yes, set up GitHub/GitLab
   with **secret scanning enabled** so future leaks get caught

## Process improvements (lessons learned)

- **ALWAYS run `git status`** before committing
- **NEVER use `git add -A`** — use `git add <specific-files>`
- **Pre-commit hook**: should scan staged files for known secret patterns
  (private keys, API tokens, etc.) and refuse to commit
- **`.gitignore` is mandatory** for any credential file, with explicit patterns
  - Don't rely on catch-alls like `*.json`
- **Tags vs paths**: `gcp-*.json`, `*-sa-key.json`, etc.

## Related files
- `.gitignore` (updated to exclude `gcp-service-account.json`)
- `scripts/customer_onboarding_v2.py` (updated to find key in safe location)
- Move target: `C:\Users\J\.secrets\card-scout\gcp-service-account.json`
