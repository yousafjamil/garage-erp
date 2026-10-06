"""Idempotent garage configuration. Runs on install and on every migrate (via patches)."""
import frappe

ROLES = ["Garage Owner", "Garage Manager", "Receptionist", "Technician"]

ROLE_PROFILES = {
    "Garage Owner": ["Garage Owner", "Garage Manager", "Sales Manager", "Sales User", "Accounts Manager",
                     "Accounts User", "Stock Manager", "Stock User", "Purchase Manager", "Purchase User"],
    "Garage Manager": ["Garage Manager", "Sales Manager", "Sales User", "Stock User", "Accounts User", "Purchase User"],
    "Receptionist": ["Receptionist", "Sales User"],
    "Technician": ["Technician", "Stock User"],
    "Accountant": ["Accounts Manager", "Accounts User"],
    "Inventory Manager": ["Stock Manager", "Stock User", "Purchase Manager", "Purchase User"],
}

SERVICES = [
    "Engine Oil Change", "Brake Service", "AC Service", "Engine Repair", "Transmission Repair",
    "Wheel Alignment", "Tire Replacement", "Battery Replacement", "Diagnostic", "General Inspection",
]
PARTS = ["Brake Pads", "Oil Filter", "Air Filter", "Spark Plug", "Battery", "Engine Oil", "Brake Fluid"]


def after_install():
    create_roles()
    setup_all()


def setup_all():
    create_roles()
    configure_accounting()
    seed_catalog()
    create_role_profiles()
    frappe.db.commit()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def _company():
    return frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")


def _account(company, name, abbr):
    full = f"{name} - {abbr}"
    return full if frappe.db.exists("Account", {"name": full, "is_group": 0}) else None


def configure_accounting():
    company = _company()
    if not company:
        return
    abbr = frappe.db.get_value("Company", company, "abbr")
    # UAE chart picks odd defaults (e.g. "Trade in Opening Fees" as receivable): point them at sensible accounts.
    wanted = {
        "default_receivable_account": "Trade Receivable",
        "default_income_account": "Sales Account",
        "default_expense_account": "Cost Of Goods Sold",
        "default_cash_account": "Main Safe",
        "default_bank_account": "Banks Current Accounts",
    }
    for field, acc in wanted.items():
        full = _account(company, acc, abbr)
        if full:
            frappe.db.set_value("Company", company, field, full)

    # Payment methods: Cash, Card, Bank Transfer, Other
    for old, new in (("Credit Card", "Card"), ("Wire Transfer", "Bank Transfer"), ("Bank Draft", "Other")):
        if frappe.db.exists("Mode of Payment", old) and not frappe.db.exists("Mode of Payment", new):
            frappe.rename_doc("Mode of Payment", old, new, force=True)
    accounts = {"Cash": "Main Safe", "Card": "Visa & Master Credit Cards",
                "Bank Transfer": "Banks Current Accounts", "Other": "Banks Current Accounts"}
    for mode, acc in accounts.items():
        full = _account(company, acc, abbr)
        if not full or not frappe.db.exists("Mode of Payment", mode):
            continue
        doc = frappe.get_doc("Mode of Payment", mode)
        doc.set("accounts", [])
        doc.append("accounts", {"company": company, "default_account": full})
        doc.save(ignore_permissions=True)

    # VAT 5% template is the default for sales and purchases; the rate itself lives in the template.
    for dt in ("Sales Taxes and Charges Template", "Purchase Taxes and Charges Template"):
        tmpl = f"UAE VAT 5% - {abbr}"
        if frappe.db.exists(dt, tmpl):
            frappe.db.set_value(dt, tmpl, "is_default", 1)

    if not frappe.db.exists("Item Group", "Spare Parts"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Spare Parts",
                        "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True)
    frappe.db.set_single_value("Stock Settings", "default_warehouse", f"Stores - {abbr}")


def seed_catalog():
    """Example services/parts from the garage brief. Prices are left at 0 for the garage to fill in."""
    company = _company()
    if not company:
        return
    abbr = frappe.db.get_value("Company", company, "abbr")
    tax = f"UAE VAT 5% - {abbr}"
    base = {"company": company}
    for name in SERVICES:
        _make_item(name, "Services", False, tax, company, abbr)
    for name in PARTS:
        _make_item(name, "Spare Parts", True, tax, company, abbr)


def _make_item(name, group, is_stock, tax, company, abbr):
    if frappe.db.exists("Item", name):
        return
    doc = frappe.get_doc({
        "doctype": "Item", "item_code": name, "item_name": name, "item_group": group,
        "stock_uom": "Nos", "is_stock_item": 1 if is_stock else 0, "is_sales_item": 1, "is_purchase_item": 1 if is_stock else 0,
        "maintain_stock": 1 if is_stock else 0,
    })
    if is_stock:
        doc.append("item_defaults", {"company": company, "default_warehouse": f"Stores - {abbr}"})
    if frappe.db.exists("Item Tax Template", tax):
        doc.append("taxes", {"item_tax_template": tax})
    doc.insert(ignore_permissions=True)


def create_role_profiles():
    for name, roles in ROLE_PROFILES.items():
        if frappe.db.exists("Role Profile", name):
            continue
        doc = frappe.new_doc("Role Profile")
        doc.role_profile = name
        for r in roles:
            if frappe.db.exists("Role", r):
                doc.append("roles", {"role": r})
        doc.insert(ignore_permissions=True)
