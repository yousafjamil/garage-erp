"""Business details for Candle Auto Repair Workshop. Run once after the Setup Wizard:
    bench --site <site> execute garage_management.setup.company.apply"""
import frappe

NAME = "Candle Auto Repair Workshop"
EMAIL = "Candlearw@gmail.com"
PHONES = ["056-900 3156", "050-495 6602", "050-806 2151"]
ADDRESS = {"line1": "Musaffah M32-02", "city": "Abu Dhabi", "country": "United Arab Emirates"}
HEADER = '<img src="/assets/garage_management/images/letterhead-header.jpg" style="width:100%;display:block">'
FOOTER = '<img src="/assets/garage_management/images/letterhead-footer.jpg" style="width:100%;display:block">'


def apply():
    if not frappe.db.exists("Company", NAME):
        frappe.throw(f"Company '{NAME}' not found - run the Setup Wizard first.")
    if not frappe.db.exists("Address", f"{NAME}-Billing"):
        frappe.get_doc({"doctype": "Address", "address_title": NAME, "address_type": "Billing",
                        "address_line1": ADDRESS["line1"], "city": ADDRESS["city"], "country": ADDRESS["country"],
                        "email_id": EMAIL, "phone": PHONES[0], "is_your_company_address": 1,
                        "links": [{"link_doctype": "Company", "link_name": NAME}]}).insert(ignore_permissions=True)
    frappe.db.set_value("Letter Head", {"is_default": 1}, "is_default", 0)
    lh = frappe.get_doc("Letter Head", "Candle Auto Repair") if frappe.db.exists("Letter Head", "Candle Auto Repair") \
        else frappe.get_doc({"doctype": "Letter Head", "letter_head_name": "Candle Auto Repair"})
    lh.update({"source": "HTML", "content": HEADER, "footer_source": "HTML", "footer": FOOTER, "is_default": 1})
    lh.save(ignore_permissions=True)
    c = frappe.get_doc("Company", NAME)
    c.update({"email": EMAIL, "phone_no": PHONES[0], "default_letter_head": "Candle Auto Repair",
              "company_description": "ورشة كاندل لاصلاح السيارات - Candle Auto Repair Workshop"})
    c.save(ignore_permissions=True)
    frappe.db.commit()
    print("Company details applied. Remember to set the Tax ID (TRN) on the Company.")
