"""Fewer columns and filters on the lists staff use every day (nothing is deleted, only de-cluttered)."""
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# (doctype, fieldname, property, value): 0/1 switches for list columns and quick filters
CHANGES = [
    # Quotation list: customer, plate, date, total, approval - no company / order type clutter
    ("Quotation", "company", "in_list_view", 0), ("Quotation", "order_type", "in_standard_filter", 0),
    ("Quotation", "quotation_to", "in_standard_filter", 0), ("Quotation", "party_name", "in_standard_filter", 0),
    ("Quotation", "party_name", "in_list_view", 0), ("Quotation", "order_type", "in_list_view", 0),
    # Sales Invoice list
    ("Sales Invoice", "company", "in_list_view", 0), ("Sales Invoice", "company", "in_standard_filter", 0),
    ("Sales Invoice", "customer", "in_standard_filter", 0),
    # Payment Entry list
    ("Payment Entry", "company", "in_list_view", 0), ("Payment Entry", "company", "in_standard_filter", 0),
]


def apply():
    for dt, field, prop, value in CHANGES:
        if frappe.get_meta(dt).has_field(field):
            make_property_setter(dt, field, prop, str(value), "Check", validate_fields_for_doctype=False)
    for dt, field in (("Quotation", "plate_number"), ("Quotation", "approval_status"), ("Sales Invoice", "plate_number")):
        pass  # list visibility of our own custom fields is set in setup/custom_fields.py


def set_defaults():
    """Fields hidden on the lean forms still need sensible values."""
    for field, value in (("customer_group", "Individual"), ("territory", "All Territories")):
        if frappe.get_meta("Selling Settings").has_field(field) and frappe.db.exists(
                "Customer Group" if field == "customer_group" else "Territory", value):
            frappe.db.set_single_value("Selling Settings", field, value)
