import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day, getdate, nowdate


class CustomerStatement(Document):
    def before_validate(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
        if not self.from_date:
            self.from_date = get_first_day(nowdate())
        if not self.to_date:
            self.to_date = get_last_day(nowdate())

    def validate(self):
        if getdate(self.from_date) > getdate(self.to_date):
            frappe.throw("'From' date must be before 'To' date.")
        self.load_lines()

    def load_lines(self):
        """Invoices of the period, plus older invoices of this customer that are still not fully paid (carried forward)."""
        rows = frappe.db.sql("""
            SELECT name, posting_date, grand_total, outstanding_amount, vehicle_no
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND is_return = 0 AND company = %(company)s AND customer = %(customer)s
              AND posting_date <= %(to)s AND (posting_date >= %(from)s OR outstanding_amount > 0.005)
            ORDER BY posting_date, creation""", {"company": self.company, "customer": self.customer,
                                                  "from": self.from_date, "to": self.to_date}, as_dict=True)
        self.set("lines", [])
        for r in rows:
            self.append("lines", {"invoice": r.name, "posting_date": r.posting_date, "vehicle_no": r.vehicle_no,
                                  "amount": r.grand_total, "balance": r.outstanding_amount})
        self.total_amount = sum(flt(r.amount) for r in self.lines)
        self.balance_due = sum(flt(r.balance) for r in self.lines)
        self.total_paid = self.total_amount - self.balance_due
