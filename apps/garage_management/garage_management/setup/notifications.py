import frappe

BOSS = ["Garage Manager", "Garage Owner"]

# name, doctype, event, extra fields, condition, roles, message
NOTIFICATIONS = [
    ("Vehicle Checked In", "Vehicle Check-In", "New", {}, None, BOSS,
     "{{ doc.plate_number }} ({{ doc.customer_name }}) was checked in. Complaint: {{ doc.customer_complaint }}"),
    ("Quotation Waiting for Approval", "Repair Job", "Value Change", {"value_changed": "status"},
     "doc.status == 'Waiting for Customer Approval'", BOSS + ["Receptionist"],
     "Job {{ doc.name }} ({{ doc.plate_number }}) is waiting for the customer's approval."),
    ("Customer Approved Quotation", "Quotation", "Value Change", {"value_changed": "approval_status"},
     "doc.approval_status == 'Customer Approved'", BOSS + ["Receptionist", "Technician"],
     "{{ doc.party_name }} approved quotation {{ doc.name }} ({{ doc.plate_number }}). Repair can start."),
    ("Job Ready for Delivery", "Repair Job", "Value Change", {"value_changed": "status"},
     "doc.status == 'Ready for Delivery'", ["Receptionist"] + BOSS,
     "{{ doc.plate_number }} is ready for delivery to {{ doc.customer_name }}."),
    ("Repair Completed", "Repair Job", "Value Change", {"value_changed": "status"},
     "doc.status == 'Completed'", BOSS,
     "Job {{ doc.name }} ({{ doc.plate_number }}) was delivered and completed."),
    ("Invoice Outstanding", "Sales Invoice", "Days After", {"date_changed": "due_date", "days_in_advance": 1},
     "doc.outstanding_amount > 0 and doc.docstatus == 1", ["Accounts User", "Accounts Manager", "Garage Owner"],
     "Invoice {{ doc.name }} for {{ doc.customer_name }} is overdue. Outstanding: {{ doc.get_formatted('outstanding_amount') }}."),
]


def create():
    for name, dt, event, extra, cond, roles, message in NOTIFICATIONS:
        if frappe.db.exists("Notification", name):
            continue
        doc = frappe.new_doc("Notification")
        doc.update({"name": name, "subject": name + ": {{ doc.name }}", "document_type": dt, "event": event,
                    "channel": "System Notification", "enabled": 1, "condition": cond, "message": message,
                    "message_type": "Markdown", "module": "Garage Management", **extra})
        for r in roles:
            if frappe.db.exists("Role", r):
                doc.append("recipients", {"receiver_by_role": r})
        doc.insert(ignore_permissions=True)
