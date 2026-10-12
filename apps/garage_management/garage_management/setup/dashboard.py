import json
import frappe

MODULE = "Garage Management"
SIDEBAR = "Garage"


def _f(*conds):
    return json.dumps([list(c) for c in conds])


def _status(s):
    return ("Repair Job", "status", "=", s)


CARDS = [
    # label, doctype, function, based_on, filters, color
    ("Today's Jobs", "Repair Job", "Count", None, [("Repair Job", "job_date", "Timespan", "today"), ("Repair Job", "status", "!=", "Cancelled")], "#2490EF"),
    ("Vehicles In Garage", "Garage Vehicle", "Count", None, [("Garage Vehicle", "status", "in", ["Under Repair", "Ready for Delivery"])], "#2490EF"),
    ("Waiting for Approval", "Repair Job", "Count", None, [_status("Waiting for Customer Approval")], "#F5A623"),
    ("Jobs In Repair", "Repair Job", "Count", None, [_status("In Repair")], "#2490EF"),
    ("Ready for Delivery", "Repair Job", "Count", None, [_status("Ready for Delivery")], "#29CD42"),
    ("Today's Invoices", "Sales Invoice", "Count", None, [("Sales Invoice", "posting_date", "Timespan", "today"), ("Sales Invoice", "docstatus", "=", 1)], "#2490EF"),
    ("Outstanding Payments", "Sales Invoice", "Sum", "outstanding_amount", [("Sales Invoice", "docstatus", "=", 1), ("Sales Invoice", "outstanding_amount", ">", 0)], "#F5A623"),
    ("Monthly Revenue", "Sales Invoice", "Sum", "net_total", [("Sales Invoice", "posting_date", "Timespan", "this month"), ("Sales Invoice", "docstatus", "=", 1)], "#29CD42"),
    ("Vehicles Serviced (Month)", "Repair Job", "Count", None, [_status("Completed"), ("Repair Job", "actual_completion", "Timespan", "this month")], "#29CD42"),
    ("Pending Quotations", "Quotation", "Count", None, [("Quotation", "approval_status", "=", "Pending"), ("Quotation", "docstatus", "<", 2)], "#F5A623"),
]

CHARTS = [
    dict(chart_name="Jobs by Status", chart_type="Group By", document_type="Repair Job", group_by_type="Count",
         group_by_based_on="status", type="Donut", filters_json=_f(("Repair Job", "status", "!=", "Cancelled"))),
    dict(chart_name="Monthly Revenue (net)", chart_type="Sum", document_type="Sales Invoice", based_on="posting_date",
         value_based_on="net_total", timeseries=1, timespan="Last Year", time_interval="Monthly", type="Bar",
         filters_json=_f(("Sales Invoice", "docstatus", "=", 1))),
    dict(chart_name="Daily Sales (30 days)", chart_type="Sum", document_type="Sales Invoice", based_on="posting_date",
         value_based_on="grand_total", timeseries=1, timespan="Last Month", time_interval="Daily", type="Line",
         filters_json=_f(("Sales Invoice", "docstatus", "=", 1))),
]

SHORTCUTS = [  # label, doctype/report, type, view
    ("New Check-In", "Vehicle Check-In", "DocType", "New"),
    ("Jobs", "Repair Job", "DocType", "List"),
    ("Cars", "Garage Vehicle", "DocType", "List"),
    ("Customers", "Customer", "DocType", "List"),
    ("Quotations", "Quotation", "DocType", "List"),
    ("Invoices", "Sales Invoice", "DocType", "List"),
    ("Payments", "Payment Entry", "DocType", "List"),
    ("Items (Parts & Services)", "Item", "DocType", "List"),
    ("Garage Settings", "Garage Settings", "DocType", ""),
]

REPORT_LINKS = ["Vehicle Reminders", "Customer 360", "Vehicle Service History", "Jobs by Status", "Technician Performance", "Parts Used",
                "Services Performed", "Low Stock Parts", "Sales Register", "Accounts Receivable", "Stock Balance",
                "Quotation Trends", "Profit and Loss Statement", "General Ledger"]


def create():
    for label, dt, fn, based_on, filters, color in CARDS:
        if frappe.db.exists("Number Card", label):
            continue
        frappe.get_doc({"doctype": "Number Card", "label": label, "name": label, "type": "Document Type",
                        "document_type": dt, "function": fn, "aggregate_function_based_on": based_on,
                        "filters_json": _f(*filters), "is_public": 1, "show_percentage_stats": 0, "module": MODULE,
                        "color": color}).insert(ignore_permissions=True)
    if not frappe.db.exists("Number Card", "Low Stock Parts"):
        frappe.get_doc({"doctype": "Number Card", "label": "Low Stock Parts", "name": "Low Stock Parts", "type": "Custom",
                        "method": "garage_management.api.dashboard.low_stock_count", "document_type": "Item", "is_public": 1,
                        "module": MODULE, "color": "#E24C4C"}).insert(ignore_permissions=True)
    for ch in CHARTS:
        if not frappe.db.exists("Dashboard Chart", ch["chart_name"]):
            frappe.get_doc(dict(ch, doctype="Dashboard Chart", is_public=1, module=MODULE)).insert(ignore_permissions=True)
    _fix_currency()
    _workspace()
    _sidebar_and_icon()


def _fix_currency():
    """Cards/charts created before the Setup Wizard pick up the pre-wizard default currency; use the company's."""
    company = frappe.defaults.get_global_default("company")
    cur = frappe.db.get_value("Company", company, "default_currency") if company else None
    if not cur:
        return
    for label, dt, fn, *_ in CARDS:
        frappe.db.set_value("Number Card", label, "currency", cur if fn == "Sum" else None)
    for ch in CHARTS:
        frappe.db.set_value("Dashboard Chart", ch["chart_name"], "currency", cur if ch["chart_type"] == "Sum" else None)


def _workspace():
    # Home page: 6 big buttons, 6 key numbers, then a small "More" row. Nothing else (charts/reports are one click away under More).
    main_tiles = ["New Check-In", "Jobs", "Customers", "Cars", "Quotations", "Invoices"]
    key_cards = ["Today's Jobs", "Vehicles In Garage", "Waiting for Approval", "Ready for Delivery", "Outstanding Payments", "Monthly Revenue"]
    more = [s[0] for s in SHORTCUTS if s[0] not in main_tiles] + [r for r in REPORT_LINKS[:3]]
    card_names = [c[0] for c in CARDS] + ["Low Stock Parts"]  # all cards stay defined; the page shows only the key ones
    blocks = [{"id": "gh0", "type": "header", "data": {"text": '<span class="h4"><b>What would you like to do?</b></span>', "col": 12}}]
    blocks += [{"id": f"sc{i}", "type": "shortcut", "data": {"shortcut_name": n, "col": 4}} for i, n in enumerate(main_tiles)]
    blocks += [{"id": "gh1", "type": "header", "data": {"text": '<span class="h4"><b>Today</b></span>', "col": 12}}]
    blocks += [{"id": f"nc{i}", "type": "number_card", "data": {"number_card_name": n, "col": 4}} for i, n in enumerate(key_cards)]
    blocks += [{"id": "gh4", "type": "header", "data": {"text": '<span class="h6 text-muted">More</span>', "col": 12}}]
    blocks += [{"id": f"mo{i}", "type": "shortcut", "data": {"shortcut_name": n, "col": 3}} for i, n in enumerate(more)]
    if frappe.db.exists("Workspace", "Garage"):
        if frappe.db.get_value("Workspace", "Garage", "content") == json.dumps(blocks):
            return
        frappe.delete_doc("Workspace", "Garage", force=True, ignore_permissions=True)  # system-managed page: rebuild
    ws = frappe.new_doc("Workspace")
    ws.update({"label": "Garage", "title": "Garage", "name": "Garage", "module": MODULE, "public": 1, "icon": "wrench",
               "content": json.dumps(blocks), "sequence_id": 1})
    for n in card_names:
        ws.append("number_cards", {"number_card_name": n, "label": n})
    for c in CHARTS:
        ws.append("charts", {"chart_name": c["chart_name"], "label": c["chart_name"]})
    for label, target, typ, view in SHORTCUTS:
        ws.append("shortcuts", {"label": label, "type": typ, "link_to": target, "doc_view": view})
    for r in REPORT_LINKS:
        if frappe.db.exists("Report", r):
            ws.append("shortcuts", {"label": r, "type": "Report", "link_to": r})
    ws.insert(ignore_permissions=True)


SIDEBAR_NAME = "Garage Management"  # same as the module name, so it replaces the auto-generated menu


def _sidebar_and_icon():
    """The left-hand menu ships as a standard file (garage_management/sidebar/garage_management/garage_management.json), like
    ERPNext's own modules - an app's own menu cannot be created from code outside developer mode. Here we only remove
    copies made by earlier versions."""
    for legacy in ("Garage", SIDEBAR_NAME):
        if frappe.db.exists("Workspace Sidebar", legacy):
            frappe.delete_doc("Workspace Sidebar", legacy, force=True, ignore_permissions=True)
    if frappe.db.exists("Sidebar", SIDEBAR_NAME) and not frappe.db.get_value("Sidebar", SIDEBAR_NAME, "standard"):
        frappe.delete_doc("Sidebar", SIDEBAR_NAME, force=True, ignore_permissions=True)
    if frappe.db.exists("Desktop Icon", "Garage"):
        frappe.delete_doc("Desktop Icon", "Garage", force=True, ignore_permissions=True)
    from frappe.modules.import_file import import_file_by_path
    import_file_by_path(frappe.get_app_path("garage_management", "garage_management", "sidebar", "garage_management",
                                            "garage_management.json"), force=True)
