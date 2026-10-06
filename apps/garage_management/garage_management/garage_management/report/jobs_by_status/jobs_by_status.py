import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    cond, vals = ["1=1"], {}
    if filters.get("from_date"):
        cond.append("job_date >= %(from_date)s"); vals["from_date"] = filters.from_date
    if filters.get("to_date"):
        cond.append("job_date <= %(to_date)s"); vals["to_date"] = filters.to_date
    rows = frappe.db.sql(f"""SELECT status, COUNT(*) AS jobs, SUM(estimated_total) AS estimated_total
        FROM `tabRepair Job` WHERE {' AND '.join(cond)} GROUP BY status ORDER BY jobs DESC""", vals, as_dict=True)
    cols = [{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 220},
            {"fieldname": "jobs", "label": "Jobs", "fieldtype": "Int", "width": 90},
            {"fieldname": "estimated_total", "label": "Estimated Value", "fieldtype": "Currency", "width": 140}]
    chart = {"data": {"labels": [r.status for r in rows], "datasets": [{"values": [r.jobs for r in rows]}]}, "type": "donut"}
    return cols, rows, None, chart
