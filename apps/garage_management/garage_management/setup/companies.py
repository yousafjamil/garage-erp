"""The two businesses that share this system: accounts, letterheads, TRN, bank details and document wording."""
import frappe

BUSINESSES = [
    dict(name="Candle Auto Repair Workshop", abbr="CARW", style="Garage", trn="104134169200003",
         arabic="ورشة كاندل لإصلاح السيارات", letterhead="Candle Auto Repair", images="candle", email="Candlearw@gmail.com",
         phone="056-900 3156", address="Musaffah M32-02, Abu Dhabi, UAE", bank=None,
         vat_text="5 % Vat will be applicable at bill as per UAE Law",
         quotation_note="Payment will be received with in 30 days after submitting the invoices."),
    dict(name="Pak Mohmand General Transport and Contracting LLC", abbr="PMGT", style="Transport", trn="105461159300003",
         arabic="باك مهمند للنقل العام والمقاولات ذ.م.م", letterhead="Pak Mohmand", images="pm", email="Pakmohmandgtc@gmail.com",
         phone="056-900 3156", address="Musaffah M32-02, Abu Dhabi, UAE",
         bank="Name: Pak Mohmand General Transport & Contracting LLC\nA/C: 14556183920001\nIBAN: AE980030014556183920001\nBank: ADCB Bank",
         vat_text="5 % Vat will be applicable at cash bill as per UAE law", quotation_note=None),
]

ACCOUNTS = {"default_receivable_account": "Trade Receivable", "default_income_account": "Sales Account",
            "default_cash_account": "Main Safe", "default_bank_account": "Banks Current Accounts"}
MODE_ACCOUNTS = {"Cash": "Main Safe", "Card": "Visa & Master Credit Cards", "Bank Transfer": "Banks Current Accounts",
                 "Cheque": "Banks Current Accounts", "Other": "Banks Current Accounts"}


def apply():
    if not frappe.defaults.get_global_default("company"):
        return  # the Setup Wizard has not run yet; the next migrate applies this
    _payment_modes()
    for b in BUSINESSES:
        _ensure_company(b)
    for b in BUSINESSES:
        _configure(b)
    frappe.db.set_single_value("Global Defaults", "disable_rounded_total", 1)
    frappe.db.set_value("Currency", "AED", "symbol", "AED")
    _service_item()


def _payment_modes():
    for old, new in (("Credit Card", "Card"), ("Wire Transfer", "Bank Transfer"), ("Bank Draft", "Other")):
        if frappe.db.exists("Mode of Payment", old) and not frappe.db.exists("Mode of Payment", new):
            frappe.rename_doc("Mode of Payment", old, new, force=True)
    for m in MODE_ACCOUNTS:
        if not frappe.db.exists("Mode of Payment", m):
            frappe.get_doc({"doctype": "Mode of Payment", "mode_of_payment": m, "type": "Cash" if m == "Cash" else "Bank"}).insert(ignore_permissions=True)


def _ensure_company(b):
    if frappe.db.exists("Company", b["name"]):
        return
    frappe.get_doc({"doctype": "Company", "company_name": b["name"], "abbr": b["abbr"], "default_currency": "AED",
                    "country": "United Arab Emirates", "create_chart_of_accounts_based_on": "Standard Template",
                    "chart_of_accounts": "U.A.E - Chart of Accounts", "tax_id": b["trn"]}).insert(ignore_permissions=True)


def _account(company, name, abbr):
    full = f"{name} - {abbr}"
    return full if frappe.db.exists("Account", {"name": full, "is_group": 0}) else None


def _configure(b):
    name, abbr = b["name"], b["abbr"]
    for field, acc in ACCOUNTS.items():
        full = _account(name, acc, abbr)
        if full:
            frappe.db.set_value("Company", name, field, full)
    for mode, acc in MODE_ACCOUNTS.items():
        full = _account(name, acc, abbr)
        if not full:
            continue
        mp = frappe.get_doc("Mode of Payment", mode)
        if not any(r.company == name for r in mp.accounts):
            mp.append("accounts", {"company": name, "default_account": full})
            mp.save(ignore_permissions=True)
    # VAT is added to invoices by code (api/documents.py); quotations carry no tax, so no template is a default
    for dt in ("Sales Taxes and Charges Template", "Purchase Taxes and Charges Template"):
        tmpl = f"UAE VAT 5% - {abbr}"
        if frappe.db.exists(dt, tmpl):
            frappe.db.set_value(dt, tmpl, "is_default", 0)
    lh = _letterhead(b)
    frappe.db.set_value("Company", name, {
        "print_style": b["style"], "arabic_name": b["arabic"], "bank_details": b["bank"], "tax_id": b["trn"], "email": b["email"],
        "phone_no": b["phone"], "default_letter_head": lh, "quotation_vat_text": b["vat_text"],
        "quotation_note": b["quotation_note"]})


def _letterhead(b):
    img = f"/assets/garage_management/images/{b['images']}"
    doc = frappe.get_doc("Letter Head", b["letterhead"]) if frappe.db.exists("Letter Head", b["letterhead"]) else \
        frappe.get_doc({"doctype": "Letter Head", "letter_head_name": b["letterhead"]})
    doc.update({"source": "HTML", "footer_source": "HTML",
                "content": f'<img src="{img}-header.jpg" style="width:100%;display:block">',
                "footer": f'<img src="{img}-footer.jpg" style="width:100%;display:block">'})
    doc.save(ignore_permissions=True)
    return doc.name


def _service_item():
    if frappe.db.exists("Item", "Service"):
        return
    if not frappe.db.exists("Item Group", "Services"):
        frappe.get_doc({"doctype": "Item Group", "item_group_name": "Services", "parent_item_group": "All Item Groups"}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype": "Item", "item_code": "Service", "item_name": "Service", "item_group": "Services", "stock_uom": "Nos",
                    "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0, "maintain_stock": 0,
                    "description": "Service"}).insert(ignore_permissions=True)
