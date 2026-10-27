import frappe


def sync_contact(doc, method=None):
    """Keep the customer's phone/email (entered on the customer form) in a linked primary Contact,
    which is what ERPNext's search, emails and Customer 360 read."""
    phone, email = (doc.get("garage_phone") or "").strip(), (doc.get("garage_email") or "").strip()
    if not (phone or email):
        return
    contact = frappe.get_doc("Contact", doc.customer_primary_contact) if doc.customer_primary_contact and \
        frappe.db.exists("Contact", doc.customer_primary_contact) else None
    if not contact:
        contact = frappe.new_doc("Contact")
        contact.first_name = doc.customer_name
        contact.append("links", {"link_doctype": "Customer", "link_name": doc.name})
    if phone:
        contact.set("phone_nos", [{"phone": phone, "is_primary_mobile_no": 1}])
    if email:
        contact.set("email_ids", [{"email_id": email, "is_primary": 1}])
    contact.flags.ignore_permissions = True
    contact.save()
    values = {"customer_primary_contact": contact.name, "mobile_no": phone, "email_id": email}
    frappe.db.set_value("Customer", doc.name, values, update_modified=False)
    doc.update(values)  # so the form shows them straight away
    from frappe.utils.global_search import sync_global_search, update_global_search
    update_global_search(doc)  # the search index was built before the phone was filed
    sync_global_search()  # make it searchable now instead of at the next 15-minute flush


@frappe.whitelist()
def get_details(customer):
    """Everything about one customer on one screen: contact data, what each business has quoted/invoiced/received, what is still owed,
    and the latest documents (the 'Details' button on the Customers list)."""
    from frappe.utils import flt

    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw("You do not have permission to view this customer.", frappe.PermissionError)
    c = frappe.db.get_value("Customer", customer, ["name", "customer_name", "tax_id", "doc_address", "garage_phone", "garage_email"], as_dict=True)
    companies = []
    for co in frappe.get_all("Company", pluck="name"):
        invs = frappe.get_all("Sales Invoice", filters={"company": co, "customer": customer, "docstatus": 1, "is_return": 0}, fields=["grand_total", "outstanding_amount"])
        qts = frappe.get_all("Quotation", filters={"company": co, "party_name": customer, "docstatus": ["<", 2]}, fields=["grand_total"])
        inv = frappe._dict(n=len(invs), total=sum(flt(i.grand_total) for i in invs), owed=sum(flt(i.outstanding_amount) for i in invs))
        qt = frappe._dict(n=len(qts), total=sum(flt(q.grand_total) for q in qts))
        if not (inv.n or qt.n):
            continue
        companies.append({"company": co, "quotations": qt.n, "quoted": flt(qt.total), "invoices": inv.n, "invoiced": flt(inv.total),
                          "paid": flt(inv.total) - flt(inv.owed), "owes": flt(inv.owed)})
    recent = []
    for dt, party in (("Quotation", "party_name"), ("Sales Invoice", "customer")):
        for d in frappe.get_all(dt, filters={party: customer, "docstatus": ["<", 2]}, fields=["name", "company", "grand_total", "creation", "docstatus"], limit=6, order_by="creation desc"):
            recent.append({"doctype": dt, **d})
    recent.sort(key=lambda x: x["creation"], reverse=True)
    return {"customer": c, "companies": companies, "recent": [{**r, "creation": str(r["creation"])} for r in recent[:8]]}
