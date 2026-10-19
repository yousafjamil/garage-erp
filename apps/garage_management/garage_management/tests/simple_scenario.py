"""The two businesses, end to end, using the figures from the sample documents. Run:
   ./dc exec -T backend bench --site garage.localhost execute garage_management.tests.simple_scenario.run
Creates real test documents (dev/rehearsal sites only). Prints SIMPLE OK / SIMPLE FAIL lines and writes PDFs to /tmp."""
import frappe
from frappe.utils import flt

GARAGE = "Candle Auto Repair Workshop"
TRANSPORT = "Pak Mohmand General Transport and Contracting LLC"
CUSTOMER = "Emirates LandScape Sole Proprietorship LLC"  # a unique suffix is added per run so the test can be repeated


def check(label, ok, extra=""):
    print(("SIMPLE OK   " if ok else "SIMPLE FAIL ") + label, extra)


def _customer():
    c = frappe.get_doc({"doctype": "Customer", "customer_name": CUSTOMER + " " + frappe.generate_hash(length=4).upper(), "customer_type": "Company", "tax_id": "100041562800003",
                        "doc_address": "Abu Dhabi UAE", "garage_phone": "0501112222", "garage_email": "accounts@emirateslandscape.example.com"}).insert()
    return c.name


def _doc(doctype, company, customer, lines, vehicle_no=None, date=None, note=None, lpo=None):
    d = frappe.new_doc(doctype)
    d.company = company
    d.customer = customer
    if doctype == "Quotation":
        d.quotation_to = "Customer"; d.party_name = customer; d.order_type = "Sales"
        if date: d.transaction_date = date
    elif date:
        d.set_posting_time = 1; d.posting_date = date
    d.vehicle_no = vehicle_no
    d.doc_note = note
    if lpo:
        d.lpo_ref = lpo
    for desc, rate in lines:
        d.append("items", {"description": desc, "qty": 1, "rate": rate})
    d.insert()
    return d


def run():
    frappe.set_user("Administrator")
    cust = _customer()
    pdf = lambda dt, name, fmt, path: open(path, "wb").write(frappe.get_print(dt, name, print_format=fmt, as_pdf=True))

    # ---- garage invoice (sample ELS0011/26: 150 + 220 + 180 = 550, VAT 27.50, total 577.50)
    gi = _doc("Sales Invoice", GARAGE, cust, [("Mechanical Work ( Labor Charges )", 150), ("Fixing Radiator and Cleaning", 220), ("Change Plugs", 180)],
              vehicle_no="76191 - Pickup", date="2026-08-25")
    check("garage invoice net 550, VAT 27.50, total 577.50", flt(gi.net_total) == 550 and flt(gi.total_taxes_and_charges) == 27.5 and flt(gi.grand_total) == 577.5,
          f"{gi.net_total}/{gi.total_taxes_and_charges}/{gi.grand_total}")
    check("garage invoice number uses the garage series", gi.name.startswith("INV-"), gi.name)
    check("free-text lines kept their own description", gi.items[1].description.startswith("Fixing Radiator"), gi.items[1].description[:40])
    gi.submit()
    pdf("Sales Invoice", gi.name, "Tax Invoice Print", "/tmp/s_garage_invoice.pdf")

    # ---- transport invoice (sample EL0002/2026: 780, VAT 39, 819) with bank details and LPO ref
    ti = _doc("Sales Invoice", TRANSPORT, cust, [("Recovery Services Charges From Al Wathba To Al Khatam", 780)], date="2026-08-31", lpo="LPO-4471")
    check("transport invoice 780 + VAT 39 = 819", flt(ti.grand_total) == 819 and flt(ti.total_taxes_and_charges) == 39, str(ti.grand_total))
    check("transport invoice number uses the transport series", ti.name.startswith("PINV-"), ti.name)
    ti.submit()
    pdf("Sales Invoice", ti.name, "Tax Invoice Print", "/tmp/s_transport_invoice.pdf")

    # ---- quotations carry no VAT (the VAT wording is printed instead)
    gq = _doc("Quotation", GARAGE, cust, [("Mechanical Work ( Labor Charges )", 250), ("Change Engine Belts", 150), ("Change Bearing", 165),
                                          ("Change Engin Pully", 225), ("Recovery Charges", 150)], vehicle_no="96228-Nissan Navara Pickup", date="2026-09-02")
    check("garage quotation total 940 without VAT", flt(gq.grand_total) == 940 and not gq.taxes, f"{gq.grand_total} taxes={len(gq.taxes)}")
    pdf("Quotation", gq.name, "Quotation Print", "/tmp/s_garage_quotation.pdf")
    tq = _doc("Quotation", TRANSPORT, cust, [("Transportation Charges Of Flatbed Trailer From Musaffah To Sadiyat", 1200)], date="2026-06-11")
    check("transport quotation total 1,200", flt(tq.grand_total) == 1200 and tq.name.startswith("PQTN-"), tq.name)
    pdf("Quotation", tq.name, "Quotation Print", "/tmp/s_transport_quotation.pdf")

    # ---- job card -> quotation -> invoice for each business
    jc = frappe.get_doc({"doctype": "Service Job Card", "company": GARAGE, "customer": cust, "vehicle_no": "24658 - Pickup",
                         "staff": "Ali", "details": "Engine overheating, check radiator and hoses",
                         "lines": [{"description": "Radiator repair", "qty": 1, "rate": 400}, {"description": "Coolant", "qty": 2, "rate": 50}]}).insert()
    check("job card total 500", flt(jc.total) == 500, str(jc.total))
    from garage_management.api import documents
    qn = documents.make_quotation(jc.name); inv = documents.make_invoice(jc.name)
    jc.reload()
    check("job card created its quotation and invoice", jc.quotation == qn and jc.sales_invoice == inv and jc.status == "Invoiced", f"{qn} {inv}")
    check("invoice from job card keeps the vehicle and lines", frappe.db.get_value("Sales Invoice", inv, "vehicle_no") == "24658 - Pickup"
          and frappe.db.get_value("Sales Invoice", inv, "net_total") == 500)
    pdf("Service Job Card", jc.name, "Job Card Print", "/tmp/s_garage_jobcard.pdf")
    jt = frappe.get_doc({"doctype": "Service Job Card", "company": TRANSPORT, "customer": cust, "vehicle_no": "Flatbed 4415", "staff": "Driver Khan",
                         "details": "Musaffah to Sadiyat", "lines": [{"description": "Transport charges", "qty": 1, "rate": 1200}]}).insert()
    pdf("Service Job Card", jt.name, "Job Card Print", "/tmp/s_transport_jobcard.pdf")

    # ---- monthly statement + payments applied to the oldest invoices first (statement sample: 11 invoices = 18,301.50)
    amounts = [(703.50, "27964 - Pickup", "2026-07-31"), (420, "85824 - Pickup", "2026-08-01"), (367.50, "74320 - Pickup", "2026-08-03"),
               (8557.50, "76191 - Pickup", "2026-08-08"), (1144.50, "96228 - Pickup", "2026-08-08"), (1050, "Club Car", "2026-08-08"),
               (1050, "99785 - Pickup", "2026-08-11"), (399, "85824 - Pickup", "2026-08-18"), (1218, "85863 - Pickup", "2026-08-19"),
               (2814, "24658 - Pickup", "2026-08-20")]
    made = []
    for grand, veh, date in amounts:
        d = _doc("Sales Invoice", GARAGE, cust, [("Garage work", round(grand / 1.05, 2))], vehicle_no=veh, date=date)
        d.submit(); made.append(d)
    st = frappe.get_doc({"doctype": "Customer Statement", "company": GARAGE, "customer": cust, "from_date": "2026-07-01", "to_date": "2026-08-31"}).insert()
    n = len(st.lines)
    expected = sum(a[0] for a in amounts) + 577.5  # = 18,301.50, the total on the sample statement
    check("statement = the 11 invoices of July-August = 18,301.50", n == 11 and abs(flt(st.total_amount) - 18301.5) < 0.005, f"{n} lines, total {st.total_amount}")
    from garage_management.api import payments
    pay = payments.receive_customer_payment(GARAGE, cust, 1000, "Bank Transfer", "TRF-1", "2026-09-05")
    first = frappe.get_all("Sales Invoice", filters={"company": GARAGE, "customer": cust, "docstatus": 1}, fields=["name", "outstanding_amount", "grand_total"],
                           order_by="posting_date asc, creation asc", limit=3)
    ok = pay["allocated"][0]["invoice"] == first[0].name and flt(first[0].outstanding_amount) == 0 and pay["allocated"][0]["paid"] == 703.5 \
        and pay["allocated"][1]["paid"] == 296.5
    check("payment of 1,000 paid invoice 1 (703.50) in full, then 296.50 on the next", ok, str(pay["allocated"])[:120])
    st.reload(); st.save()
    check("statement shows the payment and the remaining balance", abs(flt(st.total_paid) - 1000) < 0.05 and abs(flt(st.balance_due) - (expected - 1000)) < 0.05,
          f"paid {st.total_paid}, due {st.balance_due}")
    try:
        payments.receive_customer_payment(GARAGE, cust, 10 ** 7, "Cash")
        check("paying more than owed is refused", False)
    except frappe.ValidationError:
        check("paying more than owed is refused", True)
    # a payment to the transport business does not touch the garage's invoices
    pay2 = payments.receive_customer_payment(TRANSPORT, cust, 100, "Cash")
    check("payments are kept separate per business", pay2["allocated"][0]["invoice"].startswith("PINV-"), pay2["allocated"][0]["invoice"])
    pdf("Customer Statement", st.name, "Statement Print", "/tmp/s_garage_statement.pdf")
    pdf("Payment Entry", pay["payment_entry"], "Receipt Print", "/tmp/s_receipt.pdf")
    frappe.db.commit()
    print("SIMPLE PDFs written to /tmp/s_*.pdf")
