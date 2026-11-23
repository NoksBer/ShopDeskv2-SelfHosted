"""Small shared helpers: errors, ids, time, input validation."""
import re
import secrets
import time
from datetime import date, datetime, timezone


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_ts():
    return int(time.time())


def new_id():
    """16 hex chars. Random ids (not counters) so ids from one tenant never collide with another's."""
    return secrets.token_hex(8)


EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")
TZ_RE = re.compile(r"^[A-Za-z0-9_+\-/]{1,64}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


def clean_text(body, key, max_len=200, required=False, default=""):
    value = body.get(key, default)
    if value is None:
        value = default
    if not isinstance(value, str):
        raise ApiError(400, "%s must be text" % key)
    value = value.strip()
    if required and not value:
        raise ApiError(400, "%s is required" % key)
    if len(value) > max_len:
        raise ApiError(400, "%s is too long" % key)
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ApiError(400, "%s contains invalid characters" % key)
    return value


def clean_email(body, key="email"):
    value = clean_text(body, key, max_len=254, required=True).lower()
    if not EMAIL_RE.match(value):
        raise ApiError(400, "Enter a valid email address")
    return value


def clean_date(body, key):
    """Optional ISO date (YYYY-MM-DD). Returns None when empty."""
    value = body.get(key)
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        raise ApiError(400, "%s must be a date (YYYY-MM-DD)" % key)
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ApiError(400, "%s is not a valid date" % key)
    return value


def like_pattern(text):
    """Escape LIKE wildcards (use with ESCAPE '\\') and wrap for a contains-search."""
    return "%" + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "shop"
