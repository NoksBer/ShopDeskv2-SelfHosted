"""Permission catalogue and default role grants. The owner role implicitly has every permission."""

PERMISSIONS = [
    "business.manage",
    "users.manage",
    "users.read",
    "customers.read",
    "customers.write",
    "equipment.read",
    "equipment.write",
    "tickets.read",
    "tickets.write",
    "tickets.assign",
    "tickets.read_all",     # without it, a user only sees tickets assigned to them
    "audit.read",
]

# (name, label, default permissions)
ROLES = [
    ("owner", "Owner", list(PERMISSIONS)),
    ("manager", "Manager", [
        "users.read", "customers.read", "customers.write", "equipment.read", "equipment.write",
        "tickets.read", "tickets.write", "tickets.assign", "tickets.read_all", "audit.read",
    ]),
    ("technician", "Technician", [
        "customers.read", "equipment.read", "equipment.write", "tickets.read", "tickets.write",
    ]),
    ("front_desk", "Front desk", [
        "customers.read", "customers.write", "equipment.read", "equipment.write",
        "tickets.read", "tickets.write", "tickets.assign", "tickets.read_all",
    ]),
]

# Access levels a route may declare besides a permission name.
ACCESS_LEVELS = ("public", "authed", "platform")
