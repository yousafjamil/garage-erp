"""Client-edit test: change Garage Settings, confirm the printed documents follow. Restores the original values after."""
import frappe


def run():
    frappe.set_user("Administrator")
    gs = frappe.get_doc("Garage Settings")
    keep = {k: gs.get(k) for k in ("quotation_title", "accent_color", "quotation_terms", "bank_details", "invoice_title", "thank_you_note")}
    gs.update({"quotation_title": "PRICE QUOTE", "accent_color": "#8b0000", "quotation_terms": "<p>CLIENT-EDITED TERMS: pay 50% upfront.</p>",
               "bank_details": "Bank: Test Bank\nIBAN: AE00 0000 0000 0000 0000 000", "invoice_title": "VAT INVOICE", "thank_you_note": "See you again soon!"})
    gs.save()
    frappe.db.commit()
    q = frappe.get_all("Quotation", pluck="name", order_by="creation desc", limit=1)[0]
    i = frappe.get_all("Sales Invoice", filters={"docstatus": 1}, pluck="name", order_by="creation desc", limit=1)[0]
    qh = frappe.get_print("Quotation", q, print_format="Garage Quotation")
    ih = frappe.get_print("Sales Invoice", i, print_format="Garage Tax Invoice")
    for label, ok in (("quotation title", "PRICE QUOTE" in qh), ("quotation terms", "CLIENT-EDITED TERMS" in qh), ("accent colour", "#8b0000" in qh),
                      ("invoice title", "VAT INVOICE" in ih), ("bank details", "IBAN: AE00" in ih), ("thank-you line", "See you again soon" in ih)):
        print(("SET OK   " if ok else "SET FAIL ") + label)
    open("/tmp/Garage_Quotation_edited.pdf", "wb").write(frappe.get_print("Quotation", q, print_format="Garage Quotation", as_pdf=True, letterhead=frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "default_letter_head")))
    open("/tmp/Garage_Invoice_edited.pdf", "wb").write(frappe.get_print("Sales Invoice", i, print_format="Garage Tax Invoice", as_pdf=True, letterhead=frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "default_letter_head")))
    gs.reload(); gs.update(keep); gs.save(); frappe.db.commit()
    print("SET restored original values")
