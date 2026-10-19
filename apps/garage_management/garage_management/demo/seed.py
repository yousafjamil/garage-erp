"""Sample data for the free-tier demo image (never for production):
    bench --site <site> execute garage_management.demo.seed.load
One customer with the documents of BOTH businesses, a monthly statement and a part-payment, plus demo logins (password below)."""
import frappe
from garage_management.tests.simple_scenario import GARAGE, TRANSPORT, _doc

PASSWORD = "Garage@Demo2026"
CUSTOMER = "Emirates LandScape Sole Proprietorship LLC"
GARAGE_JOBS = [(703.50, "27964 - Pickup", "2026-07-31"), (420, "85824 - Pickup", "2026-08-01"), (8557.50, "76191 - Pickup", "2026-08-08"),
               (1050, "Club Car", "2026-08-08"), (1218, "85863 - Pickup", "2026-08-19"), (2814, "24658 - Pickup", "2026-08-20")]


def load():
    from garage_management.api import payments
    frappe.set_user("Administrator")
    for email, first, profile in (("reception.demo@example.com", "Reception", "Receptionist"), ("manager.demo@example.com", "Manager", "Garage Manager")):
        if not frappe.db.exists("User", email):
            frappe.get_doc({"doctype": "User", "email": email, "first_name": first, "last_name": "Demo", "send_welcome_email": 0,
                            "role_profile_name": profile, "new_password": PASSWORD}).insert(ignore_permissions=True)
    if frappe.db.exists("Customer", {"customer_name": CUSTOMER}):
        return
    cust = frappe.get_doc({"doctype": "Customer", "customer_name": CUSTOMER, "customer_type": "Company", "tax_id": "100041562800003", "doc_address": "Abu Dhabi UAE",
                           "garage_phone": "0501112222", "garage_email": "accounts@emirateslandscape.example.com"}).insert().name
    for grand, veh, date in GARAGE_JOBS:
        _doc("Sales Invoice", GARAGE, cust, [("Mechanical work and spare parts", round(grand / 1.05, 2))], vehicle_no=veh, date=date).submit()
    _doc("Quotation", GARAGE, cust, [("Mechanical Work ( Labor Charges )", 250), ("Change Engine Belts", 150), ("Change Bearing", 165), ("Recovery Charges", 150)],
         vehicle_no="96228-Nissan Navara Pickup", date="2026-09-02")
    _doc("Sales Invoice", TRANSPORT, cust, [("Recovery Services Charges From Al Wathba To Al Khatam", 780)], date="2026-08-31", lpo="LPO-4471").submit()
    _doc("Quotation", TRANSPORT, cust, [("Transportation Charges Of Flatbed Trailer From Musaffah To Sadiyat", 1200)], date="2026-06-11")
    jc = frappe.get_doc({"doctype": "Service Job Card", "company": GARAGE, "customer": cust, "vehicle_no": "24658 - Pickup", "staff": "Ali",
                         "details": "Engine overheating, check radiator and hoses", "lines": [{"description": "Radiator repair", "qty": 1, "rate": 400}]}).insert()
    payments.receive_customer_payment(GARAGE, cust, 5000, "Bank Transfer", "TRF-DEMO-1", "2026-09-05")
    frappe.get_doc({"doctype": "Customer Statement", "company": GARAGE, "customer": cust, "from_date": "2026-07-01", "to_date": "2026-08-31"}).insert()
    frappe.db.commit()
