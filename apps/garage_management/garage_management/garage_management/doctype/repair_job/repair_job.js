frappe.ui.form.on("Repair Job", {
	setup(frm) {
		frm.set_query("vehicle", () => ({ filters: frm.doc.customer ? { customer: frm.doc.customer } : {} }));
		frm.set_query("item_code", "services", () => ({ filters: { is_stock_item: 0, disabled: 0 } }));
		frm.set_query("item_code", "parts", () => ({ filters: { is_stock_item: 1, disabled: 0 } }));
		frm.set_query("technician", () => ({ query: "frappe.core.doctype.user.user.user_query", filters: { enabled: 1 } }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
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

const garage_row_defaults = (cdt, cdn) => {
	const row = locals[cdt][cdn];
	if (!row.item_code) return;
	frappe.db.get_value("Item", row.item_code, ["standard_rate", "item_name"]).then((r) => {
		frappe.model.set_value(cdt, cdn, "rate", r.message.standard_rate || 0);
		if (cdt === "Repair Job Service" && !row.description) frappe.model.set_value(cdt, cdn, "description", r.message.item_name);
	});
};
const garage_row_amount = (cdt, cdn) => {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", (row.qty || 0) * (row.rate || 0));
};
["Repair Job Service", "Repair Job Part"].forEach((dt) =>
	frappe.ui.form.on(dt, { item_code: garage_row_defaults, qty: garage_row_amount, rate: garage_row_amount }));
