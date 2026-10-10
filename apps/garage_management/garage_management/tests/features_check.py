"""WhatsApp link, next-service automation and reminders. Run:
   ./dc exec -T backend bench --site garage.localhost execute garage_management.tests.features_check.run"""
import frappe
from frappe.utils import add_days, nowdate, getdate


def check(label, ok, extra=""):
    print(("FEAT OK   " if ok else "FEAT FAIL ") + label, extra)


def run():
    frappe.set_user("Administrator")
    from garage_management.api import messages, reminders
    # customer with a phone (via the customer form logic), vehicle expiring soon
    cust = frappe.get_doc({"doctype": "Customer", "customer_name": "Feature Test Customer", "customer_type": "Individual",
                           "garage_phone": "0551234567", "garage_email": "feat@example.com"}).insert()
    veh = frappe.get_doc({"doctype": "Garage Vehicle", "plate_number": "FEAT-" + frappe.generate_hash(length=3).upper(),
                          "customer": cust.name, "make": "Nissan", "model": "Patrol", "current_mileage": 90000,
                          "registration_expiry": add_days(nowdate(), 3), "insurance_expiry": add_days(nowdate(), 200)}).insert()
    job = frappe.get_doc({"doctype": "Repair Job", "customer": cust.name, "vehicle": veh.name, "mileage": 91000,
                          "services": [{"item_code": "AC Gas Refill", "qty": 1}]}).insert()
    url = messages.whatsapp_link("Repair Job", job.name, "ready")
    from urllib.parse import unquote
    text = unquote(url)
    check("whatsapp link has UAE number + message", url.startswith("https://wa.me/971551234567?text=") and "Nissan Patrol" in text and veh.plate_number in text, text[26:120])
    # completing the job sets the next service
    job.db_set("status", "Completed"); job.reload(); job.sync_vehicle()  # what saving a completed job does
    v = frappe.get_doc("Garage Vehicle", veh.name)
    check("next service date set after completion", v.next_service_date and getdate(v.next_service_date) > getdate(nowdate()), str(v.next_service_date))
    check("next service mileage = job mileage + interval", v.next_service_mileage == 91000 + (frappe.db.get_single_value("Garage Settings", "service_interval_km") or 5000), str(v.next_service_mileage))
    # reminders: registration in 3 days is due within 7; insurance in 200 days is not
    rows = reminders.due_rows(days=7, vehicle=veh.name)
    reasons = {r["reason"] for r in rows}
    check("registration expiry appears in reminders", "Registration expires" in reasons, str(reasons))
    check("far-away insurance expiry does not appear", "Insurance expires" not in reasons)
    before = frappe.db.count("Notification Log", {"document_name": "Vehicle Reminders"})
    u = "feat.recep@example.com"
    if frappe.db.exists("User", u):
        frappe.delete_doc("User", u, force=True)
    frappe.get_doc({"doctype": "User", "email": u, "first_name": "Feat", "send_welcome_email": 0, "role_profile_name": "Receptionist"}).insert(ignore_permissions=True)
    reminders.daily_vehicle_reminders()
    after = frappe.db.count("Notification Log", {"document_name": "Vehicle Reminders", "for_user": u})
    check("daily job notifies the receptionist", after >= 1, str(after))
    # cleanup everything created here
    frappe.db.rollback()
    print("FEAT done (changes rolled back)")
