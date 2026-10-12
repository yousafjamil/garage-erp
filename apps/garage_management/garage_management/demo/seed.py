"""Sample garage data for the free-tier demo image (not used in production):
    bench --site <site> execute garage_management.demo.seed.load
Creates priced services/parts with stock, three customers with phones, four cars and four jobs at different stages,
plus demo logins (password: Garage@Demo2026)."""
import frappe
from frappe.model.workflow import apply_workflow
from frappe.utils import add_days, nowdate

PASSWORD = "Garage@Demo2026"
PRICES = {"Engine Oil Change": 120, "Brake Service": 250, "AC Service": 180, "Diagnostic": 80, "General Inspection": 60,
          "Wheel Alignment": 100, "Brake Pads": 180, "Oil Filter": 35, "Engine Oil": 90, "Air Filter": 45, "Battery": 380,
          "AC Compressor": 600, "AC Gas Refill": 150}
STOCK = {"Brake Pads": 12, "Oil Filter": 20, "Engine Oil": 30, "Air Filter": 15, "Battery": 6, "AC Compressor": 4}


def _company():
    return frappe.defaults.get_global_default("company")


def _prices():
    from garage_management.setup.install import _make_item
    co = _company(); abbr = frappe.db.get_value("Company", co, "abbr"); tax = f"UAE VAT 5% - {abbr}"
    for name, rate in PRICES.items():
        if not frappe.db.exists("Item", name):
            _make_item(name, "Spare Parts" if name in STOCK or name == "AC Compressor" else "Services", name in STOCK, tax, co, abbr)
        frappe.db.set_value("Item", name, "standard_rate", rate)
    wh = f"Stores - {abbr}"
    items = [{"item_code": k, "qty": q, "basic_rate": PRICES[k] * 0.6, "t_warehouse": wh} for k, q in STOCK.items()]
    se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": co, "items": items})
    se.insert(); se.submit()


def _customer(name, phone):
    return frappe.get_doc({"doctype": "Customer", "customer_name": name, "customer_type": "Individual",
                           "garage_phone": phone, "garage_email": name.split()[0].lower() + "@example.com"}).insert()


def _vehicle(cust, plate, make, model, year, km):
    return frappe.get_doc({"doctype": "Garage Vehicle", "plate_number": plate, "customer": cust, "make": make, "model": model,
                           "year": year, "current_mileage": km, "fuel_type": "Petrol", "transmission": "Automatic",
                           "registration_expiry": add_days(nowdate(), 20)}).insert()


def _job(cust, veh, complaint, km, services, parts, technician="technician.demo@example.com"):
    ci = frappe.get_doc({"doctype": "Vehicle Check-In", "customer": cust, "vehicle": veh, "mileage": km, "fuel_level": "1/2",
                         "customer_complaint": complaint, "keys_received": 1}).insert()
    job = frappe.get_doc({"doctype": "Repair Job", "customer": cust, "vehicle": veh, "check_in": ci.name, "mileage": km,
                          "customer_complaint": complaint, "technician": technician,
                          "services": [{"item_code": s, "qty": 1} for s in services],
                          "parts": [{"item_code": p, "qty": 1} for p in parts]}).insert()
    return job


def _step(job, *actions):
    for a in actions:
        job = apply_workflow(job, a)
    return job


def load():
    from garage_management.api import payments, repair_job as rj
    frappe.set_user("Administrator")
    for email, first, profile in (("reception.demo@example.com", "Reception", "Receptionist"),
                                  ("technician.demo@example.com", "Technician", "Technician"),
                                  ("manager.demo@example.com", "Manager", "Garage Manager")):
        if not frappe.db.exists("User", email):
            frappe.get_doc({"doctype": "User", "email": email, "first_name": first, "last_name": "Demo", "send_welcome_email": 0,
                            "role_profile_name": profile, "new_password": PASSWORD}).insert(ignore_permissions=True)
    _prices()
    ahmed = _customer("Ahmed Al Mansoori", "0501234567")
    fatima = _customer("Fatima Hassan", "0559876543")
    khalid = _customer("Khalid Al Nuaimi", "0524561234")
    corolla = _vehicle(ahmed.name, "A 12345", "Toyota", "Corolla", 2019, 84200)
    cruiser = _vehicle(ahmed.name, "B 77821", "Toyota", "Land Cruiser", 2021, 41000)
    patrol = _vehicle(fatima.name, "D 40418", "Nissan", "Patrol", 2018, 126500)
    tucson = _vehicle(khalid.name, "C 90356", "Hyundai", "Tucson", 2020, 67800)

    # 1) finished and paid
    j1 = _job(ahmed.name, corolla.name, "Oil change and general check", 84200, ["Engine Oil Change", "General Inspection"], ["Oil Filter", "Engine Oil"])
    j1 = _step(j1, "Start Inspection", "Inspection Done")
    q = rj.make_quotation(j1.name); rj.submit_quotation(j1.name); rj.record_approval(q, "Customer Approved", "Ahmed Al Mansoori", "OK")
    j1.reload(); j1 = _step(j1, "Start Repair", "Send to Quality Check", "Quality Passed")
    inv = rj.make_invoice(j1.name); rj.submit_invoice(j1.name)
    payments.receive_payment(inv, frappe.db.get_value("Sales Invoice", inv, "outstanding_amount"), "Card", "SLIP-1001")
    j1.reload(); _step(j1, "Deliver Vehicle")

    # 2) in repair (approved)
    j2 = _job(fatima.name, patrol.name, "Brakes squeal and vibrate when stopping", 126500, ["Brake Service", "Diagnostic"], ["Brake Pads"])
    j2 = _step(j2, "Start Inspection", "Inspection Done")
    q = rj.make_quotation(j2.name); rj.submit_quotation(j2.name); rj.record_approval(q, "Customer Approved", "Fatima Hassan", "Please go ahead")
    j2.reload(); _step(j2, "Start Repair")

    # 3) waiting for the customer's decision
    j3 = _job(khalid.name, tucson.name, "AC is not cooling", 67800, ["AC Service", "AC Gas Refill"], ["AC Compressor"])
    j3 = _step(j3, "Start Inspection", "Inspection Done")
    rj.make_quotation(j3.name); rj.submit_quotation(j3.name)

    # 4) just checked in
    _job(ahmed.name, cruiser.name, "Warning light on the dashboard", 41000, [], [])
    frappe.db.commit()
    print("DEMO loaded:", frappe.db.count("Repair Job"), "jobs,", frappe.db.count("Customer"), "customers")
