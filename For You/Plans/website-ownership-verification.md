
---
## DEPLOY-FAILURE CASCADE MAPPED (Oct 22 16:06, after Render email: "commit f3d2f0a failed")
TIMELINE nailed:
- f3d2f0a (15:37, tag) -> founder Manual Deploy -> FAILED: IndentationError app.py:156 (the Oct-11 wound, on main for 11d)
- Founder clicks Add Website -> verify fails (tag never live: nothing deployed)
- 60a6782 (15:41, dual-attr) -> (no deploy — auto-deploy DEAD since Oct 11)
- 0ff8f1f (15:58, ALL indent repairs; 53-file origin audit ALL CLEAN) -> pushed, (no auto-deploy)
- Render email = notice of the 15:37 attempt (lags)
FOUNDER ACTION: Manual Deploy -> Deploy latest commit AGAIN (now carrying 0ff8f1f). The failing import CANNOT recur: dashboard/app.py parses clean + imports clean locally in the exact gunicorn manner. The new deploy carries: tag + Stage C routes + B4 consent + repairs = 11 days of backlog in one restart.
IF the fresh manual deploy fails AGAIN: paste the log tail — but it would be a NEW failure class, not indentation (whole tree parse-clean verified).
NOTE: auto-deploy must be re-armed (Settings -> Build & Deploy -> Auto-Deploy ON branch main) — 11-day silent-disconnect is why tonight's manual dance happened at all.
