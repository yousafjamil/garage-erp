"""Fewer columns/filters, free-text lines, hidden modules - nothing is deleted, only kept out of the way."""
import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

HIDE_WORKSPACES = ["Manufacturing", "Projects", "Assets", "Quality", "Support", "CRM", "Website", "Subcontracting", "Payroll", "HR",
                   "Home", "ERPNext Settings", "Build", "Integrations", "Stock", "Buying", "Taxes", "Banking"]

# (doctype, fieldname, property, value)
CHANGES = [
    # lines are plain descriptions: no item code / unit of measure / stock columns
    *[(dt, "item_code", p, v) for dt in ("Quotation Item", "Sales Invoice Item") for p, v in (("in_list_view", 0), ("reqd", 0))],
    *[(dt, "description", "in_list_view", 1) for dt in ("Quotation Item", "Sales Invoice Item")],
    *[(dt, f, "in_list_view", 0) for dt in ("Quotation Item", "Sales Invoice Item") for f in ("item_name", "uom", "warehouse")],
    # lists
    ("Quotation", "company", "in_list_view", 1), ("Quotation", "order_type", "in_standard_filter", 0),
    ("Quotation", "quotation_to", "in_standard_filter", 0), ("Quotation", "party_name", "in_standard_filter", 0),
    ("Quotation", "order_type", "in_list_view", 0),
    ("Sales Invoice", "company", "in_list_view", 1), ("Sales Invoice", "customer", "in_standard_filter", 0),
    ("Payment Entry", "company", "in_list_view", 1),
]


def apply():
    for dt, field, prop, value in CHANGES:
        if frappe.get_meta(dt).has_field(field):
            make_property_setter(dt, field, prop, str(value), "Check", validate_fields_for_doctype=False)
    for field, value in (("customer_group", "Individual"), ("territory", "All Territories")):
        if frappe.db.exists("Customer Group" if field == "customer_group" else "Territory", value):
            frappe.db.set_single_value("Selling Settings", field, value)
    # default sales price list is not needed for free-text lines
    for name in HIDE_WORKSPACES:
        if frappe.db.exists("Workspace", name):
            frappe.db.set_value("Workspace", name, "is_hidden", 1)
        if frappe.db.exists("Desktop Icon", name):
            frappe.db.set_value("Desktop Icon", name, "hidden", 1)
