import re
import frappe
from urllib.parse import quote


def _phone(number):
    digits = re.sub(r"\D", "", number or "")
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):  # UAE local format 05x... -> 9715x...
        digits = "971" + digits[1:]
    return digits


@frappe.whitelist()
def whatsapp_link(doctype, name, kind="ready"):
    """Build a click-to-chat WhatsApp link (opens the sender's WhatsApp with the message pre-typed)."""
    doc = frappe.get_doc(doctype, name)
    doc.check_permission("read")
    customer = doc.get("customer") or doc.get("party_name")
    cust = frappe.db.get_value("Customer", customer, ["customer_name", "mobile_no"], as_dict=True) or {}
    phone = _phone(cust.get("mobile_no"))
    if not phone:
        frappe.throw(f"No mobile number saved for {cust.get('customer_name') or customer}. Add it on the customer first.")
    gs = frappe.get_cached_doc("Garage Settings")
    from garage_management.garage_management.doctype.garage_settings.garage_settings import NEW_DEFAULTS
    key = "whatsapp_quote_message" if kind == "quotation" else "whatsapp_ready_message"
    template = gs.get(key) or NEW_DEFAULTS[key]
    vehicle = doc.get("vehicle")
    veh = frappe.db.get_value("Garage Vehicle", vehicle, ["make", "model", "plate_number"], as_dict=True) if vehicle else {}
    total = doc.get("grand_total") or doc.get("estimated_total") or 0
    text = template.format_map(frappe._dict(
        customer=cust.get("customer_name") or customer, vehicle=f"{veh.get('make', '')} {veh.get('model', '')}".strip(),
        plate=veh.get("plate_number", ""), garage=gs.garage_name or "", name=doc.name,
        total=frappe.utils.fmt_money(total, currency=doc.get("currency"))))
    return f"https://wa.me/{phone}?text={quote(text)}"
