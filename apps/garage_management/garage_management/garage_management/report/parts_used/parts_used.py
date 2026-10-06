import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    cond, vals = ["rj.status != 'Cancelled'"], {}
    if filters.get("from_date"):
        cond.append("rj.job_date >= %(from_date)s"); vals["from_date"] = filters.from_date
    if filters.get("to_date"):
        cond.append("rj.job_date <= %(to_date)s"); vals["to_date"] = filters.to_date
    rows = frappe.db.sql(f"""
        SELECT p.item_code, p.item_name, SUM(p.qty) AS qty, COUNT(DISTINCT rj.name) AS jobs, SUM(p.amount) AS amount
        FROM `tabRepair Job Part` p JOIN `tabRepair Job` rj ON rj.name = p.parent
        WHERE {' AND '.join(cond)} GROUP BY p.item_code, p.item_name ORDER BY qty DESC""", vals, as_dict=True)
    cols = [{"fieldname": "item_code", "label": "Part", "fieldtype": "Link", "options": "Item", "width": 160},
            {"fieldname": "item_name", "label": "Name", "fieldtype": "Data", "width": 200},
            {"fieldname": "qty", "label": "Qty Used", "fieldtype": "Float", "width": 100},
            {"fieldname": "jobs", "label": "Jobs", "fieldtype": "Int", "width": 80},
            {"fieldname": "amount", "label": "Value", "fieldtype": "Currency", "width": 120}]
    return cols, rows
