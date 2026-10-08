"""Logo/favicon on the login page, navbar and browser tab. Replace public/images/logo.png with a higher-resolution
file (square, ideally 512px+) and run `bench migrate` to update."""
import frappe

LOGO = "/assets/garage_management/images/logo.png"
FAVICON = "/assets/garage_management/images/favicon.png"


def apply():
    frappe.db.set_single_value("Navbar Settings", "app_logo", LOGO)
    frappe.db.set_single_value("Website Settings", "app_logo", LOGO)
    frappe.db.set_single_value("Website Settings", "favicon", FAVICON)
    frappe.db.set_single_value("Website Settings", "app_name", "Candle Auto Repair")
