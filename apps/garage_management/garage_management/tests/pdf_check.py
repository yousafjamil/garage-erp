"""Render sample PDFs for every garage print format and email a quotation via the dev mail catcher."""
import frappe


def run():
    frappe.set_user("Administrator")
    out = {}
    job = frappe.get_all("Repair Job", filters={"status": "Completed"}, pluck="name", order_by="creation desc", limit=1)[0]
    j = frappe.get_doc("Repair Job", job)
    docs = [("Repair Job", job, "Garage Job Card"), ("Quotation", j.quotation, "Garage Quotation"),
            ("Sales Invoice", j.sales_invoice, "Garage Tax Invoice"),
            ("Vehicle Check-In", j.check_in, "Garage Vehicle Check-In"),
            ("Vehicle Inspection", j.inspection, "Garage Vehicle Inspection"),
            ("Payment Entry", frappe.get_all("Payment Entry Reference", filters={"reference_name": j.sales_invoice}, pluck="parent")[0], "Garage Payment Receipt")]
    for dt, name, pf in docs:
        if not name:
            print("PDF SKIP", dt); continue
        pdf = frappe.get_print(dt, name, print_format=pf, as_pdf=True, letterhead="Candle Auto Repair")
        path = f"/tmp/{pf.replace(' ', '_')}.pdf"
        open(path, "wb").write(pdf); print("PDF OK", pf, len(pdf), "bytes", path)
    # email the quotation (PDF attached) to the dev mail catcher
    from frappe.core.doctype.communication.email import make
    r = make(doctype="Quotation", name=j.quotation, subject=f"Quotation {j.quotation} - Candle Auto Repair Workshop",
             content="Dear customer, please find your quotation attached.", recipients="ahmed@example.com",
             send_email=True, print_format="Garage Quotation", attachments=[], print_letterhead=True)
    frappe.db.commit(); print("MAIL queued", r.get("name"))
    from frappe.email.queue import flush
    flush(); print("MAIL flushed")
