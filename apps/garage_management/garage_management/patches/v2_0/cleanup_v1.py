"""One-off: remove what version 1 (full garage workflow) created, so the simple version starts clean."""
import frappe

OLD_CUSTOM_FIELDS = ["garage_section", "vehicle", "plate_number", "garage_cb", "repair_job", "approval_section", "approval_status",
                     "approval_date", "approval_cb", "approved_by", "approved_amount", "customer_comments"]
OLD_PRINT_FORMATS = ["Garage Quotation", "Garage Tax Invoice", "Garage Job Card", "Garage Vehicle Inspection",
                     "Garage Vehicle Check-In", "Garage Payment Receipt"]
OLD_NOTIFICATIONS = ["Vehicle Checked In", "Quotation Waiting for Approval", "Customer Approved Quotation", "Job Ready for Delivery",
                     "Repair Completed", "Invoice Outstanding"]
OLD_CARDS = ["Today's Jobs", "Vehicles In Garage", "Waiting for Approval", "Jobs In Repair", "Ready for Delivery", "Today's Invoices",
             "Outstanding Payments", "Monthly Revenue", "Vehicles Serviced (Month)", "Pending Quotations", "Low Stock Parts"]
OLD_CHARTS = ["Jobs by Status", "Monthly Revenue (net)", "Daily Sales (30 days)"]


def _drop(doctype, name):
    if frappe.db.exists(doctype, name):
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True, ignore_missing=True)


def execute():
    _drop("Workflow", "Repair Job Workflow")
    for n in OLD_NOTIFICATIONS:
        _drop("Notification", n)
    for cf in frappe.get_all("Custom Field", filters={"dt": ["in", ["Quotation", "Sales Order", "Sales Invoice"]],
                                                      "fieldname": ["in", OLD_CUSTOM_FIELDS]}, pluck="name"):
        _drop("Custom Field", cf)
    for pf in OLD_PRINT_FORMATS:
        _drop("Print Format", pf)
    frappe.db.delete("Property Setter", {"property": "default_print_format", "doc_type": ["in", ["Quotation", "Sales Invoice", "Payment Entry"]]})
    for c in OLD_CARDS:
        _drop("Number Card", c)
    for c in OLD_CHARTS:
        _drop("Dashboard Chart", c)
    _drop("Workspace", "Garage")
    if frappe.db.exists("Sidebar", "Garage Management"):
        frappe.db.delete("Sidebar Item", {"parent": "Garage Management"})
        frappe.db.delete("Sidebar", {"name": "Garage Management"})
    for r in ("Vehicle Service History", "Jobs by Status", "Technician Performance", "Parts Used", "Services Performed",
              "Low Stock Parts", "Customer 360", "Vehicle Reminders"):
        _drop("Report", r)
    frappe.db.commit()
