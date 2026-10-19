"""Idempotent configuration. Runs on install and on every migrate."""
import frappe

ROLES = ["Garage Owner", "Garage Manager", "Receptionist", "Technician"]

ROLE_PROFILES = {
    "Garage Owner": ["Garage Owner", "Garage Manager", "Sales Manager", "Sales User", "Accounts Manager", "Accounts User", "Item Manager"],
    "Garage Manager": ["Garage Manager", "Sales Manager", "Sales User", "Accounts User", "Item Manager"],
    "Receptionist": ["Receptionist", "Sales User", "Accounts User"],
    "Technician": ["Technician", "Sales User"],
    "Accountant": ["Accounts Manager", "Accounts User"],
}


def after_install():
    create_roles()
    setup_all()


def setup_all():
    create_roles()
    from garage_management.setup import companies, custom_fields, dashboard, print_formats, simplify, whitelabel
    custom_fields.create()
    companies.apply()
    simplify.apply()
    create_role_profiles()
    configure_search()
    print_formats.create()
    dashboard.create()
    whitelabel.apply()
    frappe.db.commit()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def create_role_profiles():
    for name, roles in ROLE_PROFILES.items():
        doc = frappe.get_doc("Role Profile", name) if frappe.db.exists("Role Profile", name) else frappe.new_doc("Role Profile")
        doc.role_profile = name
        doc.name = name
        if doc.is_locked:  # a failed earlier run can leave the "queued" lock file behind
            doc.unlock()
        have = {r.role for r in doc.get("roles", [])}
        for r in roles:
            if r not in have and frappe.db.exists("Role", r):
                doc.append("roles", {"role": r})
        doc.save(ignore_permissions=True)


def configure_search():
    """Job cards, quotations, invoices and statements are findable from the search bar; customers by phone."""
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    gs = frappe.get_single("Global Search Settings")
    gs.set("allowed_in_global_search", [r for r in gs.allowed_in_global_search if frappe.db.exists("DocType", r.document_type)])
    have = {r.document_type for r in gs.allowed_in_global_search}
    for dt in ("Service Job Card", "Customer Statement"):
        if dt not in have:
            gs.append("allowed_in_global_search", {"document_type": dt})
    gs.save(ignore_permissions=True)
    make_property_setter("Customer", None, "search_fields", "customer_name,customer_group,territory,mobile_no", "Data",
                         for_doctype=True, validate_fields_for_doctype=False)
