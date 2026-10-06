import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    cond, vals = ["rj.status != 'Cancelled'"], {}
    for f, col in (("vehicle", "rj.vehicle"), ("customer", "rj.customer")):
        if filters.get(f):
            cond.append(f"{col} = %({f})s"); vals[f] = filters[f]
    if filters.get("plate_number"):
        cond.append("rj.plate_number LIKE %(plate)s"); vals["plate"] = f"%{filters.plate_number.strip().upper()}%"
    if filters.get("from_date"):
        cond.append("rj.job_date >= %(from_date)s"); vals["from_date"] = filters.from_date
    if filters.get("to_date"):
        cond.append("rj.job_date <= %(to_date)s"); vals["to_date"] = filters.to_date
    rows = frappe.db.sql(f"""
        SELECT rj.job_date, rj.name AS repair_job, rj.vehicle, rj.plate_number, rj.mileage, rj.status,
               rj.customer_complaint AS complaint, rj.diagnosis, rj.technician,
               (SELECT GROUP_CONCAT(CONCAT(s.item_code, ' x', s.qty) SEPARATOR ', ') FROM `tabRepair Job Service` s WHERE s.parent = rj.name) AS services,
               (SELECT GROUP_CONCAT(CONCAT(p.item_code, ' x', p.qty) SEPARATOR ', ') FROM `tabRepair Job Part` p WHERE p.parent = rj.name) AS parts,
               rj.sales_invoice, si.grand_total, si.grand_total - si.outstanding_amount AS paid, si.outstanding_amount
        FROM `tabRepair Job` rj
        LEFT JOIN `tabSales Invoice` si ON si.name = rj.sales_invoice AND si.docstatus = 1
        WHERE {' AND '.join(cond)}
        ORDER BY rj.job_date DESC, rj.creation DESC""", vals, as_dict=True)
    return get_columns(), rows


def get_columns():
    return [
        {"fieldname": "job_date", "label": "Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "repair_job", "label": "Job", "fieldtype": "Link", "options": "Repair Job", "width": 130},
        {"fieldname": "vehicle", "label": "Vehicle", "fieldtype": "Link", "options": "Garage Vehicle", "width": 110},
        {"fieldname": "plate_number", "label": "Plate", "fieldtype": "Data", "width": 90},
        {"fieldname": "mileage", "label": "Mileage", "fieldtype": "Int", "width": 90},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "complaint", "label": "Customer Complaint", "fieldtype": "Data", "width": 200},
        {"fieldname": "diagnosis", "label": "Diagnosis", "fieldtype": "Data", "width": 200},
        {"fieldname": "services", "label": "Services", "fieldtype": "Data", "width": 220},
        {"fieldname": "parts", "label": "Parts Replaced", "fieldtype": "Data", "width": 220},
        {"fieldname": "technician", "label": "Technician", "fieldtype": "Link", "options": "User", "width": 140},
        {"fieldname": "sales_invoice", "label": "Invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
        {"fieldname": "grand_total", "label": "Invoice Total", "fieldtype": "Currency", "width": 110},
        {"fieldname": "paid", "label": "Paid", "fieldtype": "Currency", "width": 100},
        {"fieldname": "outstanding_amount", "label": "Outstanding", "fieldtype": "Currency", "width": 110},
    ]
