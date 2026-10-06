import frappe
from frappe.utils import add_days, nowdate, flt


def _job(name):
    job = frappe.get_doc("Repair Job", name)
    job.check_permission("write")
    return job


@frappe.whitelist()
def make_quotation(job):
    """Build a Quotation from the job's services, labor and parts."""
    job = _job(job)
    if job.quotation:
        frappe.throw(f"Quotation {job.quotation} already exists for this job.")
    if not (job.services or job.parts):
        frappe.throw("Add at least one service or part before creating a quotation.")
    q = frappe.new_doc("Quotation")
    q.update({
        "quotation_to": "Customer", "party_name": job.customer, "transaction_date": nowdate(),
        "valid_till": add_days(nowdate(), 15), "vehicle": job.vehicle, "repair_job": job.name,
        "order_type": "Sales",
    })
    for r in job.services:
        q.append("items", {"item_code": r.item_code, "description": r.description, "qty": r.qty, "rate": r.rate})
    for r in job.parts:
        q.append("items", {"item_code": r.item_code, "qty": r.qty, "rate": r.rate, "warehouse": r.warehouse})
    q.run_method("set_missing_values")
    q.insert()
    job.db_set("quotation", q.name)
    return q.name


@frappe.whitelist()
def record_approval(quotation, decision, approved_by=None, comments=None):
    """Record the customer's decision on a submitted quotation and move the linked job on."""
    if decision not in ("Customer Approved", "Customer Rejected"):
        frappe.throw("Invalid decision")
    q = frappe.get_doc("Quotation", quotation)
    q.check_permission("write")
    if q.docstatus != 1:
        frappe.throw("Submit (send) the quotation before recording the customer's decision.")
    if decision == "Customer Approved" and not approved_by:
        frappe.throw("Enter who approved the quotation.")
    q.db_set({
        "approval_status": decision, "approval_date": nowdate(), "approved_by": approved_by,
        "approved_amount": q.grand_total if decision == "Customer Approved" else 0,
        "customer_comments": comments,
    })
    q.add_comment("Info", f"{decision} by {approved_by or 'customer'}. {comments or ''}")
    if q.get("repair_job"):
        job = frappe.get_doc("Repair Job", q.repair_job)
        if decision == "Customer Approved":
            if job.status in ("Waiting for Quotation", "Waiting for Customer Approval", "Inspection", "Checked In", "Draft"):
                job.db_set("status", "Approved")
        else:
            job.db_set({"status": "Waiting for Quotation", "quotation": None})
    return decision


@frappe.whitelist()
def make_invoice(job):
    """Quotation -> Sales Order -> Sales Invoice (stock is reduced by the invoice)."""
    from erpnext.selling.doctype.quotation.quotation import make_sales_order
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

    job = _job(job)
    if job.sales_invoice:
        frappe.throw(f"Invoice {job.sales_invoice} already exists for this job.")
    q = frappe.get_doc("Quotation", job.quotation) if job.quotation else None
    if not q or (q.approval_status != "Customer Approved" and not job.override_approval):
        frappe.throw("The quotation must be approved by the customer before invoicing.")
    so = make_sales_order(q.name)
    so.delivery_date = nowdate()
    so.update({"vehicle": job.vehicle, "repair_job": job.name})
    so.insert()
    so.submit()
    si = make_sales_invoice(so.name)
    si.update_stock = 1
    si.update({"vehicle": job.vehicle, "repair_job": job.name})
    si.insert()
    job.db_set({"sales_order": so.name, "sales_invoice": si.name})
    return si.name
