"""Staff with minimal roles must still be able to print the garage documents (they read Garage Settings)."""
import frappe


def run():
    frappe.set_user("Administrator")
    q = frappe.get_all("Quotation", pluck="name", limit=1, order_by="creation desc")[0]
    j = frappe.get_all("Repair Job", pluck="name", limit=1, order_by="creation desc")[0]
    for profile, dt, name, fmt in (("Receptionist", "Quotation", q, "Garage Quotation"), ("Technician", "Repair Job", j, "Garage Job Card")):
        email = f"print.{profile.lower()}@example.com"
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True)
        frappe.get_doc({"doctype": "User", "email": email, "first_name": profile, "send_welcome_email": 0, "role_profile_name": profile}).insert(ignore_permissions=True)
        frappe.set_user(email)
        try:
            if profile == "Technician":
                frappe.db.set_value("Repair Job", j, "technician", email)
            html = frappe.get_print(dt, name, print_format=fmt)
            print("PRT OK  ", profile, dt, "title+accent present:", "gm" in html)
        except Exception as e:
            print("PRT FAIL", profile, dt, type(e).__name__, str(e)[:120])
        frappe.set_user("Administrator")
        frappe.delete_doc("User", email, force=True)
    frappe.db.rollback()
