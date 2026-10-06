import frappe
from frappe.model.document import Document


class VehicleCheckIn(Document):
    def validate(self):
        owner = frappe.db.get_value("Garage Vehicle", self.vehicle, "customer")
        if owner and owner != self.customer:
            frappe.throw(f"Vehicle {self.vehicle} belongs to {owner}, not {self.customer}.")

    def on_update(self):
        # keep the vehicle's odometer current
        current = frappe.db.get_value("Garage Vehicle", self.vehicle, "current_mileage") or 0
        if self.mileage and self.mileage > current:
            frappe.db.set_value("Garage Vehicle", self.vehicle, "current_mileage", self.mileage)
