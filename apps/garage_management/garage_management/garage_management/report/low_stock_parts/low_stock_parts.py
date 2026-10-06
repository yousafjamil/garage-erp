import frappe


LOW_STOCK_SQL = """
    SELECT i.name AS item_code, i.item_name, b.warehouse, b.actual_qty,
           COALESCE(NULLIF(ir.warehouse_reorder_level, 0), NULLIF(i.safety_stock, 0)) AS min_level
    FROM `tabItem` i
    JOIN `tabBin` b ON b.item_code = i.name
    LEFT JOIN `tabItem Reorder` ir ON ir.parent = i.name AND ir.warehouse = b.warehouse
    WHERE i.is_stock_item = 1 AND i.disabled = 0
      AND b.actual_qty <= COALESCE(NULLIF(ir.warehouse_reorder_level, 0), NULLIF(i.safety_stock, 0), -1)
    ORDER BY b.actual_qty ASC"""


def execute(filters=None):
    rows = frappe.db.sql(LOW_STOCK_SQL, as_dict=True)
    cols = [{"fieldname": "item_code", "label": "Part", "fieldtype": "Link", "options": "Item", "width": 160},
            {"fieldname": "item_name", "label": "Name", "fieldtype": "Data", "width": 200},
            {"fieldname": "warehouse", "label": "Warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
            {"fieldname": "actual_qty", "label": "In Stock", "fieldtype": "Float", "width": 100},
            {"fieldname": "min_level", "label": "Minimum Level", "fieldtype": "Float", "width": 120}]
    return cols, rows
