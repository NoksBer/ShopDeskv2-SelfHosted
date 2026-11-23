"""Dashboard summary. Ticket numbers respect visibility: technicians only count tickets assigned to them."""
import json
from datetime import datetime, timedelta, timezone

_R = "(:restrict = 0 OR EXISTS (SELECT 1 FROM ticket_assignees ra WHERE ra.ticket_id = t.id AND ra.user_id = :uid))"

COUNTS_SQL = ("""
SELECT
  SUM(CASE WHEN s.is_closed = 0 THEN 1 ELSE 0 END) AS open_count,
  SUM(CASE WHEN s.is_closed = 0 AND t.due_date IS NOT NULL AND t.due_date < :today THEN 1 ELSE 0 END) AS overdue,
  SUM(CASE WHEN s.is_closed = 0 AND t.due_date IS NOT NULL AND t.due_date >= :today AND t.due_date <= :week_end
           THEN 1 ELSE 0 END) AS due_week,
  SUM(CASE WHEN s.is_closed = 0 AND NOT EXISTS (SELECT 1 FROM ticket_assignees ua WHERE ua.ticket_id = t.id)
           THEN 1 ELSE 0 END) AS unassigned,
  SUM(CASE WHEN s.is_closed = 1 AND t.closed_at >= :week_ago THEN 1 ELSE 0 END) AS closed_week
FROM tickets t JOIN ticket_statuses s ON s.id = t.status_id
WHERE """ + _R)

BY_STATUS_SQL = ("""
SELECT s.id, s.name, s.is_closed,
       (SELECT COUNT(*) FROM tickets t WHERE t.status_id = s.id AND """ + _R + """) AS n
FROM ticket_statuses s WHERE s.active = 1 ORDER BY s.sort_order, s.name
""")

MINE_SQL = """
SELECT t.id, t.number, t.title, t.priority, t.due_date, c.name AS customer_name, s.name AS status_name
FROM tickets t
JOIN ticket_statuses s ON s.id = t.status_id
JOIN customers c ON c.id = t.customer_id
JOIN ticket_assignees a ON a.ticket_id = t.id AND a.user_id = :uid
WHERE s.is_closed = 0
ORDER BY CASE t.priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
         COALESCE(t.due_date, '9999-12-31'), t.created_at
LIMIT 10
"""

RECENT_SQL = ("""
SELECT h.id, h.ts, h.kind, h.detail, u.name AS user_name, t.id AS ticket_id, t.number, t.title
FROM ticket_history h
JOIN tickets t ON t.id = h.ticket_id
LEFT JOIN users u ON u.id = h.user_id
WHERE """ + _R + """
ORDER BY h.id DESC LIMIT 10
""")


def register(router):
    router.add("GET", "/api/dashboard", get_dashboard, "authed")


def get_dashboard(ctx):
    user = ctx.user
    if not user.can("tickets.read"):
        return {"tickets": None}
    restrict = 0 if user.can("tickets.read_all") else 1
    # "today" is the server's UTC date until per-shop timezones are applied.
    today = datetime.now(timezone.utc).date()
    params = {"restrict": restrict, "uid": user.id, "today": today.isoformat(),
              "week_end": (today + timedelta(days=7)).isoformat(),
              "week_ago": (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    row = ctx.db.execute(COUNTS_SQL, params).fetchone()
    counts = {k: (row[k] or 0) for k in ("open_count", "overdue", "due_week", "unassigned", "closed_week")}
    if restrict:
        counts["unassigned"] = None          # unassigned tickets are invisible to this user
    by_status = [dict(r) for r in ctx.db.execute(BY_STATUS_SQL, params)]
    mine = [dict(r) for r in ctx.db.execute(MINE_SQL, {"uid": user.id})]
    recent = []
    for r in ctx.db.execute(RECENT_SQL, params):
        item = dict(r)
        item["detail"] = json.loads(item["detail"])
        recent.append(item)
    return {"tickets": {"counts": counts, "by_status": by_status, "my_open": mine, "recent": recent}}
