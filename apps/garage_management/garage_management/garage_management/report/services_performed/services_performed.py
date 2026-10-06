import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    cond, vals = ["rj.status != 'Cancelled'"], {}
    if filters.get("from_date"):
        cond.append("rj.job_date >= %(from_date)s"); vals["from_date"] = filters.from_date
    if filters.get("to_date"):
        cond.append("rj.job_date <= %(to_date)s"); vals["to_date"] = filters.to_date
    rows = frappe.db.sql(f"""
        SELECT s.item_code, s.item_name, SUM(s.qty) AS times, COUNT(DISTINCT rj.name) AS jobs,
               SUM(s.labor_hours) AS labor_hours, SUM(s.amount) AS revenue
        FROM `tabRepair Job Service` s JOIN `tabRepair Job` rj ON rj.name = s.parent
        WHERE {' AND '.join(cond)} GROUP BY s.item_code, s.item_name ORDER BY times DESC""", vals, as_dict=True)
    cols = [{"fieldname": "item_code", "label": "Service", "fieldtype": "Link", "options": "Item", "width": 180},
            {"fieldname": "item_name", "label": "Name", "fieldtype": "Data", "width": 200},
            {"fieldname": "times", "label": "Times Performed", "fieldtype": "Float", "width": 120},
            {"fieldname": "jobs", "label": "Jobs", "fieldtype": "Int", "width": 80},
            {"fieldname": "labor_hours", "label": "Labor Hours", "fieldtype": "Float", "width": 110},
            {"fieldname": "revenue", "label": "Revenue", "fieldtype": "Currency", "width": 120}]
    return cols, rows
