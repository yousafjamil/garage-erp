import frappe
from frappe.model.document import Document

ORDER = ["Good", "Attention Needed", "Repair Required", "Critical"]

DEFAULT_COMPONENTS = ["Engine", "Engine Oil", "Coolant", "Battery", "Brakes", "Tires", "Suspension",
                      "AC", "Lights", "Electrical", "Body", "Transmission", "Other"]


class VehicleInspection(Document):
    def validate(self):
        worst = max((ORDER.index(r.result) for r in self.items if r.result in ORDER), default=0)
        self.overall_result = ORDER[worst]

    def on_update(self):
        if self.repair_job and frappe.db.exists("Repair Job", self.repair_job):
            frappe.db.set_value("Repair Job", self.repair_job, "inspection", self.name, update_modified=False)
            if self.diagnosis and not frappe.db.get_value("Repair Job", self.repair_job, "diagnosis"):
                frappe.db.set_value("Repair Job", self.repair_job, "diagnosis", self.diagnosis, update_modified=False)


@frappe.whitelist()
def default_checklist():
    return DEFAULT_COMPONENTS
