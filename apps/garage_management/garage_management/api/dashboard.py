import frappe

from garage_management.garage_management.report.low_stock_parts.low_stock_parts import LOW_STOCK_SQL


@frappe.whitelist()
def low_stock_count():
    return len(frappe.db.sql(LOW_STOCK_SQL))


def low_stock_alert():
    """Daily: tell the inventory/owner roles which parts are at or below their minimum level."""
    rows = frappe.db.sql(LOW_STOCK_SQL, as_dict=True)
    if not rows:
        return
    users = set()
    for role in ("Stock Manager", "Garage Owner", "Garage Manager"):
        users.update(frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent"))
    users = [u for u in users if u not in ("Administrator", "Guest") and frappe.db.get_value("User", u, "enabled")]
    parts = ", ".join(f"{r.item_name} ({r.actual_qty:g})" for r in rows[:10])
    for u in users:
        frappe.get_doc({"doctype": "Notification Log", "for_user": u, "type": "Alert", "document_type": "Report",
                        "document_name": "Low Stock Parts", "subject": f"Low stock: {len(rows)} part(s)",
                        "email_content": parts}).insert(ignore_permissions=True)
