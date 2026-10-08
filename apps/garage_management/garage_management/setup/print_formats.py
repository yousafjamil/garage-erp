import os
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "print_formats")

# (print format name, doctype, template file)
FORMATS = [
    ("Garage Quotation", "Quotation", "quotation.html"),
    ("Garage Tax Invoice", "Sales Invoice", "sales_invoice.html"),
    ("Garage Job Card", "Repair Job", "repair_job.html"),
    ("Garage Vehicle Inspection", "Vehicle Inspection", "vehicle_inspection.html"),
    ("Garage Vehicle Check-In", "Vehicle Check-In", "vehicle_check_in.html"),
    ("Garage Payment Receipt", "Payment Entry", "payment_receipt.html"),
]


def create():
    style = open(os.path.join(DIR, "_style.html")).read()
    tail = open(os.path.join(DIR, "_tail.html")).read()
    for name, doctype, fname in FORMATS:
        html = style + open(os.path.join(DIR, fname)).read() + tail
        if frappe.db.exists("Print Format", name):
            doc = frappe.get_doc("Print Format", name)
        else:
            doc = frappe.new_doc("Print Format")
            doc.name = name
        doc.update({"doc_type": doctype, "print_format_type": "Jinja", "custom_format": 1, "html": html,
                    "standard": "No", "disabled": 0, "margin_top": 10, "margin_bottom": 34, "margin_left": 0, "margin_right": 0, "module": "Garage Management", "default_print_language": "en"})
        doc.save(ignore_permissions=True)
        make_property_setter(doctype, None, "default_print_format", name, "Data", for_doctype=True)
