"""Home page (workspace) and numbers. The left menu ships as a standard file (sidebar/garage_management/garage_management.json)."""
import json
import frappe

MODULE = "Garage Management"
SIDEBAR_NAME = "Garage Management"


def _f(*conds):
    return json.dumps([list(c) for c in conds])


# label, doctype, function, based_on, filters, color
CARDS = [
    ("Open Job Cards", "Service Job Card", "Count", None, [("Service Job Card", "status", "=", "Open")], "#2490EF"),
    ("Quotations This Month", "Quotation", "Count", None, [("Quotation", "transaction_date", "Timespan", "this month"), ("Quotation", "docstatus", "<", 2)], "#2490EF"),
    ("Invoiced This Month", "Sales Invoice", "Sum", "grand_total", [("Sales Invoice", "posting_date", "Timespan", "this month"), ("Sales Invoice", "docstatus", "=", 1)], "#29CD42"),
    ("Unpaid Invoices", "Sales Invoice", "Sum", "outstanding_amount", [("Sales Invoice", "docstatus", "=", 1), ("Sales Invoice", "outstanding_amount", ">", 0)], "#F5A623"),
]
SHORTCUTS = [  # label, doctype, view
    ("New Job Card", "Service Job Card", "New"), ("New Quotation", "Quotation", "New"), ("New Invoice", "Sales Invoice", "New"),
    ("New Statement", "Customer Statement", "New"), ("Customers", "Customer", "List"), ("Payments Received", "Payment Entry", "List"),
]


def create():
    for label, dt, fn, based_on, filters, color in CARDS:
        doc = frappe.get_doc("Number Card", label) if frappe.db.exists("Number Card", label) else frappe.new_doc("Number Card")
        doc.update({"label": label, "name": label, "type": "Document Type", "document_type": dt, "function": fn,
                    "aggregate_function_based_on": based_on, "filters_json": _f(*filters), "is_public": 1, "show_percentage_stats": 0,
                    "module": MODULE, "color": color})
        doc.save(ignore_permissions=True)
    _fix_currency()
    _workspace()
    _sidebar()


def _fix_currency():
    cur = frappe.db.get_single_value("Global Defaults", "default_currency") or "AED"
    for label, dt, fn, *_ in CARDS:
        frappe.db.set_value("Number Card", label, "currency", cur if fn == "Sum" else None)


def _workspace():
    blocks = [{"id": "h1", "type": "header", "data": {"text": '<span class="h4"><b>What would you like to do?</b></span>', "col": 12}}]
    blocks += [{"id": f"sc{i}", "type": "shortcut", "data": {"shortcut_name": s[0], "col": 4}} for i, s in enumerate(SHORTCUTS)]
    blocks += [{"id": "h2", "type": "header", "data": {"text": '<span class="h4"><b>Today</b></span>', "col": 12}}]
    blocks += [{"id": f"nc{i}", "type": "number_card", "data": {"number_card_name": c[0], "col": 3}} for i, c in enumerate(CARDS)]
    content = json.dumps(blocks)
    if frappe.db.exists("Workspace", "Garage"):
        if frappe.db.get_value("Workspace", "Garage", "content") == content:
            return
        frappe.delete_doc("Workspace", "Garage", force=True, ignore_permissions=True)  # system-managed page: rebuild
    ws = frappe.new_doc("Workspace")
    ws.update({"label": "Garage", "title": "Home", "name": "Garage", "module": MODULE, "public": 1, "icon": "wrench",
               "content": content, "sequence_id": 1})
    for c in CARDS:
        ws.append("number_cards", {"number_card_name": c[0], "label": c[0]})
    for label, target, view in SHORTCUTS:
        ws.append("shortcuts", {"label": label, "type": "DocType", "link_to": target, "doc_view": view})
    ws.insert(ignore_permissions=True)


def _sidebar():
    """An app's own menu cannot be created from code outside developer mode, so it ships as a file: remove stale copies and import it."""
    from frappe.modules.import_file import import_file_by_path
    for legacy in ("Garage", SIDEBAR_NAME):
        if frappe.db.exists("Workspace Sidebar", legacy):
            frappe.delete_doc("Workspace Sidebar", legacy, force=True, ignore_permissions=True)
    if frappe.db.exists("Sidebar", SIDEBAR_NAME) and not frappe.db.get_value("Sidebar", SIDEBAR_NAME, "standard"):
        frappe.delete_doc("Sidebar", SIDEBAR_NAME, force=True, ignore_permissions=True)
    if frappe.db.exists("Desktop Icon", "Garage"):
        frappe.delete_doc("Desktop Icon", "Garage", force=True, ignore_permissions=True)
    import_file_by_path(frappe.get_app_path("garage_management", "garage_management", "sidebar", "garage_management",
                                            "garage_management.json"), force=True)
