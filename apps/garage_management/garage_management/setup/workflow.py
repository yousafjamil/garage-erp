import frappe

STATES = ["Draft", "Checked In", "Inspection", "Waiting for Quotation", "Waiting for Customer Approval",
          "Approved", "In Repair", "Quality Check", "Ready for Delivery", "Completed", "Cancelled"]

FRONT = ["Receptionist", "Garage Manager", "Garage Owner"]
WORK = ["Technician", "Garage Manager", "Garage Owner"]
BOSS = ["Garage Manager", "Garage Owner"]

TRANSITIONS = [
    ("Draft", "Check In", "Checked In", FRONT),
    ("Checked In", "Start Inspection", "Inspection", WORK + ["Receptionist"]),
    ("Inspection", "Inspection Done", "Waiting for Quotation", WORK),
    ("Waiting for Quotation", "Send for Approval", "Waiting for Customer Approval", FRONT),
    ("Waiting for Customer Approval", "Customer Approved", "Approved", FRONT),
    ("Waiting for Customer Approval", "Revise Quotation", "Waiting for Quotation", FRONT),
    ("Approved", "Start Repair", "In Repair", WORK),
    ("In Repair", "Send to Quality Check", "Quality Check", WORK),
    ("Quality Check", "Quality Passed", "Ready for Delivery", BOSS),
    ("Quality Check", "Needs Rework", "In Repair", BOSS),
    ("Ready for Delivery", "Deliver Vehicle", "Completed", FRONT),
] + [(s, "Cancel Job", "Cancelled", BOSS) for s in STATES[:8] if s != "Draft"] + [("Draft", "Cancel Job", "Cancelled", BOSS)]


def create():
    for s in STATES:
        if not frappe.db.exists("Workflow State", s):
            frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": s}).insert(ignore_permissions=True)
    for a in {t[1] for t in TRANSITIONS}:
        if not frappe.db.exists("Workflow Action Master", a):
            frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": a}).insert(ignore_permissions=True)
    name = "Repair Job Workflow"
    if frappe.db.exists("Workflow", name):
        return  # keep any edits made in the UI
    wf = frappe.new_doc("Workflow")
    wf.update({"workflow_name": name, "document_type": "Repair Job", "workflow_state_field": "status",
               "is_active": 1, "send_email_alert": 0})
    for s in STATES:
        wf.append("states", {"state": s, "doc_status": "0", "allow_edit": "All" if s not in ("Completed", "Cancelled") else "Garage Manager"})
    for state, action, nxt, roles in TRANSITIONS:
        for role in roles:
            wf.append("transitions", {"state": state, "action": action, "next_state": nxt, "allowed": role,
                                      "allow_self_approval": 1})
    wf.insert(ignore_permissions=True)
