frappe.ui.form.on("Service Job Card", {
	setup(frm) {
		if (frm.is_new() && !frm.doc.company) frm.set_value("company", frappe.defaults.get_user_default("Company"));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		const api = "garage_management.api.documents.";
		const go = (dt, name) => frappe.set_route("Form", dt, name);
		if (!frm.doc.quotation) {
			frm.add_custom_button(__("Create Quotation"), () => frappe.call({ method: api + "make_quotation", args: { job: frm.doc.name }, freeze: true })
				.then((r) => go("Quotation", r.message)), __("Create"));
		}
		if (!frm.doc.sales_invoice) {
			frm.add_custom_button(__("Create Invoice"), () => frappe.call({ method: api + "make_invoice", args: { job: frm.doc.name }, freeze: true })
				.then((r) => go("Sales Invoice", r.message)), __("Create"));
		}
		if (frm.doc.status === "Open") {
			frm.page.set_primary_action(__("Mark Completed"), () => { frm.set_value("status", "Completed"); frm.save(); });
		}
	},
});

const garage_job_amount = (frm, cdt, cdn) => {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", (row.qty || 0) * (row.rate || 0));
	frm.set_value("total", (frm.doc.lines || []).reduce((s, r) => s + (r.amount || 0), 0));
};
frappe.ui.form.on("Service Job Card Item", { qty: garage_job_amount, rate: garage_job_amount });
