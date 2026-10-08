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
