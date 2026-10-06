import frappe
from frappe.model.document import Document


class GarageVehicle(Document):
    def validate(self):
        self.plate_number = (self.plate_number or "").strip().upper()
        if self.vin:
            self.vin = self.vin.strip().upper()
