import frappe
from frappe.utils import flt, fmt_money, escape_html

from garage_management.garage_management.report.vehicle_service_history.vehicle_service_history import execute as history


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.customer:
        return [], []
    cust = frappe.get_doc("Customer", filters.customer)
    cur = frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "default_currency")
    columns, jobs = history({"customer": cust.name})

    totals = frappe.db.sql("""SELECT COUNT(*), COALESCE(SUM(base_grand_total), 0), COALESCE(SUM(outstanding_amount), 0), MAX(posting_date)
        FROM `tabSales Invoice` WHERE customer = %s AND docstatus = 1""", cust.name)[0]
    vehicles = frappe.get_all("Garage Vehicle", filters={"customer": cust.name},
                              fields=["name", "plate_number", "make", "model", "year", "current_mileage", "status"])
    last_visit = max((j.job_date for j in jobs if j.job_date), default=None)

    contact = " &nbsp;|&nbsp; ".join(x for x in [escape_html(cust.customer_name), escape_html(cust.mobile_no or ""),
                                              escape_html(cust.email_id or "")] if x)
    cars = "".join(f"<li><b>{escape_html(v.plate_number)}</b> &mdash; {escape_html(v.make)} {escape_html(v.model)} {v.year or ''} "
                   f"&middot; {v.current_mileage or 0} km &middot; {escape_html(v.status)}</li>" for v in vehicles) or "<li>No vehicles</li>"
    message = f"<div><b>{contact}</b></div><div style='margin-top:6px'>Vehicles ({len(vehicles)}):</div><ul>{cars}</ul>"

    summary = [
        {"label": "Vehicles", "value": len(vehicles), "datatype": "Int", "indicator": "blue"},
        {"label": "Repair Jobs", "value": len(jobs), "datatype": "Int", "indicator": "blue"},
        {"label": "Total Spent (incl. VAT)", "value": flt(totals[1]), "datatype": "Currency", "currency": cur, "indicator": "green"},
        {"label": "Still Owes", "value": flt(totals[2]), "datatype": "Currency", "currency": cur,
         "indicator": "red" if flt(totals[2]) else "green"},
        {"label": "Last Visit", "value": str(last_visit or "-"), "datatype": "Data", "indicator": "grey"},
    ]
    return columns, jobs, message, None, summary
