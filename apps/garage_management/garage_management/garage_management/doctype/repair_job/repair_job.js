frappe.ui.form.on("Repair Job", {
	setup(frm) {
		frm.set_query("vehicle", () => ({ filters: frm.doc.customer ? { customer: frm.doc.customer } : {} }));
		frm.set_query("item_code", "services", () => ({ filters: { is_stock_item: 0, disabled: 0 } }));
		frm.set_query("item_code", "parts", () => ({ filters: { is_stock_item: 1, disabled: 0 } }));
		frm.set_query("technician", () => ({ query: "frappe.core.doctype.user.user.user_query", filters: { enabled: 1 } }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		garage_next_step(frm);
		const api = "garage_management.api.repair_job.";
		frm.add_custom_button(__("Vehicle History"), () =>
			frappe.set_route("query-report", "Vehicle Service History", { vehicle: frm.doc.vehicle }));
		if (!frm.doc.quotation) {
			frm.add_custom_button(__("Quotation"), () =>
				frappe.call({ method: api + "make_quotation", args: { job: frm.doc.name }, freeze: true }).then((r) => {
					frappe.set_route("Form", "Quotation", r.message);
				}), __("Create"));
		}
		if (frm.doc.quotation && !frm.doc.sales_invoice) {
			frm.add_custom_button(__("Invoice"), () =>
				frappe.call({ method: api + "make_invoice", args: { job: frm.doc.name }, freeze: true }).then((r) => {
					frappe.set_route("Form", "Sales Invoice", r.message);
				}), __("Create"));
		}
		if (!frm.doc.inspection) {
			frm.add_custom_button(__("Inspection"), () =>
				frappe.new_doc("Vehicle Inspection", {
					customer: frm.doc.customer, vehicle: frm.doc.vehicle, repair_job: frm.doc.name,
					check_in: frm.doc.check_in, mileage: frm.doc.mileage,
				}), __("Create"));
		}
	},
	vehicle(frm) {
		if (!frm.doc.vehicle) return;
		frappe.db.get_value("Garage Vehicle", frm.doc.vehicle, ["customer", "current_mileage"]).then((r) => {
			if (r.message.customer) frm.set_value("customer", r.message.customer);
			if (!frm.doc.mileage) frm.set_value("mileage", r.message.current_mileage);
		});
	},
});

const garage_row_defaults = (frm, cdt, cdn) => {
	const row = locals[cdt][cdn];
	if (!row.item_code) return;
	frappe.db.get_value("Item", row.item_code, ["standard_rate", "item_name"]).then((r) => {
		frappe.model.set_value(cdt, cdn, "rate", r.message.standard_rate || 0);
		if (cdt === "Repair Job Service" && !row.description) frappe.model.set_value(cdt, cdn, "description", r.message.item_name);
	});
};
const garage_row_amount = (frm, cdt, cdn) => {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", (row.qty || 0) * (row.rate || 0));
};
["Repair Job Service", "Repair Job Part"].forEach((dt) =>
	frappe.ui.form.on(dt, { item_code: garage_row_defaults, qty: garage_row_amount, rate: garage_row_amount }));

// One clear sentence and one big button for "what do I do next?"
const GARAGE_HINTS = {
	"Draft": "Press Next to check the car in.",
	"Checked In": "Add the inspection, then press Next to start it.",
	"Inspection": "Inspect the car (Create > Inspection), then press Next.",
	"Waiting for Quotation": "Add services and parts below, then Create > Quotation, send it, and press Next.",
	"Waiting for Customer Approval": "Open the quotation and press Customer Decision > Customer Approved (or Rejected).",
	"Approved": "The customer approved. Press Next to start the repair.",
	"In Repair": "Repair the car. When done press Next to send it to quality check.",
	"Quality Check": "Check the work. If it is good press Next (manager).",
	"Ready for Delivery": "Press the big button: create the invoice, submit it, receive the payment, then deliver the car.",
	"Completed": "Delivered. The job is finished.",
	"Cancelled": "This job was cancelled.",
};
const GARAGE_SKIP = ["Cancel Job", "Needs Rework", "Revise Quotation", "Customer Approved"];

function garage_next_step(frm) {
	const hint = GARAGE_HINTS[frm.doc.status];
	if (hint) frm.dashboard.set_headline(`<b>${__(frm.doc.status)}</b> &mdash; ${__(hint)}`);
	if (frm.is_dirty()) return;
	const api = "garage_management.api.repair_job.";
	const go = (doctype, name) => frappe.set_route("Form", doctype, name);
	const big = (label, fn) => frm.page.set_primary_action(__(label), fn);
	const st = frm.doc.status;

	// quotation steps
	if (["Inspection", "Waiting for Quotation"].includes(st) && !frm.doc.quotation && (frm.doc.services || []).length + (frm.doc.parts || []).length) {
		return big("Create Quotation", () => frappe.call({ method: api + "make_quotation", args: { job: frm.doc.name }, freeze: true })
			.then((r) => go("Quotation", r.message)));
	}
	if (frm.doc.quotation && ["Waiting for Quotation", "Waiting for Customer Approval"].includes(st)) {
		return big("Open Quotation", () => go("Quotation", frm.doc.quotation));
	}
	// money steps
	if (st === "Ready for Delivery") {
		if (!frm.doc.sales_invoice) {
			return big("Create Invoice", () => frappe.call({ method: api + "make_invoice", args: { job: frm.doc.name }, freeze: true })
				.then((r) => go("Sales Invoice", r.message)));
		}
		return frappe.db.get_value("Sales Invoice", frm.doc.sales_invoice, ["docstatus", "outstanding_amount"]).then((r) => {
			const inv = r.message;
			if (inv.docstatus === 0) return big("Open Invoice (submit it)", () => go("Sales Invoice", frm.doc.sales_invoice));
			if (inv.outstanding_amount > 0) {
				return big("Receive Payment", () => window.garage_receive_payment(frm.doc.sales_invoice, inv.outstanding_amount, () => frm.reload_doc()));
			}
			garage_workflow_next(frm);
		});
	}
	garage_workflow_next(frm);
}

function garage_workflow_next(frm) {
	frappe.xcall("frappe.model.workflow.get_transitions", { doc: frm.doc }).then((ts) => {
		const t = (ts || []).find((x) => !GARAGE_SKIP.includes(x.action));
		if (!t) return;
		frm.page.set_primary_action(__("Next: {0}", [__(t.action)]), () =>
			frappe.xcall("frappe.model.workflow.apply_workflow", { doc: frm.doc, action: t.action }).then(() => frm.reload_doc()));
	});
}
