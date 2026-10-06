"""End-to-end garage scenario (dev site only). Run:
    ./dc exec -T backend bench --site garage.localhost execute garage_management.tests.e2e_scenario.run
Prints E2E OK / E2E FAIL lines."""
import frappe
from frappe.model.workflow import apply_workflow
from frappe.utils import nowdate, flt
from garage_management.api import repair_job as api

def run():
    frappe.set_user("Administrator")
    CO = frappe.defaults.get_global_default("company"); ABBR = frappe.db.get_value("Company", CO, "abbr")
    WH = f"Stores - {ABBR}"
    results = []
    def check(label, cond, extra=""):
        results.append(bool(cond)); print(("E2E OK   " if cond else "E2E FAIL ") + label, extra)

    def bin_qty(item): return flt(frappe.db.get_value("Bin", {"item_code": item, "warehouse": WH}, "actual_qty"))

    # --- master data ---
    for code, grp, stock, rate in (("AC Gas Refill", "Services", 0, 150), ("AC Compressor", "Spare Parts", 1, 600)):
        if not frappe.db.exists("Item", code):
            from garage_management.setup.install import _make_item
            _make_item(code, grp, bool(stock), f"UAE VAT 5% - {ABBR}", CO, ABBR)
        frappe.db.set_value("Item", code, "standard_rate", rate)
    frappe.db.commit()
    if bin_qty("AC Compressor") < 3:
        se = frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": CO,
                             "items": [{"item_code": "AC Compressor", "qty": 5, "basic_rate": 350, "t_warehouse": WH}]})
        se.insert(); se.submit()
    start_qty = bin_qty("AC Compressor")

    PLATE = "ABC-" + frappe.generate_hash(length=4).upper()
    # 1-2 customer + vehicle
    cust = frappe.get_doc({"doctype": "Customer", "customer_name": "Ahmed Ali E2E", "customer_type": "Individual",
                           "customer_group": "Individual", "territory": "All Territories"}).insert()
    veh = frappe.get_doc({"doctype": "Garage Vehicle", "plate_number": PLATE.lower(), "customer": cust.name, "make": "Toyota",
                          "model": "Corolla", "year": 2019, "fuel_type": "Petrol", "current_mileage": 80000}).insert()
    check("vehicle plate normalised + linked", veh.plate_number == PLATE and veh.customer == cust.name)

    # 3-4 check-in with mileage
    ci = frappe.get_doc({"doctype": "Vehicle Check-In", "customer": cust.name, "vehicle": veh.name, "mileage": 85000,
                         "fuel_level": "1/2", "customer_complaint": "AC is not cooling", "keys_received": 1}).insert()
    check("check-in raised vehicle mileage", frappe.db.get_value("Garage Vehicle", veh.name, "current_mileage") == 85000)

    # 5 inspection
    ins = frappe.get_doc({"doctype": "Vehicle Inspection", "customer": cust.name, "vehicle": veh.name, "check_in": ci.name,
                          "mileage": 85000, "diagnosis": "Compressor not engaging",
                          "items": [{"component": "AC", "result": "Repair Required", "notes": "No cooling"},
                                    {"component": "Brakes", "result": "Good"}]}).insert()
    check("inspection overall = worst result", ins.overall_result == "Repair Required")

    # 6-8 job
    job = frappe.get_doc({"doctype": "Repair Job", "customer": cust.name, "vehicle": veh.name, "check_in": ci.name,
                          "mileage": 85000, "customer_complaint": ci.customer_complaint, "technician": "Administrator",
                          "services": [{"item_code": "AC Gas Refill", "qty": 1, "labor_hours": 1.5}],
                          "parts": [{"item_code": "AC Compressor", "qty": 1}]}).insert()
    check("job totals 150 + 600", job.total_services == 150 and job.total_parts == 600 and job.estimated_total == 750)
    for a in ("Check In", "Start Inspection", "Inspection Done"):
        job = apply_workflow(job, a)
    check("job reached Waiting for Quotation", job.status == "Waiting for Quotation")
    check("vehicle Under Repair", frappe.db.get_value("Garage Vehicle", veh.name, "status") == "Under Repair")

    # 9 quotation
    qn = api.make_quotation(job.name); q = frappe.get_doc("Quotation", qn)
    check("quotation totals (net 750, VAT 5% = 37.5, total 787.5)",
          flt(q.net_total) == 750 and flt(q.total_taxes_and_charges) == 37.5 and flt(q.grand_total) == 787.5,
          f"net={q.net_total} tax={q.total_taxes_and_charges} grand={q.grand_total}")
    check("quotation carries vehicle + job", q.vehicle == veh.name and q.repair_job == job.name)

    # approval gate: repair must not start before approval
    job.reload(); job = apply_workflow(job, "Send for Approval")
    try:
        job.status = "In Repair"; job.save(); check("repair blocked before approval", False)
    except frappe.ValidationError:
        check("repair blocked before approval", True); job.reload()
    try:
        api.make_invoice(job.name); check("invoice blocked before approval", False)
    except frappe.ValidationError:
        check("invoice blocked before approval", True)

    # 10-11 send + approve
    q.submit()
    api.record_approval(qn, "Customer Approved", "Ahmed Ali", "Go ahead")
    q.reload(); job.reload()
    check("quotation approved fields", q.approval_status == "Customer Approved" and q.approved_by == "Ahmed Ali" and flt(q.approved_amount) == 787.5)
    check("job moved to Approved", job.status == "Approved")

    # 12-14 repair -> QC -> ready
    for a in ("Start Repair", "Send to Quality Check", "Quality Passed"):
        job = apply_workflow(job, a)
    check("job Ready for Delivery", job.status == "Ready for Delivery")
    check("vehicle Ready for Delivery", frappe.db.get_value("Garage Vehicle", veh.name, "status") == "Ready for Delivery")
    try:
        apply_workflow(job, "Deliver Vehicle"); check("delivery blocked before invoice", False)
    except frappe.ValidationError:
        check("delivery blocked before invoice", True); job.reload()

    # 15 invoice (draft) -> submit
    sn = api.make_invoice(job.name); si = frappe.get_doc("Sales Invoice", sn)
    check("invoice has vehicle/job, update_stock", si.vehicle == veh.name and si.repair_job == job.name and si.update_stock == 1)
    check("invoice total 787.5 incl VAT", flt(si.grand_total) == 787.5, f"grand={si.grand_total}")
    si.submit(); si.reload()
    check("stock reduced by 1", bin_qty("AC Compressor") == start_qty - 1, f"{start_qty} -> {bin_qty('AC Compressor')}")

    # 16 payment
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Sales Invoice", sn); pe.mode_of_payment = "Cash"; pe.reference_no = "E2E"; pe.reference_date = nowdate()
    pe.insert(); pe.submit(); si.reload()
    check("invoice paid / outstanding 0", si.status == "Paid" and flt(si.outstanding_amount) == 0, si.status)

    # 17-18 deliver
    job.reload(); job = apply_workflow(job, "Deliver Vehicle")
    check("job Completed + completion date", job.status == "Completed" and job.actual_completion)
    check("vehicle Delivered", frappe.db.get_value("Garage Vehicle", veh.name, "status") == "Delivered")

    # 19-20 history
    from garage_management.garage_management.report.vehicle_service_history.vehicle_service_history import execute
    cols, rows = execute({"vehicle": veh.name})
    check("service history row", len(rows) == 1 and rows[0]["repair_job"] == job.name and flt(rows[0]["grand_total"]) == 787.5, str(rows[:1]))
    frappe.db.commit()
    print("E2E SUMMARY", sum(results), "/", len(results), "passed; vehicle", veh.name, "job", job.name)

