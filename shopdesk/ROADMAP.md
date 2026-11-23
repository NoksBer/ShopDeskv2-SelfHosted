# ShopDesk implementation plan

Legend: [x] implemented AND tested (tests run and passing), [~] written, NOT yet run, [ ] not started.

## Phase 1 - Core application / MVP foundation

- [~] 1. Skeleton: config, router, HTTP layer, test harness
- [~] 2. Migration runner (platform + tenant DBs), initial schemas
- [~] 3. Auth: scrypt, sessions (hashed tokens), CSRF + Origin check, rate limiting, permission-checked routes
- [~] 4. Tenant provisioning, registration, shop-type profiles (terminology, statuses, equipment fields)
- [~] Minimal UI: register / sign in / business profile / team list
- [~] Platform admin: CLI `create-admin`, sign in, list / suspend / reactivate tenants (metadata only)
- [~] 5. Staff invites (single-use 7-day link, token hashed at rest), role changes, deactivate (kills sessions). Invite links are
      copied by the owner; emailing them arrives with Phase 2 email. Password reset flow is NOT done yet.
- [~] 6. Customers and equipment: search, archive/restore, profile-driven equipment fields (owner can reconfigure via
      `PUT /api/equipment/fields`; there is no UI for that yet), audit without customer PII. Photos wait for Phase 2 uploads.
- [~] 7. Tickets: create/edit/search/filter, configurable statuses (editor in Settings), priority, due date, multi-assignee,
      append-only history, configurable numbering, per-technician visibility (`tickets.read_all`). Tickets cannot be deleted
      (use the Cancelled status). Due dates compare against the server's UTC date, not the shop's timezone yet.
- [~] 8. Activity log screen (filter by area and person, paging). Only users with `audit.read` (owner, manager) see it.
- [~] 9. Dashboard: open / overdue / due in 7 days / unassigned / closed in 7 days, open by status, my open tickets,
      recent activity. Technicians see only their own assigned tickets. "Today" is the server's UTC date.
- [ ] 10. Tenant-isolation tests for every new route (existing suite covers steps 1-4 routes)
- [~] 11. Installer (`install/shopdesk.sh`): written, never run on Proxmox
- [ ] 12. Restore test on a clean container

## Status note

No Python interpreter was available on the development PC, so NOTHING in this repo has been executed.
First action on any machine with Python 3.11+: `python -m unittest discover -s tests -v`, fix failures, then flip [~] to [x].

## Later phases

See `DESIGN.md` and the product brief (phases 2 to 5).
