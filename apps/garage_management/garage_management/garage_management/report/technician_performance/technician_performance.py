import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    cond, vals = ["rj.status != 'Cancelled'", "rj.technician IS NOT NULL"], {}
    if filters.get("from_date"):
        cond.append("rj.job_date >= %(from_date)s"); vals["from_date"] = filters.from_date
    if filters.get("to_date"):
        cond.append("rj.job_date <= %(to_date)s"); vals["to_date"] = filters.to_date
    rows = frappe.db.sql(f"""
        SELECT rj.technician, COUNT(*) AS jobs, SUM(rj.status = 'Completed') AS completed,
               SUM(rj.status NOT IN ('Completed')) AS open_jobs,
               COALESCE(SUM(si.net_total), 0) AS revenue,
               (SELECT COALESCE(SUM(s.labor_hours), 0) FROM `tabRepair Job Service` s JOIN `tabRepair Job` j2 ON j2.name = s.parent
                  WHERE j2.technician = rj.technician AND j2.status != 'Cancelled') AS labor_hours
        FROM `tabRepair Job` rj LEFT JOIN `tabSales Invoice` si ON si.name = rj.sales_invoice AND si.docstatus = 1
        WHERE {' AND '.join(cond)} GROUP BY rj.technician ORDER BY revenue DESC""", vals, as_dict=True)
    cols = [{"fieldname": "technician", "label": "Technician", "fieldtype": "Link", "options": "User", "width": 200},
            {"fieldname": "jobs", "label": "Jobs", "fieldtype": "Int", "width": 80},
            {"fieldname": "completed", "label": "Completed", "fieldtype": "Int", "width": 100},
            {"fieldname": "open_jobs", "label": "Open", "fieldtype": "Int", "width": 80},
            {"fieldname": "labor_hours", "label": "Labor Hours", "fieldtype": "Float", "width": 110},
            {"fieldname": "revenue", "label": "Revenue (net of VAT)", "fieldtype": "Currency", "width": 160}]
    return cols, rows
