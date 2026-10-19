import frappe
from frappe.utils import flt, nowdate

MODES = ("Cash", "Card", "Bank Transfer", "Cheque", "Other")


def outstanding_invoices(company, customer, invoice=None):
    filters = {"company": company, "customer": customer, "docstatus": 1, "is_return": 0, "outstanding_amount": [">", 0.005]}
    if invoice:
        filters["name"] = invoice
    return frappe.get_all("Sales Invoice", filters=filters,
                          fields=["name", "posting_date", "grand_total", "outstanding_amount"], order_by="posting_date asc, creation asc")


@frappe.whitelist()
def get_due(company, customer, invoice=None):
    return sum(flt(i.outstanding_amount) for i in outstanding_invoices(company, customer, invoice))


@frappe.whitelist()
def receive_customer_payment(company, customer, amount, mode_of_payment, reference_no=None, posting_date=None, invoice=None):
    """One payment from a customer, applied to their oldest unpaid invoices first (partial payments are fine)."""
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw("You do not have permission to record payments.", frappe.PermissionError)
    amount = flt(amount)
    if amount <= 0:
        frappe.throw("Enter an amount greater than zero.")
    if mode_of_payment not in MODES:
        frappe.throw("Choose Cash, Card, Bank Transfer, Cheque or Other.")
    invoices = outstanding_invoices(company, customer, invoice)
    due = sum(flt(i.outstanding_amount) for i in invoices)
    if not invoices:
        frappe.throw("This customer has no unpaid invoices.")
    if amount > due + 0.005:
        frappe.throw(f"The amount is more than what the customer owes ({due:,.2f}).")
    pe = get_payment_entry("Sales Invoice", invoices[0].name)
    pe.posting_date = posting_date or nowdate()
    pe.mode_of_payment = mode_of_payment
    pe.reference_no = reference_no or f"{mode_of_payment} {pe.posting_date}"
    pe.reference_date = pe.posting_date
    pe.paid_amount = pe.received_amount = amount
    pe.set("references", [])
    left, allocated = amount, []
    for inv in invoices:
        if left <= 0.004:
            break
        part = min(left, flt(inv.outstanding_amount))
        pe.append("references", {"reference_doctype": "Sales Invoice", "reference_name": inv.name, "total_amount": inv.grand_total,
                                 "outstanding_amount": inv.outstanding_amount, "allocated_amount": part})
        left -= part
        allocated.append({"invoice": inv.name, "paid": part})
    pe.setup_party_account_field()
    pe.set_missing_values()
    pe.insert()
    pe.submit()
    return {"payment_entry": pe.name, "allocated": allocated, "balance_due": due - amount}
