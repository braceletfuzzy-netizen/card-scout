"""
CAMEL FLAGS — the file-based flag layer (the no-Render-dashboard workaround).

Precedence: config/camel_flags.json (file-based, git-transportable) >
environment override (Render env var, if set) > safe default (allowlist, dry-run).

Law: values are read-in-place; never echoed; never logged at info level.
The flags file lives in the repo — the founder flips a flag by editing the
JSON and pushing (the deploy = the flip). The env override stays king for the
Render-dashboard path when the founder IS present.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

_FLAGS_FILE = Path(__file__).resolve().parent.parent / "config" / "camel_flags.json"


def _read_flags_file() -> dict:
    try:
        return json.loads(_FLAGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def _cached_flags() -> tuple[str, str]:
    f = _read_flags_file()
    return (
        (f.get("PUBLIC_USERS_MODE") or "").strip().lower(),
        (f.get("PUBLIC_USER_ALERTS_ENABLED") or "").strip().lower(),
    )


def public_users_mode() -> str:
    """'open' | 'allowlist'. Env override wins; flags file second; default allowlist."""
    env = (os.environ.get("PUBLIC_USERS_MODE") or "").strip().lower()
    if env in ("open", "allowlist"):
        return env
    file, _ = _cached_flags()
    if file in ("open", "allowlist"):
        return file
    return "allowlist"


def user_alerts_enabled() -> bool:
    """True only if the human explicitly turned the send path on (env override or
    the flags file). Default = False (dry-run)."""
    env = (os.environ.get("PUBLIC_USER_ALERTS_ENABLED") or "").strip().lower()
    if env:
        return env in ("1", "true", "yes", "on")
    _, file = _cached_flags()
    return file in ("1", "true", "yes", "on")
