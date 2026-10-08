import frappe
from frappe.model.document import Document

DEFAULT_HEADER = "/assets/garage_management/images/letterhead-header.jpg"
DEFAULT_FOOTER = "/assets/garage_management/images/letterhead-footer.jpg"
DEFAULT_LOGO = "/assets/garage_management/images/logo.png"


class GarageSettings(Document):
    def on_update(self):
        sync_branding(self)


def _img(src, extra=""):
    return f'<img src="{src}" style="width:100%;display:block;{extra}">'


def sync_branding(gs):
    """Push the client's settings into ERPNext's own branding/letterhead records (idempotent)."""
    # letterhead
    if gs.letterhead_mode == "Text" or not (gs.header_image or DEFAULT_HEADER):
        header = (f'<div style="text-align:center;padding:10mm 12mm 3mm"><div style="font-size:22px;font-weight:bold;'
                  f'color:{gs.accent_color or "#000"}">{frappe.utils.escape_html(gs.garage_name or "")}</div>'
                  f'<div style="font-size:18px;direction:rtl">{frappe.utils.escape_html(gs.garage_name_ar or "")}</div>'
                  f'<div style="font-size:11px;color:#555">{frappe.utils.escape_html(gs.tagline or "")}</div></div>')
        contact = " &nbsp;|&nbsp; ".join(frappe.utils.escape_html(x) for x in
                                         [gs.contact_email, " ".join((gs.contact_phones or "").split()), gs.contact_address] if x)
        footer = f'<div style="text-align:center;font-size:11px;padding:4mm 12mm;border-top:2px solid {gs.accent_color or "#000"}">{contact}</div>'
    else:
        header = _img(gs.header_image or DEFAULT_HEADER)
        footer = _img(gs.footer_image or DEFAULT_FOOTER)
    company = frappe.defaults.get_global_default("company")
    name = (frappe.db.get_value("Company", company, "default_letter_head") if company else None) or "Garage Letterhead"
    lh = frappe.get_doc("Letter Head", name) if frappe.db.exists("Letter Head", name) else frappe.get_doc(
        {"doctype": "Letter Head", "letter_head_name": name})
    lh.update({"source": "HTML", "content": header, "footer_source": "HTML", "footer": footer, "is_default": 1})
    lh.save(ignore_permissions=True)
    if company and not frappe.db.get_value("Company", company, "default_letter_head"):
        frappe.db.set_value("Company", company, "default_letter_head", name)
    # names / logo shown in the application
    logo = gs.logo or DEFAULT_LOGO
    frappe.db.set_single_value("System Settings", "app_name", gs.garage_name)
    frappe.db.set_single_value("System Settings", "otp_issuer_name", gs.garage_name)
    for field, val in (("app_name", gs.garage_name), ("app_logo", logo), ("favicon", logo), ("splash_image", logo),
                       ("copyright", gs.garage_name), ("brand_html", frappe.utils.escape_html(gs.garage_name or ""))):
        frappe.db.set_single_value("Website Settings", field, val)
    frappe.db.set_single_value("Navbar Settings", "app_logo", logo)
    frappe.clear_cache()


def ensure_defaults():
    """First run only: fill the contact/letterhead fields from the garage's details."""
    gs = frappe.get_single("Garage Settings")
    if gs.initialized:
        return
    gs.update({"header_image": DEFAULT_HEADER, "footer_image": DEFAULT_FOOTER, "logo": DEFAULT_LOGO,
               "contact_phones": "056-900 3156\n050-495 6602\n050-806 2151", "contact_email": "Candlearw@gmail.com",
               "contact_address": "Musaffah M32-02, Abu Dhabi, UAE", "tagline": "Auto repair & maintenance",
               "quotation_terms": "<ul><li>Prices are in AED and exclude VAT unless stated.</li><li>Quotation valid for the number of days shown.</li><li>Work starts after the customer's approval.</li></ul>",
               "initialized": 1})
    gs.save(ignore_permissions=True)
