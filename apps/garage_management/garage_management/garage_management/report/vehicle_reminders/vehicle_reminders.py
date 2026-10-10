import frappe

from garage_management.api.reminders import due_rows


def execute(filters=None):
    filters = frappe._dict(filters or {})
    rows = due_rows(days=filters.get("days") or 30)
    columns = [
        {"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "days_left", "label": "Days Left", "fieldtype": "Int", "width": 90},
        {"fieldname": "reason", "label": "What", "fieldtype": "Data", "width": 170},
        {"fieldname": "plate_number", "label": "Plate", "fieldtype": "Data", "width": 100},
        {"fieldname": "vehicle", "label": "Vehicle", "fieldtype": "Link", "options": "Garage Vehicle", "width": 110},
        {"fieldname": "car", "label": "Car", "fieldtype": "Data", "width": 150},
        {"fieldname": "customer_name", "label": "Owner", "fieldtype": "Data", "width": 160},
        {"fieldname": "phone", "label": "Phone", "fieldtype": "Data", "width": 120},
        {"fieldname": "next_mileage", "label": "Next Service (km)", "fieldtype": "Int", "width": 130},
    ]
    return columns, rows
