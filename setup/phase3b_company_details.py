import frappe
c = frappe.get_doc("Company", "Candle Auto Repair Workshop")
c.email = "Candlearw@gmail.com"
c.phone_no = "056-900 3156"
c.company_description = "ورشة كاندل لاصلاح السيارات - Candle Auto Repair Workshop"
c.default_letter_head = "Candle Auto Repair"
c.save()
frappe.db.commit()
print("DONE", c.email, c.phone_no, c.default_letter_head, frappe.get_all("Letter Head", fields=["name","is_default"]))
