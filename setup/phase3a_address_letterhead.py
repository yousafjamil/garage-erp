import frappe
c = frappe.get_doc("Company", "Candle Auto Repair Workshop")
c.email = "Candlearw@gmail.com"
c.phone_no = "056-900 3156 / 050-495 6602 / 050-806 2151"
c.company_description = "ورشة كاندل لاصلاح السيارات - Candle Auto Repair Workshop"
c.save()
if not frappe.db.exists("Address", "Candle Auto Repair Workshop-Billing"):
    a = frappe.get_doc({"doctype":"Address","address_title":"Candle Auto Repair Workshop","address_type":"Billing","address_line1":"Musaffah M32-02","city":"Abu Dhabi","country":"United Arab Emirates","email_id":"Candlearw@gmail.com","phone":"056-900 3156","is_your_company_address":1,"links":[{"link_doctype":"Company","link_name":"Candle Auto Repair Workshop"}]})
    a.insert()
head = '<div style="text-align:center"><div style="font-size:20px;font-weight:bold">Candle Auto Repair Workshop</div><div style="font-size:18px;direction:rtl">ورشة كاندل لاصلاح السيارات</div></div>'
foot = '<div style="text-align:center;font-size:11px">Candlearw@gmail.com<br>056-900 3156 &nbsp; 050-495 6602 &nbsp; 050-806 2151<br>Musaffah M32-02 Abu Dhabi UAE</div>'
frappe.db.set_value("Letter Head", {"is_default":1}, "is_default", 0)
if frappe.db.exists("Letter Head", "Candle Auto Repair"):
    lh = frappe.get_doc("Letter Head", "Candle Auto Repair")
else:
    lh = frappe.new_doc("Letter Head"); lh.letter_head_name = "Candle Auto Repair"
lh.source = "HTML"; lh.content = head; lh.footer_source = "HTML"; lh.footer = foot; lh.is_default = 1
lh.save()
c.reload(); c.default_letter_head = "Candle Auto Repair"; c.save()
frappe.db.commit()
print("DONE", c.email, c.phone_no, c.default_letter_head, frappe.get_all("Address", filters={"address_title":"Candle Auto Repair Workshop"}, pluck="name"))
