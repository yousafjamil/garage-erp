"""Remove ERPNext / Frappe branding from the visible application. Idempotent. Names/logo come from Garage Settings."""
import frappe

HIDE_WORKSPACES = ["ERPNext Settings", "Build", "Integrations"]


def apply():
    # no update / change-log notices, no vendor footer in emails, no vendor links in the Help menu
    ss = frappe.get_single("System Settings")  # saved as a document so the system defaults refresh too
    for field in ("disable_system_update_notification", "disable_change_log_notification", "disable_standard_email_footer"):
        ss.set(field, 1)
    ss.save(ignore_permissions=True)
    for field in ("disable_system_update_notification", "disable_change_log_notification", "disable_standard_email_footer"):
        frappe.db.set_default(field, 1)  # read from system defaults by the email/notification code
    ws = frappe.get_single("Website Settings")
    for field, val in (("footer_powered", ""), ("hide_footer_signup", 1), ("disable_signup", 1), ("call_to_action", ""),
                       ("call_to_action_url", "")):
        if ws.meta.has_field(field):
            ws.set(field, val)
    ws.save(ignore_permissions=True)
    nav = frappe.get_single("Navbar Settings")
    nav.set("help_dropdown", [])
    nav.set("settings_dropdown", [r for r in nav.settings_dropdown if "demo" not in (r.item_label or "").lower()])
    nav.save(ignore_permissions=True)
    for name in HIDE_WORKSPACES:
        if frappe.db.exists("Workspace", name):
            frappe.db.set_value("Workspace", name, "is_hidden", 1)
    # apply the client's identity from Garage Settings
    from garage_management.garage_management.doctype.garage_settings.garage_settings import ensure_defaults, sync_branding
    ensure_defaults()
    sync_branding(frappe.get_single("Garage Settings"))
