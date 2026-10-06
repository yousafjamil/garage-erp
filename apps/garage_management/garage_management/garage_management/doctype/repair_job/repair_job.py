import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate

# Work cannot start (or finish) before the customer has approved the quotation.
APPROVAL_GATED = ("In Repair", "Quality Check", "Ready for Delivery", "Completed")

VEHICLE_STATUS = {
    "Ready for Delivery": "Ready for Delivery",
    "Completed": "Delivered",
    "Cancelled": "Active",
}


class RepairJob(Document):
    def validate(self):
        self.title = f"{self.customer_name or self.customer} - {self.plate_number or self.vehicle}"
        self.validate_vehicle_owner()
        self.fill_rows()
        self.calculate_totals()
        self.check_workflow_rules()
        if self.status == "Completed" and not self.actual_completion:
            self.actual_completion = nowdate()

    def on_update(self):
        self.sync_vehicle()

    def validate_vehicle_owner(self):
        owner, make, model = frappe.db.get_value("Garage Vehicle", self.vehicle, ["customer", "make", "model"])
        if owner != self.customer:
            frappe.throw(f"Vehicle {self.vehicle} belongs to {owner}, not {self.customer}.")
        self.vehicle_model = f"{make} {model}"

    def fill_rows(self):
        for row in self.services:
            item = frappe.db.get_value("Item", row.item_code, ["item_name", "description", "standard_rate"], as_dict=True)
            if not row.rate:
                row.rate = item.standard_rate
            if not row.description:
                row.description = item.item_name
        for row in self.parts:
            item = frappe.db.get_value("Item", row.item_code, ["standard_rate", "is_stock_item"], as_dict=True)
            if not row.rate:
                row.rate = item.standard_rate
            if not row.warehouse and item.is_stock_item:
                row.warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

    def calculate_totals(self):
        for row in self.services + self.parts:
            row.amount = flt(row.qty) * flt(row.rate)
        self.total_services = sum(flt(r.amount) for r in self.services)
        self.total_parts = sum(flt(r.amount) for r in self.parts)
        self.estimated_total = self.total_services + self.total_parts

    def check_workflow_rules(self):
        if self.override_approval:
            return
        if self.status == "Waiting for Customer Approval" and not self.quotation:
            frappe.throw("Create the quotation first (Create > Quotation) before sending the job for customer approval.")
        if self.status in APPROVAL_GATED:
            if not self.quotation or frappe.db.get_value("Quotation", self.quotation, "approval_status") != "Customer Approved":
                frappe.throw("The customer has not approved the quotation yet. Repair cannot start. "
                             "A Garage Manager/Owner can tick 'Override approval requirement'.")
        if self.status == "Completed" and not self.sales_invoice:
            frappe.throw("Create the invoice (Create > Invoice) before delivering the vehicle.")

    def sync_vehicle(self):
        updates = {}
        if self.mileage and self.mileage > (frappe.db.get_value("Garage Vehicle", self.vehicle, "current_mileage") or 0):
            updates["current_mileage"] = self.mileage
        if self.status == "Draft":
            pass
        elif self.status in VEHICLE_STATUS:
            updates["status"] = VEHICLE_STATUS[self.status]
        else:
            updates["status"] = "Under Repair"
        if updates:
            frappe.db.set_value("Garage Vehicle", self.vehicle, updates)
        if self.check_in and not frappe.db.get_value("Vehicle Check-In", self.check_in, "repair_job"):
            frappe.db.set_value("Vehicle Check-In", self.check_in, "repair_job", self.name, update_modified=False)


def get_permission_query_conditions(user=None):
    """Technicians only see the jobs assigned to them."""
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    if "Technician" in roles and not roles & {"Garage Owner", "Garage Manager", "Receptionist", "System Manager"}:
        return f"`tabRepair Job`.technician = {frappe.db.escape(user)}"


def has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    if "Technician" in roles and not roles & {"Garage Owner", "Garage Manager", "Receptionist", "System Manager"}:
        return doc.technician == user
    return True
