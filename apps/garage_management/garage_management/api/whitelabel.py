import frappe

OUR_APP = "garage_management"
APP_NAME = "Candle Auto Repair & Pak Mohmand"
APP_LOGO = "/assets/garage_management/images/logo.png"
SHELL = "Garage Management"
SIMPLE_DOCTYPES = ["Quotation", "Sales Invoice", "Payment Entry", "Customer", "Service Job Card", "Customer Statement"]


def _only_garage(apps):
    return [a for a in (apps or []) if a.get("name") == OUR_APP]


def extend_bootinfo(bootinfo):
    """Show only the garage app in the app switcher, and give the ERPNext/Frappe modules the garage's name and logo."""
    data = bootinfo.get("apps_data")
    if data:
        data["apps"] = _only_garage(data.get("apps"))
        data["is_desk_apps"] = 1
    name, logo = APP_NAME, APP_LOGO
    for app in bootinfo.get("app_data") or []:
        if app.get("app_name") != OUR_APP:
            app["app_title"] = name
            app["app_logo_url"] = logo
            app["on_apps_screen"] = False  # not a separate tile on the launcher
            app["dock"] = []  # no module icons on the left: the simple menu is the only one
    # the documents we use open inside the simple menu (not the ERPNext "Selling" / "Accounts" menus)
    shells = bootinfo.get("canonical_shell")
    if shells is not None:
        shells.setdefault("DocType", {}).update({d: SHELL for d in SIMPLE_DOCTYPES})
        bootinfo["home_shell"] = SHELL
    bootinfo["dock"] = {}


@frappe.whitelist()
def get_apps():
    import frappe.apps
    return _only_garage(frappe.apps.get_apps())
