"""Remove ERPNext / Frappe branding from the visible application and set the app name/logo. Idempotent."""
import frappe

from garage_management.api.whitelabel import APP_LOGO, APP_NAME


def apply():
    if not frappe.is_setup_complete():
        return  # System Settings needs language/time zone from the Setup Wizard; the next migrate applies this
    ss = frappe.get_single("System Settings")
    for field in ("disable_system_update_notification", "disable_change_log_notification", "disable_standard_email_footer"):
        ss.set(field, 1)
    ss.app_name = APP_NAME
    ss.otp_issuer_name = APP_NAME
    ss.save(ignore_permissions=True)
    for field in ("disable_system_update_notification", "disable_change_log_notification", "disable_standard_email_footer"):
        frappe.db.set_default(field, 1)  # read from the system defaults by the email/notification code
    ws = frappe.get_single("Website Settings")
    for field, val in (("footer_powered", ""), ("hide_footer_signup", 1), ("disable_signup", 1), ("call_to_action", ""),
                       ("call_to_action_url", ""), ("app_name", APP_NAME), ("app_logo", APP_LOGO), ("favicon", APP_LOGO),
                       ("splash_image", APP_LOGO), ("copyright", APP_NAME), ("brand_html", APP_NAME)):
        if ws.meta.has_field(field):
            ws.set(field, val)
    ws.save(ignore_permissions=True)
    nav = frappe.get_single("Navbar Settings")
    nav.set("help_dropdown", [])
    nav.set("settings_dropdown", [r for r in nav.settings_dropdown if "demo" not in (r.item_label or "").lower()])
    nav.app_logo = APP_LOGO
    nav.save(ignore_permissions=True)
    frappe.clear_cache()
