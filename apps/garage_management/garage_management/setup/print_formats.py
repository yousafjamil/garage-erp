import os
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "print_formats")

# print format name, doctype, template body. Each format switches between the two businesses' layouts (Company > Document Style).
FORMATS = [
    ("Quotation Print", "Quotation", "quotation.html"),
    ("Tax Invoice Print", "Sales Invoice", "invoice.html"),
    ("Job Card Print", "Service Job Card", "jobcard.html"),
    ("Statement Print", "Customer Statement", "statement.html"),
    ("Receipt Print", "Payment Entry", "receipt.html"),
]


def create():
    base = open(os.path.join(DIR, "_base.html")).read()
    tail = open(os.path.join(DIR, "_tail.html")).read()
    for name, doctype, fname in FORMATS:
        html = base + open(os.path.join(DIR, fname)).read() + tail
        doc = frappe.get_doc("Print Format", name) if frappe.db.exists("Print Format", name) else frappe.new_doc("Print Format")
        if doc.is_new():
            doc.name = name
        doc.update({"doc_type": doctype, "print_format_type": "Jinja", "custom_format": 1, "html": html, "standard": "No",
                    "disabled": 0, "margin_top": 8, "margin_bottom": 64, "margin_left": 0, "margin_right": 0,
                    "module": "Garage Management", "default_print_language": "en"})
        doc.save(ignore_permissions=True)
        make_property_setter(doctype, None, "default_print_format", name, "Data", for_doctype=True, validate_fields_for_doctype=False)
