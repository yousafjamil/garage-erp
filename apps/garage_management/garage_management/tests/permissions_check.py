"""Role permission matrix for the garage roles. Run:
    ./dc exec -T backend bench --site garage.localhost execute garage_management.tests.permissions_check.run"""
import frappe

# role profile -> (doctype, ptype, expected)
MATRIX = {
    "Receptionist": [("Customer", "create", 1), ("Garage Vehicle", "create", 1), ("Vehicle Check-In", "create", 1),
                     ("Repair Job", "create", 1), ("Quotation", "create", 1), ("Vehicle Inspection", "read", 1),
                     ("Item", "write", 0), ("Journal Entry", "read", 0), ("Stock Entry", "create", 0), ("Garage Vehicle", "delete", 0)],
    "Technician": [("Repair Job", "write", 1), ("Vehicle Inspection", "create", 1), ("Garage Vehicle", "read", 1),
                   ("Customer", "create", 0), ("Sales Invoice", "read", 0), ("Journal Entry", "read", 0),
                   ("Vehicle Check-In", "create", 0), ("Garage Vehicle", "write", 0)],
    "Garage Manager": [("Repair Job", "create", 1), ("Quotation", "submit", 1), ("Sales Invoice", "create", 1),
                       ("Garage Vehicle", "delete", 1), ("User", "create", 0), ("Item", "write", 1)],
    "Garage Owner": [("Repair Job", "delete", 1), ("Sales Invoice", "submit", 1), ("Payment Entry", "create", 1),
                     ("Item", "write", 1), ("Purchase Order", "create", 1), ("Journal Entry", "read", 1)],
    "Accountant": [("Sales Invoice", "submit", 1), ("Payment Entry", "create", 1), ("Journal Entry", "create", 1),
                   ("Repair Job", "read", 1), ("Repair Job", "write", 0), ("Garage Vehicle", "write", 0), ("Item", "write", 0)],
    "Inventory Manager": [("Item", "write", 1), ("Purchase Order", "create", 1), ("Stock Entry", "create", 1),
                          ("Warehouse", "write", 1), ("Repair Job", "write", 0), ("Sales Invoice", "create", 0), ("Journal Entry", "read", 0)],
}


def run():
    frappe.set_user("Administrator")
    results = []
    for profile, checks in MATRIX.items():
        email = f"perm.{profile.lower().replace(' ', '.')}@example.com"
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True)
        u = frappe.get_doc({"doctype": "User", "email": email, "first_name": profile, "send_welcome_email": 0,
                            "role_profile_name": profile}).insert(ignore_permissions=True)
        u.reload()
        for dt, ptype, want in checks:
            got = int(bool(frappe.has_permission(dt, ptype, user=email)))
            ok = got == want
            results.append(ok)
            print(("PERM OK   " if ok else "PERM FAIL ") + f"{profile:18} {ptype:7} {dt:20} expected={want} got={got}")
        frappe.delete_doc("User", email, force=True)
    frappe.db.commit()
    print("PERM SUMMARY", sum(results), "/", len(results))
