import frappe
from frappe.utils import flt, nowdate

MODES = ("Cash", "Card", "Bank Transfer", "Other")


@frappe.whitelist()
def receive_payment(invoice, amount, mode_of_payment, reference_no=None):
    """One-step payment: creates and submits the Payment Entry for a submitted Sales Invoice (partial payments allowed)."""
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

    inv = frappe.get_doc("Sales Invoice", invoice)
    if inv.docstatus != 1:
        frappe.throw("Submit the invoice before receiving payment.")
    if mode_of_payment not in MODES:
        frappe.throw("Choose Cash, Card, Bank Transfer or Other.")
    amount = flt(amount)
    if amount <= 0:
        frappe.throw("Enter an amount greater than zero.")
    if amount > flt(inv.outstanding_amount) + 0.005:
        frappe.throw(f"The amount is more than the outstanding balance ({inv.outstanding_amount}).")
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw("You do not have permission to record payments.", frappe.PermissionError)
    pe = get_payment_entry("Sales Invoice", invoice)
    pe.mode_of_payment = mode_of_payment
    pe.paid_amount = pe.received_amount = amount
    pe.reference_no = reference_no or f"{mode_of_payment} {nowdate()}"
    pe.reference_date = nowdate()
    for ref in pe.references:
        ref.allocated_amount = amount
    pe.setup_party_account_field()
    pe.set_missing_values()
    pe.insert()
    pe.submit()
    return {"payment_entry": pe.name, "outstanding": frappe.db.get_value("Sales Invoice", invoice, "outstanding_amount")}
