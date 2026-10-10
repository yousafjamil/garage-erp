import frappe
from frappe.utils import add_days, cint, date_diff, getdate, nowdate

REASONS = (("next_service_date", "Service due"), ("registration_expiry", "Registration expires"), ("insurance_expiry", "Insurance expires"))


def due_rows(days=None, vehicle=None):
    """One row per upcoming/overdue reminder (service date, registration expiry, insurance expiry)."""
    days = cint(days if days is not None else frappe.db.get_single_value("Garage Settings", "reminder_days_before")) or 7
    limit = getdate(add_days(nowdate(), days))
    filters = {"status": ["!=", "Inactive"]}
    if vehicle:
        filters["name"] = vehicle
    rows = []
    for v in frappe.get_all("Garage Vehicle", filters=filters, fields=["name", "plate_number", "make", "model", "customer",
                            "customer_name", "customer_phone", "current_mileage", "next_service_mileage"] + [r[0] for r in REASONS]):
        for field, label in REASONS:
            when = v.get(field)
            if when and getdate(when) <= limit:
                rows.append(dict(vehicle=v.name, plate_number=v.plate_number, car=f"{v.make} {v.model}", customer=v.customer,
                                 customer_name=v.customer_name, phone=v.customer_phone, reason=label, due_date=when,
                                 days_left=date_diff(when, nowdate()), mileage=v.current_mileage, next_mileage=v.next_service_mileage))
    rows.sort(key=lambda r: r["days_left"])
    return rows


def daily_vehicle_reminders():
    """Daily: tell the front desk / managers which vehicles need contacting."""
    rows = due_rows()
    if not rows:
        return
    users = set()
    for role in ("Receptionist", "Garage Manager", "Garage Owner"):
        users.update(frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent"))
    users = [u for u in users if u not in ("Administrator", "Guest") and frappe.db.get_value("User", u, "enabled")]
    sample = ", ".join(f"{r['plate_number']} ({r['reason'].lower()})" for r in rows[:8])
    for u in users:
        frappe.get_doc({"doctype": "Notification Log", "for_user": u, "type": "Alert", "document_type": "Report",
                        "document_name": "Vehicle Reminders", "subject": f"{len(rows)} vehicle reminder(s) due",
                        "email_content": sample}).insert(ignore_permissions=True)
