import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ServiceJobCard(Document):
    def before_validate(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")

    def validate(self):
        for row in self.lines:
            row.amount = flt(row.qty) * flt(row.rate)
        self.total = sum(flt(r.amount) for r in self.lines)
