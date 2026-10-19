"""Server hooks for Quotation / Sales Invoice (shared by both businesses) and the Job Card shortcuts."""
import frappe
from frappe.utils import flt, nowdate

DEFAULT_ITEM = "Service"
SERIES = {
    "Garage": {"Quotation": "QTN-.####.-.YY.", "Sales Invoice": "INV-.####.-.YY."},
    "Transport": {"Quotation": "PQTN-.###.-.YY.", "Sales Invoice": "PINV-.###.-.YY."},
}


def company_style(company):
    return (frappe.db.get_value("Company", company, "print_style") if company else None) or "Garage"


def before_naming(doc, method=None):
    """Each business has its own numbering."""
    doc.naming_series = SERIES[company_style(doc.company)][doc.doctype]


def free_text_lines(doc, method=None):
    """Lines are typed as plain descriptions (no item catalogue): give them the generic Service item."""
    doc.disable_rounded_total = 1  # exact amounts to the fils, never rounded to whole dirhams
    for row in doc.items:
        if not row.item_code:
            row.item_code = DEFAULT_ITEM
            row.item_name = row.item_name or DEFAULT_ITEM


def invoice_defaults(doc, method=None):
    free_text_lines(doc)
    doc.update_stock = 0
    if not doc.taxes and not doc.taxes_and_charges:
        abbr = frappe.db.get_value("Company", doc.company, "abbr")
        template = f"UAE VAT 5% - {abbr}"
        if frappe.db.exists("Sales Taxes and Charges Template", template):
            from erpnext.controllers.accounts_controller import get_taxes_and_charges
            doc.taxes_and_charges = template
            doc.set("taxes", get_taxes_and_charges("Sales Taxes and Charges Template", template))


# ---- Job Card -> Quotation / Invoice ------------------------------------------------------------------------------

def _from_job(job, doctype):
    job = frappe.get_doc("Service Job Card", job)
    job.check_permission("write")
    if not job.lines:
        frappe.throw("Add the work and charges to the job card first.")
    link = "quotation" if doctype == "Quotation" else "sales_invoice"
    if job.get(link):
        frappe.throw(f"{doctype} {job.get(link)} already exists for this job card.")
    doc = frappe.new_doc(doctype)
    doc.company = job.company
    doc.customer = job.customer
    doc.vehicle_no = job.vehicle_no
    doc.job_card = job.name
    if doctype == "Quotation":
        doc.quotation_to = "Customer"; doc.party_name = job.customer; doc.transaction_date = nowdate(); doc.order_type = "Sales"
    else:
        doc.posting_date = nowdate(); doc.set_posting_time = 0
    for r in job.lines:
        doc.append("items", {"item_code": DEFAULT_ITEM, "description": r.description, "qty": r.qty, "rate": r.rate})
    doc.insert()
    job.db_set(link, doc.name)
    if doctype == "Sales Invoice":
        job.db_set("status", "Invoiced")
    return doc.name


@frappe.whitelist()
def make_quotation(job):
    return _from_job(job, "Quotation")


@frappe.whitelist()
def make_invoice(job):
    return _from_job(job, "Sales Invoice")
